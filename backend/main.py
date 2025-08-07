from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import Optional
import os
from dotenv import load_dotenv
import joblib
from pathlib import Path

load_dotenv()

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ESP32 configuration
ESP32_IP = os.getenv('ESP32_IP', 'http://192.168.1.100')

class PlantData(BaseModel):
    name: str
    moisture_level: float

class ControlCommand(BaseModel):
    plant_id: str
    action: str  # "pump"
    value: Optional[float] = None

# In-memory storage for plant data
plants = {}

@app.get("/")
async def root():
    return {"message": "Smart Plant Monitoring System API"}

@app.get("/plants")
async def get_plants():
    return plants

@app.post("/plants/{plant_id}")
async def update_plant_data(plant_id: str, data: PlantData):
    plants[plant_id] = data.dict()
    return {"message": f"Updated data for plant {plant_id}"}

@app.post("/control")
async def control_plant(command: ControlCommand):
    try:
        if command.action == "pump":
            state = "on" if command.value else "off"
            response = requests.get(f"{ESP32_IP}/pump?state={state}")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to control pump")
        return {"message": f"Command sent: {command.action}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sensor-data/{plant_id}")
async def get_sensor_data(plant_id: str):
    try:
        # Get moisture data from ESP32
        response = requests.get(f"{ESP32_IP}/moisture")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get sensor data")
        
        data = response.json()
        return {
            "name": plant_id,
            "moisture_level": data["moisture"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/crops")
async def get_crops():
    try:
        # Load crop statistics
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        with open(os.path.join(models_dir, 'model_info.json'), 'r') as f:
            model_info = json.load(f)
        
        # Load unique crops
        with open(os.path.join(models_dir, 'unique_crops.json'), 'r') as f:
            unique_crops = json.load(f)
        
        return {
            "crops": unique_crops,
            "crop_stats": model_info['crop_stats']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def predict_water(data: dict):
    try:
        model = joblib.load('models/crop_model.joblib')
        encoders = joblib.load('models/encoders.joblib')
        
        # Transform input data using saved encoders
        transformed_data = {}
        for column, value in data.items():
            if column in encoders:
                transformed_data[column] = encoders[column].transform([value])[0]
        
        # Make prediction
        prediction = model.predict([list(transformed_data.values())])[0]
        return {"water_requirement": float(prediction)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found. Please train the model first.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 