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

  // Sensor history entries (for real mode). Each entry includes a timestamp
  // and a dictionary of sensor readings. Only populated when the History page
  // is active and mode is real.
  const [sensorHistory, setSensorHistory] = useState([]);

  // Actuator states and user inputs for controlling devices. When visiting
  // the Actuators page, the app fetches the current state of all actuators
  // and allows the user to update them. actuatorInputs holds the temporary
  // values entered by the user before sending them to the backend.
  const [actuators, setActuators] = useState(null);
  const [actuatorInputs, setActuatorInputs] = useState({});

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

  // Group sensors into categories for more structured display on the dashboard.
  // Environmental sensors measure conditions like air quality and light,
  // whereas aquatic sensors measure water quality. If additional sensors are
  // added in the backend, extend these arrays accordingly. Keys not found in
  // these arrays will still be displayed individually.
  const sensorCategories = {
    Environmental: [
      'co2_ppm',
      'air_temp_celsius',
      'humidity_percent',
      'light_intensity_lux',
      'light_cycle_hours',
      'light_brightness_percent',
      'light_pulse_freq_hz',
      'audio_frequency_hz',
      'audio_decibels_db',
    ],
    Aquatic: [
      'water_temp_celsius',
      'pH',
      'water_flow_rate_lpm',
    ],
  };

  // Define acceptable ranges for each sensor. These values represent
  // reasonable default thresholds for demo purposes. When integrating
  // physical hardware, these can be adjusted or loaded from a database.
  const sensorThresholds = {
    co2_ppm: [300, 1200],
    air_temp_celsius: [15, 30],
    humidity_percent: [40, 80],
    light_intensity_lux: [200, 800],
    pH: [6.0, 8.0],
    water_temp_celsius: [15, 30],
    water_flow_rate_lpm: [0.5, 5],
    audio_frequency_hz: [20, 20000],
    audio_decibels_db: [30, 70],
    light_cycle_hours: [6, 18],
    light_brightness_percent: [10, 90],
    light_pulse_freq_hz: [0, 1000],
  };

  // Helper: format AI recommendation keys to human‑readable form
  const formatRecLabel = (key) => {
    return key
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase());
  };

  // Compute alert messages based on sensor readings and thresholds. If a
  // sensor value falls outside of its defined range, an alert message is
  // added. This function is re-evaluated on each render to ensure that
  // alerts reflect the most recent data.
  const computeAlerts = () => {
    const messages = [];
    if (!sensors) return messages;
    Object.entries(sensors).forEach(([key, value]) => {
      if (value === null || value === undefined) return;
      const range = sensorThresholds[key];
      if (range) {
        const [min, max] = range;
        if (value < min || value > max) {
          messages.push(
            `${formatSensorLabel(key)} is out of range (optimal ${min}–${max}): ${value}`
          );
        }
      }
    });
    return messages;
  };

  // Evaluate alerts on each render. Alerts will be an array of strings
  // describing sensors that are out of their optimal range. When no
  // sensors are out of range, the array will be empty.
  const alerts = computeAlerts();

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

  // Whenever the mode or selected plant changes, refresh sensors and AI recommendations.
  // In demo mode the backend will return the optimal configuration when a plant name
  // is provided; otherwise it returns random simulated values. In real mode sensor
  // values are placeholders until physical hardware is integrated.
  useEffect(() => {
    // Build sensor URL with optional plant query param when in demo mode
    let sensorUrl = 'https://aquaponics-ai-lab.onrender.com/sensors';
    if (mode === 'demo' && selectedPlant) {
      sensorUrl += `?plant=${encodeURIComponent(selectedPlant)}`;
    }
    // Fetch sensor data
    fetch(sensorUrl)
      .then((res) => res.json())
      .then((data) => setSensors(data))
      .catch((error) => console.error('Error fetching sensors:', error));

    // Fetch AI recommendations
    fetch('https://aquaponics-ai-lab.onrender.com/ai')
      .then((res) => res.json())
      .then((data) => setAi(data))
      .catch((error) => console.error('Error fetching AI recommendations:', error));
  }, [mode, selectedPlant]);

  // Whenever the mode changes, refresh recipes, comparison data, and plant list. These
  // datasets are independent of the currently selected plant, so they don't need
  // to be re-fetched on every plant selection.
  useEffect(() => {
    // Fetch recipes (optimized configurations)
    fetch('https://aquaponics-ai-lab.onrender.com/recipes')
      .then((res) => res.json())
      .then((data) => setRecipes(data))
      .catch((error) => console.error('Error fetching recipes:', error));

    // Fetch traditional vs aquaponics comparison data
    fetch('https://aquaponics-ai-lab.onrender.com/traditional_vs_aquaponics')
      .then((res) => res.json())
      .then((data) => setComparison(data))
      .catch((error) => console.error('Error fetching comparison data:', error));

    // Refresh plant list; in real mode this may include user-added plants
    fetch('https://aquaponics-ai-lab.onrender.com/plants')
      .then((res) => res.json())
      .then((data) => {
        setPlants(data);
        // If there is no currently selected plant or the current selection is
        // no longer in the list (e.g., switching from real to demo), pick the first.
        if (!selectedPlant || !data.includes(selectedPlant)) {
          if (data && data.length > 0) setSelectedPlant(data[0]);
        }
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

  // Helper to fetch sensors and AI recommendations. Used initially and by
  // the periodic polling interval. Constructs the sensor endpoint
  // differently depending on mode and selected plant.
  const fetchSensorsAndAi = () => {
    let sensorUrl = 'https://aquaponics-ai-lab.onrender.com/sensors';
    if (mode === 'demo' && selectedPlant) {
      sensorUrl += `?plant=${encodeURIComponent(selectedPlant)}`;
    }
    fetch(sensorUrl)
      .then((res) => res.json())
      .then((data) => setSensors(data))
      .catch((error) => console.error('Error fetching sensors:', error));
    fetch('https://aquaponics-ai-lab.onrender.com/ai')
      .then((res) => res.json())
      .then((data) => setAi(data))
      .catch((error) => console.error('Error fetching AI recommendations:', error));
  };

  // Poll sensors and AI every 5 seconds when on dashboard. The interval
  // clears on component unmount or when dependencies change. This
  // complements the initial fetch done in other effects.
  useEffect(() => {
    // Only poll on dashboard
    if (activePage !== 'dashboard') return;
    const intervalId = setInterval(() => {
      fetchSensorsAndAi();
    }, 5000);
    return () => clearInterval(intervalId);
  }, [activePage, mode, selectedPlant]);

  // Fetch sensor history when on the History page in real mode. Poll
  // every 10 seconds to update the history table with new entries.
  useEffect(() => {
    if (activePage !== 'history' || mode !== 'real') return;
    const fetchHistory = () => {
      fetch('https://aquaponics-ai-lab.onrender.com/sensors/history?limit=50')
        .then((res) => res.json())
        .then((data) => setSensorHistory(data))
        .catch((error) => console.error('Error fetching sensor history:', error));
    };
    fetchHistory();
    const histInterval = setInterval(fetchHistory, 10000);
    return () => clearInterval(histInterval);
  }, [activePage, mode]);

  // Fetch actuator states when the Actuators page is entered. Also
  // initialize actuatorInputs with current states so that inputs reflect
  // existing values.
  useEffect(() => {
    if (activePage !== 'actuators') return;
    fetch('https://aquaponics-ai-lab.onrender.com/actuators')
      .then((res) => res.json())
      .then((data) => {
        setActuators(data);
        setActuatorInputs(data);
      })
      .catch((error) => console.error('Error fetching actuators:', error));
  }, [activePage]);

  // Handle changing an actuator input value. Since inputs can be string or
  // number, do not coerce type here; the value will be sent as-is.
  const handleActuatorInputChange = (device, value) => {
    setActuatorInputs((prev) => ({ ...prev, [device]: value }));
  };

  // Send updated actuator state to backend. Only allowed in real mode.
  const handleUpdateActuator = async (device) => {
    try {
      await fetch(`https://aquaponics-ai-lab.onrender.com/actuators/${encodeURIComponent(device)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: actuatorInputs[device] }),
      });
      // Refresh actuator states after update
      const res = await fetch('https://aquaponics-ai-lab.onrender.com/actuators');
      const data = await res.json();
      setActuators(data);
      setActuatorInputs(data);
    } catch (error) {
      console.error('Error updating actuator:', error);
    }
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
        </button>{' '}
        <button onClick={() => handlePageChange('history')} disabled={activePage === 'history'}>
          History
        </button>{' '}
        <button onClick={() => handlePageChange('actuators')} disabled={activePage === 'actuators'}>
          Actuators
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

          {/* Alerts when sensors are out of range */}
          {alerts.length > 0 && (
            <div style={{ marginBottom: '10px' }}>
              <h3 style={{ color: 'red' }}>Alerts</h3>
              <ul>
                {alerts.map((msg, idx) => (
                  <li key={idx} style={{ color: 'red' }}>{msg}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Sensor data */}
          <h3>Sensor Data</h3>
          {sensors ? (
            <>
              {/* Iterate through defined categories and display grouped sensors */}
              {Object.entries(sensorCategories).map(([category, keys]) => (
                <div key={category} style={{ marginBottom: '10px' }}>
                  <h4>{category} Sensors</h4>
                  <ul>
                    {keys.map((key) => (
                      <li key={key}>
                        {formatSensorLabel(key)}: {sensors[key] !== null && sensors[key] !== undefined ? sensors[key] : 'N/A'}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
              {/* Display any additional sensors not covered by the defined categories */}
              {Object.entries(sensors)
                .filter(([key]) =>
                  !sensorCategories.Environmental.includes(key) &&
                  !sensorCategories.Aquatic.includes(key)
                )
                .map(([key, value]) => (
                  <div key={key} style={{ marginBottom: '10px' }}>
                    <h4>Other Sensors</h4>
                    <ul>
                      <li>
                        {formatSensorLabel(key)}: {value !== null && value !== undefined ? value : 'N/A'}
                      </li>
                    </ul>
                  </div>
                ))}
            </>
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

      {/* Sensor history view */}
      {activePage === 'history' && (
        <div>
          <h2>Sensor History</h2>
          {mode !== 'real' ? (
            <p>History is only available in real mode.</p>
          ) : sensorHistory && sensorHistory.length > 0 ? (
            <table border="1" cellPadding="5" style={{ borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th>Timestamp (UTC)</th>
                  {Object.keys(sensorHistory[0].readings).map((key) => (
                    <th key={key}>{formatSensorLabel(key)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sensorHistory.map((entry, idx) => (
                  <tr key={idx}>
                    <td>{new Date(entry.timestamp).toLocaleString()}</td>
                    {Object.keys(sensorHistory[0].readings).map((key) => (
                      <td key={key}>{entry.readings[key] !== undefined && entry.readings[key] !== null ? entry.readings[key] : 'N/A'}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No history data available.</p>
          )}
        </div>
      )}

      {/* Actuator control view */}
      {activePage === 'actuators' && (
        <div>
          <h2>Actuator Control</h2>
          {mode !== 'real' ? (
            <p>Actuator control is only available in real mode.</p>
          ) : actuators ? (
            <div>
              {Object.entries(actuators).map(([device, state]) => (
                <div key={device} style={{ marginBottom: '10px' }}>
                  <strong>{device}</strong>{' '}
                  <input
                    type="text"
                    value={actuatorInputs[device] !== undefined ? actuatorInputs[device] : ''}
                    onChange={(e) => handleActuatorInputChange(device, e.target.value)}
                    style={{ marginRight: '5px' }}
                  />
                  <button onClick={() => handleUpdateActuator(device)}>
                    Set
                  </button>
                  <span style={{ marginLeft: '10px' }}>Current: {state !== undefined ? state.toString() : 'N/A'}</span>
                </div>
              ))}
            </div>
          ) : (
            <p>Loading actuator states...</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
