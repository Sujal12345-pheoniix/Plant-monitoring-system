import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import os

def process_temperature(temp_range):
    low, high = map(int, temp_range.split('-'))
    return (low + high) / 2

def clean_outliers(df, column, n_std=3):
    mean = df[column].mean()
    std = df[column].std()
    df = df[np.abs(df[column] - mean) <= (n_std * std)]
    return df

def create_weather_score(weather):
    weather_scores = {
        'SUNNY': 1.0,
        'NORMAL': 0.7,
        'WINDY': 0.5,
        'RAINY': 0.2
    }
    return weather_scores.get(weather, 0.5)

def create_region_score(region):
    region_scores = {
        'DESERT': 1.0,
        'SEMI ARID': 0.75,
        'SEMI HUMID': 0.5,
        'HUMID': 0.25
    }
    return region_scores.get(region, 0.5)

def train_crop_model():
    # Get the absolute path to the CSV file
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(current_dir, 'crop.csv')
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Clean outliers from water requirement
    df = clean_outliers(df, 'WATER REQUIREMENT')
    
    # Get unique crops for the frontend
    unique_crops = df['CROP TYPE'].unique().tolist()
    
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Save unique crops to a file for frontend use
    crops_file = os.path.join(models_dir, 'unique_crops.json')
    with open(crops_file, 'w') as f:
        json.dump(unique_crops, f)
    
    # Process temperature
    df['TEMPERATURE'] = df['TEMPERATURE'].apply(process_temperature)
    
    # Create encoders
    crop_encoder = LabelEncoder()
    soil_encoder = LabelEncoder()
    region_encoder = LabelEncoder()
    weather_encoder = LabelEncoder()
    
    # Create feature matrix
    X = pd.DataFrame()
    
    # Encode categorical variables
    X['CROP'] = crop_encoder.fit_transform(df['CROP TYPE'])
    X['SOIL'] = soil_encoder.fit_transform(df['SOIL TYPE'])
    X['REGION'] = region_encoder.fit_transform(df['REGION'])
    X['WEATHER'] = weather_encoder.fit_transform(df['WEATHER CONDITION'])
    
    # Add temperature
    X['TEMPERATURE'] = df['TEMPERATURE']
    
    # Scale numerical features
    scaler = StandardScaler()
    X['TEMPERATURE'] = scaler.fit_transform(X[['TEMPERATURE']])
    
    # Target variable
    y = df['WATER REQUIREMENT']
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train Random Forest model with simpler parameters
    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate metrics
    train_score = r2_score(y_train, y_train_pred)
    test_score = r2_score(y_test, y_test_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    
    # Perform cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'feature': ['CROP', 'SOIL', 'REGION', 'WEATHER', 'TEMPERATURE'],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Save model and preprocessing objects
    model_file = os.path.join(models_dir, 'crop_model.joblib')
    encoders = {
        'crop': crop_encoder,
        'soil': soil_encoder,
        'region': region_encoder,
        'weather': weather_encoder,
        'scaler': scaler
    }
    encoders_file = os.path.join(models_dir, 'encoders.joblib')
    
    joblib.dump(model, model_file)
    joblib.dump(encoders, encoders_file)
    
    # Calculate crop statistics (after removing outliers)
    crop_stats = {}
    for crop in unique_crops:
        crop_data = df[df['CROP TYPE'] == crop]['WATER REQUIREMENT']
        crop_stats[crop] = {
            'mean': float(crop_data.mean().round(2)),
            'min': float(crop_data.min().round(2)),
            'max': float(crop_data.max().round(2)),
            'std': float(crop_data.std().round(2))
        }
    
    # Save feature information and crop stats
    info = {
        'feature_importance': feature_importance.to_dict('records'),
        'crop_stats': crop_stats
    }
    
    with open(os.path.join(models_dir, 'model_info.json'), 'w') as f:
        json.dump(info, f)
    
    return {
        'train_accuracy': train_score,
        'test_accuracy': test_score,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'cv_scores': cv_scores.tolist(),
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std(),
        'unique_crops': unique_crops,
        'feature_importance': feature_importance.to_dict('records'),
        'crop_stats': crop_stats
    } 