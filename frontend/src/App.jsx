import React, { useState, useEffect } from 'react';

function App() {
  const [mode, setMode] = useState('demo');
  const [sensors, setSensors] = useState(null);
  const [ai, setAi] = useState(null);

  // Fetch the current mode when the component mounts
  useEffect(() => {
    fetch('https://aquaponics-ai-lab.onrender.com/mode')
      .then((res) => res.json())
      .then((data) => setMode(data.mode))
      .catch((error) => console.error('Error fetching mode:', error));
  }, []);

  // Fetch sensor data and AI recommendations whenever the mode changes
  useEffect(() => {
    fetch('https://aquaponics-ai-lab.onrender.com/sensors')
      .then((res) => res.json())
      .then((data) => setSensors(data))
      .catch((error) => console.error('Error fetching sensors:', error));

    fetch('https://aquaponics-ai-lab.onrender.com/ai')
      .then((res) => res.json())
      .then((data) => setAi(data))
      .catch((error) => console.error('Error fetching AI recommendations:', error));
  }, [mode]);

  // Toggle between demo and real modes
  const toggleMode = async () => {
    const newMode = mode === 'demo' ? 'real' : 'demo';
    try {
      await fetch('https://aquaponics-ai-lab.onrender.com/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: newMode }),
      });
      setMode(newMode);
    } catch (error) {
      console.error('Error setting mode:', error);
    }
  };

  // Human-friendly sensor labels with units for display
  const formatSensorLabel = (key) => {
    const sensorLabels = {
      co2_ppm: 'CO₂ (ppm)',
      air_temp_celsius: 'Air Temp (°C)',
      humidity_percent: 'Humidity (%)',
      light_intensity_lux: 'Light Intensity (lux)',
      pH: 'pH',
      water_temp_celsius: 'Water Temp (°C)',
      water_flow_rate_lpm: 'Water Flow Rate (L/min)',
      audio_frequency_hz: 'Audio Frequency (Hz)',
      audio_decibels_db: 'Audio Level (dB)',
      light_cycle_hours: 'Light Cycle (hrs)',
      light_brightness_percent: 'Light Brightness (%)',
      light_pulse_freq_hz: 'Light Pulse Freq (Hz)',
    };
    return sensorLabels[key] || key;
  };

  // Format AI recommendation labels for readability
  const formatRecLabel = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Aquaponics AI Dashboard</h1>
      <button onClick={toggleMode} style={{ marginBottom: '10px' }}>
        Switch to {mode === 'demo' ? 'Real' : 'Demo'} Mode
      </button>
      <p><strong>Current Mode:</strong> {mode}</p>

      <h2>Sensor Data</h2>
      {sensors ? (
        <ul>
          {Object.entries(sensors).map(([key, value]) => (
            <li key={key}>
              {formatSensorLabel(key)}: {value !== null ? value.toString() : 'N/A'}
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading sensor data...</p>
      )}

      <h2>AI Recommendations</h2>
      {ai ? (
        <ul>
          {Object.entries(ai).map(([key, value]) => (
            <li key={key}>
              {formatRecLabel(key)}: {value !== null ? value.toString() : 'N/A'}
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading AI recommendations...</p>
      )}
    </div>
  );
}

export default App;
