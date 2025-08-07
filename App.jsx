import  { useState, useEffect } from 'react';
import {  
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Card, 
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import axios from 'axios';

function App() {
  const [selectedPlant, setSelectedPlant] = useState('');
  const [plantData, setPlantData] = useState(null);
  const [plants, setPlants] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [cropStats, setCropStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [weather, setWeather] = useState('');
  const [soil, setSoil] = useState('');
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    // Fetch list of plants
    fetchPlants();
    // Set up periodic data refresh
    const interval = setInterval(fetchPlantData, 5000);
    return () => clearInterval(interval);
  }, [selectedPlant]);

  useEffect(() => {
    // Fetch crops and their stats when component mounts
    const fetchCropData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/crops');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCrops(data.crops || []);
        setCropStats(data.crop_stats || null);
      } catch (error) {
        console.error('Error fetching crop data:', error);
        setError('Failed to load crop data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCropData();
  }, []);

  const fetchPlants = async () => {
    try {
      const response = await axios.get('http://localhost:8000/plants');
      setPlants(Object.keys(response.data));
    } catch (error) {
      console.error('Error fetching plants:', error);
    }
  };

  const fetchPlantData = async () => {
    if (!selectedPlant) return;
    try {
      const response = await axios.get(`http://localhost:8000/sensor-data/${selectedPlant}`);
      setPlantData(response.data);
      setHistoricalData(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        ...response.data
      }].slice(-10));
    } catch (error) {
      console.error('Error fetching plant data:', error);
    }
  };

  const handleControl = async (action, value) => {
    try {
      await axios.post('http://localhost:8000/control', {
        plant_id: selectedPlant,
        action,
        value
      });
    } catch (error) {
      console.error('Error sending control command:', error);
    }
  };

  const handleCropChange = (event) => {
    setSelectedCrop(event.target.value);
  };

  const handlePrediction = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/predict', {
        crop: selectedCrop,
        weather: weather,
        soil: soil
      });
      setPrediction(response.data);
    } catch (error) {
      console.error('Error getting prediction:', error);
      setError('Failed to get prediction. Please try again.');
    }
  };

  const getRecommendation = (waterRequirement) => {
    if (waterRequirement < 3) {
      return "Low water requirement. Monitor soil moisture and water only when needed.";
    } else if (waterRequirement < 7) {
      return "Moderate water requirement. Maintain regular watering schedule.";
    } else {
      return "High water requirement. Ensure consistent and adequate watering.";
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Plant Selection */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Select Plant</InputLabel>
              <Select
                value={selectedPlant}
                onChange={(e) => setSelectedPlant(e.target.value)}
                label="Select Plant"
              >
                {plants.map((plant) => (
                  <MenuItem key={plant} value={plant}>
                    {plant}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Crop Selection */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Select Crop</InputLabel>
              <Select
                value={selectedCrop}
                onChange={handleCropChange}
                label="Select Crop"
              >
                <MenuItem value="">Select a crop...</MenuItem>
                {Array.isArray(crops) && crops.map((crop) => (
                  <MenuItem key={crop} value={crop}>
                    {crop}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Paper>
        </Grid>

        {/* Current Status Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Soil Moisture
              </Typography>
              <Typography variant="h4">
                {plantData?.moisture_level}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Temperature
              </Typography>
              <Typography variant="h4">
                {plantData?.temperature}°C
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Light Level
              </Typography>
              <Typography variant="h4">
                {plantData?.light_level}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Control Panel */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Control Panel
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => handleControl('water', 5)}
                >
                  Water Plant (5s)
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => handleControl('light', 50)}
                >
                  Set Light (50%)
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Historical Data Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Historical Data
            </Typography>
            <LineChart
              width={800}
              height={300}
              data={historicalData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="moisture_level" stroke="#8884d8" />
              <Line type="monotone" dataKey="temperature" stroke="#82ca9d" />
              <Line type="monotone" dataKey="light_level" stroke="#ffc658" />
            </LineChart>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            {selectedCrop && cropStats && cropStats[selectedCrop] && (
              <div className="crop-info">
                <h3>{selectedCrop}</h3>
                <div className="water-stats">
                  <p>
                    <strong>Average Water Requirement:</strong>{' '}
                    {cropStats[selectedCrop].mean.toFixed(2)} units
                  </p>
                  <p>
                    <strong>Minimum:</strong> {cropStats[selectedCrop].min.toFixed(2)} units
                  </p>
                  <p>
                    <strong>Maximum:</strong> {cropStats[selectedCrop].max.toFixed(2)} units
                  </p>
                </div>
              </div>
            )}
          </Paper>
        </Grid>

        {/* Model Prediction Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Water Requirement Prediction
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Weather Condition</InputLabel>
                  <Select
                    value={weather}
                    onChange={(e) => setWeather(e.target.value)}
                    label="Weather Condition"
                  >
                    <MenuItem value="sunny">Sunny</MenuItem>
                    <MenuItem value="cloudy">Cloudy</MenuItem>
                    <MenuItem value="rainy">Rainy</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Soil Type</InputLabel>
                  <Select
                    value={soil}
                    onChange={(e) => setSoil(e.target.value)}
                    label="Soil Type"
                  >
                    <MenuItem value="sandy">Sandy</MenuItem>
                    <MenuItem value="clay">Clay</MenuItem>
                    <MenuItem value="loamy">Loamy</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handlePrediction}
                  disabled={!selectedCrop || !weather || !soil}
                >
                  Predict Water Requirement
                </Button>
              </Grid>
              {prediction && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Prediction Results
                      </Typography>
                      <Typography>
                        <strong>Predicted Water Requirement:</strong> {prediction.water_requirement.toFixed(2)} units
                      </Typography>
                      <Typography>
                        <strong>Recommendation:</strong> {getRecommendation(prediction.water_requirement)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* Add some basic styling */}
      <style jsx>{`
        .crop-section {
          margin: 2rem;
          padding: 1rem;
          border-radius: 8px;
          background-color: #f5f5f5;
        }

        .crop-selector {
          margin: 1rem 0;
        }

        .crop-dropdown {
          margin-left: 1rem;
          padding: 0.5rem;
          border-radius: 4px;
          border: 1px solid #ccc;
          font-size: 1rem;
          min-width: 200px;
        }

        .crop-info {
          margin-top: 1rem;
          padding: 1rem;
          background-color: white;
          border-radius: 4px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .water-stats {
          margin-top: 0.5rem;
        }

        .water-stats p {
          margin: 0.5rem 0;
        }

        .error {
          color: red;
          padding: 1rem;
          background-color: #ffebee;
          border-radius: 4px;
          margin: 1rem 0;
        }
      `}</style>
    </Container>
  );
}

export default App; 