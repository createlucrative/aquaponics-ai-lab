import React, { useState, useEffect } from 'react';

/*
 * This component implements a multi‑page dashboard for the Aquaponics AI project.
 * It exposes three views: a live dashboard showing sensors and AI recommendations,
 * a database view listing all optimized plant recipes, and a comparison view
 * showing how aquaponics growth metrics compare to traditional methods.
 * Users can toggle between demo and real modes, select existing plants or
 * manually enter new ones, and export the recipe database as a CSV file.
 */

function App() {
  // Global mode: 'demo' or 'real'
  const [mode, setMode] = useState('demo');
  // Which page is currently active
  const [activePage, setActivePage] = useState('dashboard');
  // List of plant names returned from the backend
  const [plants, setPlants] = useState([]);
  // Selected plant from dropdown
  const [selectedPlant, setSelectedPlant] = useState('');
  // Manually entered plant name
  const [newPlantName, setNewPlantName] = useState('');
  // Live sensor readings
  const [sensors, setSensors] = useState(null);
  // AI recommendations corresponding to sensor readings
  const [ai, setAi] = useState(null);
  // List of recipes (optimized configurations)
  const [recipes, setRecipes] = useState(null);
  // Comparison data for traditional vs aquaponics
  const [comparison, setComparison] = useState(null);

  // Helper: format sensor keys into human‑friendly labels with units
  const formatSensorLabel = (key) => {
    const labels = {
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
    return labels[key] || key;
  };

  // Helper: format AI recommendation keys to human‑readable form
  const formatRecLabel = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  // Fetch the current mode, list of plants, and initial data on mount
  useEffect(() => {
    fetch('https://aquaponics-ai-lab.onrender.com/mode')
      .then((res) => res.json())
      .then((data) => setMode(data.mode))
      .catch((err) => console.error('Error fetching mode:', err));

    fetch('https://aquaponics-ai-lab.onrender.com/plants')
      .then((res) => res.json())
      .then((data) => {
        setPlants(data);
        if (data && data.length > 0) setSelectedPlant(data[0]);
      })
      .catch((err) => console.error('Error fetching plant list:', err));
  }, []);

  // Whenever the mode changes, refresh sensors, AI, recipes and comparison data
  useEffect(() => {
    // Fetch sensor data
    fetch('https://aquaponics-ai-lab.onrender.com/sensors')
      .then((res) => res.json())
      .then((data) => setSensors(data))
      .catch((error) => console.error('Error fetching sensors:', error));

    // Fetch AI recommendations
    fetch('https://aquaponics-ai-lab.onrender.com/ai')
      .then((res) => res.json())
      .then((data) => setAi(data))
      .catch((error) => console.error('Error fetching AI recommendations:', error));

    // Fetch recipes
    fetch('https://aquaponics-ai-lab.onrender.com/recipes')
      .then((res) => res.json())
      .then((data) => setRecipes(data))
      .catch((error) => console.error('Error fetching recipes:', error));

    // Fetch traditional vs aquaponics comparison
    fetch('https://aquaponics-ai-lab.onrender.com/traditional_vs_aquaponics')
      .then((res) => res.json())
      .then((data) => setComparison(data))
      .catch((error) => console.error('Error fetching comparison data:', error));

    // Refresh plant list when mode changes to capture real recipes if any
    fetch('https://aquaponics-ai-lab.onrender.com/plants')
      .then((res) => res.json())
      .then((data) => {
        setPlants(data);
        if (data && data.length > 0) setSelectedPlant(data[0]);
      })
      .catch((err) => console.error('Error fetching plant list:', err));
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

  // Handle switching pages
  const handlePageChange = (page) => {
    setActivePage(page);
  };

  // Handle selecting a plant from the dropdown
  const handleSelectPlant = (event) => {
    setSelectedPlant(event.target.value);
  };

  // Handle manual plant input
  const handleManualInput = (event) => {
    setNewPlantName(event.target.value);
  };

  // Save manual plant entry (only in real mode). Posts empty recipe to backend
  const handleAddPlant = async () => {
    const plantName = newPlantName.trim();
    if (!plantName) return;
    try {
      await fetch('https://aquaponics-ai-lab.onrender.com/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plant: plantName, optimal_config: {}, metrics: {} }),
      });
      // refresh recipes and plants after adding
      const recipesRes = await fetch('https://aquaponics-ai-lab.onrender.com/recipes');
      setRecipes(await recipesRes.json());
      const plantsRes = await fetch('https://aquaponics-ai-lab.onrender.com/plants');
      const plData = await plantsRes.json();
      setPlants(plData);
      setSelectedPlant(plantName);
      setNewPlantName('');
    } catch (error) {
      console.error('Error adding new plant:', error);
    }
  };

  // Download recipes as CSV using backend export endpoint
  const handleDownload = () => {
    const url = 'https://aquaponics-ai-lab.onrender.com/recipes/export';
    // create temporary anchor to start download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'recipes.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Aquaponics AI Platform</h1>
      {/* Mode toggle */}
      <button onClick={toggleMode} style={{ marginBottom: '10px' }}>
        Switch to {mode === 'demo' ? 'Real' : 'Demo'} Mode
      </button>
      <p><strong>Current Mode:</strong> {mode}</p>
      {/* Navigation menu */}
      <nav style={{ marginBottom: '20px' }}>
        <button onClick={() => handlePageChange('dashboard')} disabled={activePage === 'dashboard'}>
          Dashboard
        </button>{' '}
        <button onClick={() => handlePageChange('database')} disabled={activePage === 'database'}>
          Database
        </button>{' '}
        <button onClick={() => handlePageChange('traditional')} disabled={activePage === 'traditional'}>
          Traditional vs Aquaponics
        </button>
      </nav>

      {/* Dashboard view */}
      {activePage === 'dashboard' && (
        <div>
          <h2>Dashboard</h2>
          {/* Plant selection */}
          <div style={{ marginBottom: '10px' }}>
            <label>
              Select Plant:{' '}
              <select value={selectedPlant} onChange={handleSelectPlant}>
                {plants && plants.map((plant) => (
                  <option key={plant} value={plant}>{plant}</option>
                ))}
              </select>
            </label>
            <span style={{ marginLeft: '15px' }}>
              or add new: <input value={newPlantName} onChange={handleManualInput} placeholder="Custom plant" />
              <button onClick={handleAddPlant} disabled={!newPlantName.trim() || mode === 'demo'}>
                Add Plant
              </button>
            </span>
          </div>
          {/* Sensor data */}
          <h3>Sensor Data</h3>
          {sensors ? (
            <ul>
              {Object.entries(sensors).map(([key, value]) => (
                <li key={key}>{formatSensorLabel(key)}: {value !== null ? value.toString() : 'N/A'}</li>
              ))}
            </ul>
          ) : (
            <p>Loading sensor data...</p>
          )}
          {/* AI recommendations */}
          <h3>AI Recommendations</h3>
          {ai ? (
            <ul>
              {Object.entries(ai).map(([key, value]) => (
                <li key={key}>{formatRecLabel(key)}: {value !== null ? value.toString() : 'N/A'}</li>
              ))}
            </ul>
          ) : (
            <p>Loading AI recommendations...</p>
          )}
        </div>
      )}

      {/* Database view */}
      {activePage === 'database' && (
        <div>
          <h2>Optimized Recipe Database</h2>
          {recipes ? (
            <div>
              <table border="1" cellPadding="5" style={{ borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th>Plant</th>
                    {/* Dynamically generate columns from first recipe's optimal_config keys */}
                    {recipes.length > 0 &&
                      Object.keys(recipes[0].optimal_config).map((key) => (
                        <th key={key}>{formatSensorLabel(key)}</th>
                      ))}
                    {/* Metrics columns */}
                    <th>Traditional Time (days)</th>
                    <th>Aquaponics Time (days)</th>
                    <th>Traditional Size (cm)</th>
                    <th>Aquaponics Size (cm)</th>
                  </tr>
                </thead>
                <tbody>
                  {recipes.map((r, index) => (
                    <tr key={index}>
                      <td>{r.plant}</td>
                      {Object.keys(r.optimal_config).map((key) => (
                        <td key={key}>{r.optimal_config[key]}</td>
                      ))}
                      <td>{r.traditional_time_days}</td>
                      <td>{r.aquaponics_time_days}</td>
                      <td>{r.traditional_size_cm}</td>
                      <td>{r.aquaponics_size_cm}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button onClick={handleDownload} style={{ marginTop: '10px' }}>
                Export to CSV
              </button>
            </div>
          ) : (
            <p>Loading recipes...</p>
          )}
        </div>
      )}

      {/* Traditional vs Aquaponics view */}
      {activePage === 'traditional' && (
        <div>
          <h2>Traditional vs Aquaponics Comparison</h2>
          {comparison ? (
            <table border="1" cellPadding="5" style={{ borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th>Plant</th>
                  <th>Traditional Time (days)</th>
                  <th>Aquaponics Time (days)</th>
                  <th>Traditional Size (cm)</th>
                  <th>Aquaponics Size (cm)</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((entry, index) => (
                  <tr key={index}>
                    <td>{entry.plant}</td>
                    <td>{entry.traditional_time_days}</td>
                    <td>{entry.aquaponics_time_days}</td>
                    <td>{entry.traditional_size_cm}</td>
                    <td>{entry.aquaponics_size_cm}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>Loading comparison data...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;