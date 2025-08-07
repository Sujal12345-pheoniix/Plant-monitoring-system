# Smart Plant Monitoring System

A comprehensive IoT solution for plant monitoring and control, featuring:
- Machine learning-based plant classification
- Real-time sensor data monitoring
- Arduino-based hardware control
- Modern dashboard interface

## Project Structure
```
├── backend/           # Python FastAPI backend
│   ├── models/       # ML models and training code
│   ├── api/          # API endpoints
│   └── arduino/      # Arduino communication
├── frontend/         # React dashboard
└── arduino/          # Arduino code
```

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

### Arduino Setup
1. Upload the Arduino code to your device
2. Connect sensors and actuators
3. Configure the serial port in the backend

## Features
- Plant classification using machine learning
- Real-time soil moisture monitoring
- Weather data integration
- Automated watering system
- Dashboard visualization
- Mobile-responsive design 