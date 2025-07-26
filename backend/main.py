from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import csv
import io

"""
Aquaponics AI backend with demo and real modes.

In demo mode, sensor endpoints return simulated readings and the
traditional versus aquaponics database is pre-populated with recipes for
10 of the most profitable microgreens based on typical growth times and
sizes【586515149730041†L134-L149】. Real mode acts as a placeholder for
future integration with physical sensors and storage; recipes can be
added via the POST /recipes endpoint once optimisation is complete.
"""

app = FastAPI()

# Enable CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global mode state: 'demo' or 'real'
MODE = "demo"

class ModeRequest(BaseModel):
    mode: str

class Recipe(BaseModel):
    plant: str
    optimal_config: dict
    traditional_time_days: int
    aquaponics_time_days: int
    traditional_size_cm: float
    aquaponics_size_cm: float

# ---------------------------------------------------------------------------
# Demo database of optimized runs
#
# The demo mode includes a pre-populated list of recipes for the 10 most
# profitable microgreens grown in aquaponics. Each recipe contains the plant
# name, an "optimal" configuration for the aquaponics system, and a
# comparison of traditional (soil-based) growth metrics versus aquaponics
# metrics. These values are rough estimates informed by publicly available
# reports on microgreen growth and profitability【586515149730041†L134-L149】.
#
# In demo mode the system pretends that optimisation has already been achieved
# and returns these records when the user browses the database or exports data.
# ---------------------------------------------------------------------------

demo_recipes = [
    {
        "plant": "Radish",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 22,
            "humidity_percent": 60,
            "light_intensity_lux": 500,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 1000,
            "audio_decibels_db": 60,
            "light_cycle_hours": 12,
            "light_brightness_percent": 80,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 12,
        "aquaponics_time_days": 7,
        "traditional_size_cm": 6.0,
        "aquaponics_size_cm": 8.0,
    },
    {
        "plant": "Sunflower",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 23,
            "humidity_percent": 55,
            "light_intensity_lux": 550,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.5,
            "audio_frequency_hz": 800,
            "audio_decibels_db": 55,
            "light_cycle_hours": 14,
            "light_brightness_percent": 85,
            "light_pulse_freq_hz": 1.2,
        },
        "traditional_time_days": 14,
        "aquaponics_time_days": 9,
        "traditional_size_cm": 10.0,
        "aquaponics_size_cm": 14.0,
    },
    {
        "plant": "Pea Shoots",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 21,
            "humidity_percent": 60,
            "light_intensity_lux": 450,
            "pH": 6.6,
            "water_temp_celsius": 21,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 900,
            "audio_decibels_db": 55,
            "light_cycle_hours": 12,
            "light_brightness_percent": 75,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 14,
        "aquaponics_time_days": 11,
        "traditional_size_cm": 10.0,
        "aquaponics_size_cm": 12.0,
    },
    {
        "plant": "Broccoli",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 22,
            "humidity_percent": 60,
            "light_intensity_lux": 500,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 1000,
            "audio_decibels_db": 60,
            "light_cycle_hours": 12,
            "light_brightness_percent": 80,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 11,
        "aquaponics_time_days": 8,
        "traditional_size_cm": 5.0,
        "aquaponics_size_cm": 7.0,
    },
    {
        "plant": "Cilantro",
        "optimal_config": {
            "co2_ppm": 650,
            "air_temp_celsius": 21,
            "humidity_percent": 65,
            "light_intensity_lux": 480,
            "pH": 6.4,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 1.8,
            "audio_frequency_hz": 900,
            "audio_decibels_db": 50,
            "light_cycle_hours": 12,
            "light_brightness_percent": 75,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 21,
        "aquaponics_time_days": 17,
        "traditional_size_cm": 4.0,
        "aquaponics_size_cm": 5.0,
    },
    {
        "plant": "Basil",
        "optimal_config": {
            "co2_ppm": 650,
            "air_temp_celsius": 24,
            "humidity_percent": 55,
            "light_intensity_lux": 550,
            "pH": 6.2,
            "water_temp_celsius": 23,
            "water_flow_rate_lpm": 2.2,
            "audio_frequency_hz": 1000,
            "audio_decibels_db": 60,
            "light_cycle_hours": 14,
            "light_brightness_percent": 85,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 20,
        "aquaponics_time_days": 18,
        "traditional_size_cm": 6.0,
        "aquaponics_size_cm": 7.0,
    },
    {
        "plant": "Kale",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 21,
            "humidity_percent": 60,
            "light_intensity_lux": 480,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 950,
            "audio_decibels_db": 55,
            "light_cycle_hours": 12,
            "light_brightness_percent": 75,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 14,
        "aquaponics_time_days": 10,
        "traditional_size_cm": 4.5,
        "aquaponics_size_cm": 5.5,
    },
    {
        "plant": "Mustard",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 22,
            "humidity_percent": 60,
            "light_intensity_lux": 500,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 1000,
            "audio_decibels_db": 60,
            "light_cycle_hours": 12,
            "light_brightness_percent": 80,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 14,
        "aquaponics_time_days": 12,
        "traditional_size_cm": 4.0,
        "aquaponics_size_cm": 5.0,
    },
    {
        "plant": "Arugula",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 21,
            "humidity_percent": 60,
            "light_intensity_lux": 480,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 950,
            "audio_decibels_db": 55,
            "light_cycle_hours": 12,
            "light_brightness_percent": 75,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 12,
        "aquaponics_time_days": 10,
        "traditional_size_cm": 4.0,
        "aquaponics_size_cm": 5.0,
    },
    {
        "plant": "Cabbage",
        "optimal_config": {
            "co2_ppm": 600,
            "air_temp_celsius": 22,
            "humidity_percent": 60,
            "light_intensity_lux": 500,
            "pH": 6.5,
            "water_temp_celsius": 22,
            "water_flow_rate_lpm": 2.0,
            "audio_frequency_hz": 1000,
            "audio_decibels_db": 60,
            "light_cycle_hours": 12,
            "light_brightness_percent": 80,
            "light_pulse_freq_hz": 1.0,
        },
        "traditional_time_days": 12,
        "aquaponics_time_days": 10,
        "traditional_size_cm": 5.0,
        "aquaponics_size_cm": 6.0,
    },
]

# Store recipes for real mode (empty until optimisation runs complete)
real_recipes = []

#
# In real mode, sensor readings will come from physical hardware. We store
# the most recent readings in this dictionary. A separate controller
# (e.g. Raspberry Pi or microcontroller) should POST readings to the
# /sensor/readings endpoint defined below. Each key corresponds to a sensor
# name and its value is the latest numeric reading. When no data has
# been received for a key, the sensors endpoint will return None.
latest_readings: dict[str, float] = {}

# A rolling log of sensor readings in real mode. Each entry is a dict with
# a timestamp and the readings ingested at that moment. This is used to
# provide historical data to the frontend for plotting and analysis. When
# the log grows beyond a reasonable size (e.g. 1000 entries) the oldest
# entries are dropped.
history_readings: list[dict] = []

# Track the state of actuators in real mode. Each key corresponds to
# a controllable device in the aquaponics system. Values are simple
# strings or numbers representing the device's current state. For example,
# 'co2_valve': 'on' or 'off', 'grow_lights': 75 (percent brightness).
actuator_states: dict[str, any] = {
    "co2_valve": "off",
    "grow_lights": 0,  # percent brightness 0-100
    "water_pump": "off",
    "drip_valves": "off",
    "fans": 0,  # percent speed 0-100
    "heaters": "off",
    "aerators": "off",
    "audio_transducers": 0,  # volume 0-100
    "cameras": "off",
}

# Define a simple Pydantic model for ingesting arbitrary sensor readings.
# NOTE: Instead of using a Pydantic root model (which requires Pydantic v2's RootModel),
# we accept sensor readings as a plain dictionary in the ingestion endpoint. This
# avoids type errors with the `__root__` field under newer Pydantic versions.
class SensorReadings(BaseModel):
    readings: dict[str, float]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aquaponics AI backend"}

@app.get("/mode")
def get_mode():
    return {"mode": MODE}

@app.post("/mode")
def set_mode(request: ModeRequest):
    global MODE
    if request.mode not in ["demo", "real"]:
        raise HTTPException(status_code=400, detail="Mode must be 'demo' or 'real'")
    MODE = request.mode
    return {"mode": MODE}

@app.get("/sensors")
def get_sensors(plant: str = None):
    """
    Return sensor readings.

    In demo mode, if a plant name is provided and a matching recipe exists in
    the demo database, return the optimal configuration for that plant. This
    allows the front end to display known optimal units for each selected
    microgreen rather than random simulated values. If no plant is provided
    or no recipe is found, random values are returned. In real mode, all
    sensor values are placeholders (None) until physical sensors are
    integrated.
    """
    # Define ranges for random demo simulation
    sensor_keys = {
        "co2_ppm": lambda: round(random.uniform(300, 800), 2),
        "air_temp_celsius": lambda: round(random.uniform(18, 30), 2),
        "humidity_percent": lambda: round(random.uniform(30, 70), 2),
        "light_intensity_lux": lambda: round(random.uniform(200, 1000), 2),
        "pH": lambda: round(random.uniform(6, 8), 2),
        "water_temp_celsius": lambda: round(random.uniform(18, 28), 2),
        "water_flow_rate_lpm": lambda: round(random.uniform(0.5, 5.0), 2),
        "audio_frequency_hz": lambda: round(random.uniform(200, 2000), 2),
        "audio_decibels_db": lambda: round(random.uniform(30, 90), 2),
        "light_cycle_hours": lambda: round(random.uniform(8, 18), 2),
        "light_brightness_percent": lambda: round(random.uniform(10, 100), 2),
        "light_pulse_freq_hz": lambda: round(random.uniform(0.5, 5.0), 2),
    }
    # In demo mode, return optimal config if a plant match exists
    if MODE == "demo":
        if plant:
            # Find matching recipe (case-insensitive)
            match = next((r for r in demo_recipes if r["plant"].lower() == plant.lower()), None)
            if match:
                return match["optimal_config"]
        # Otherwise return random simulated values
        return {k: gen() for k, gen in sensor_keys.items()}
    else:
        # Real mode: return the latest readings if available. Use None for sensors that
        # have not yet been reported by the hardware. The keys mirror those used
        # in the demo simulation to ensure a consistent response shape for the
        # frontend. As the system grows, additional sensors can be added to
        # `sensor_keys` without modifying this logic.
        return {k: latest_readings.get(k) for k in sensor_keys}


@app.post("/sensor/readings")
def ingest_sensor_readings(readings: dict[str, float]):
    """Ingest a batch of sensor readings from physical hardware.

    In real mode, the controller (e.g. Raspberry Pi) should POST a JSON
    object containing sensor names and their most recent values to this
    endpoint. Each reading is stored in the `latest_readings` dictionary.
    Additionally, a timestamped snapshot of the readings is appended to
    `history_readings` so that the frontend can display historical trends.

    Example payload:

    {
      "co2_ppm": 650,
      "air_temp_celsius": 23.5,
      "humidity_percent": 58
    }

    Returns the number of readings ingested. Raises a 400 error if
    called while in demo mode.
    """
    if MODE != "real":
        raise HTTPException(status_code=400, detail="Can only ingest sensor data in real mode")
    # Update the latest readings
    for key, value in readings.items():
        latest_readings[key] = value
    # Append a timestamped entry to the history log
    from datetime import datetime
    history_readings.append({
        "timestamp": datetime.utcnow().isoformat(),
        "readings": readings.copy(),
    })
    # Keep history from growing indefinitely
    if len(history_readings) > 1000:
        history_readings.pop(0)
    return {"status": "received", "count": len(readings)}

@app.get("/ai")
def get_ai_recommendations():
    """Provide AI-driven recommendations. In demo mode returns random suggestions; in real mode placeholders."""
    if MODE == "demo":
        return {
            "adjust_co2": random.choice(["increase", "decrease", "maintain"]),
            "adjust_air_temp": random.choice(["increase", "decrease", "maintain"]),
            "adjust_humidity": random.choice(["increase", "decrease", "maintain"]),
            "adjust_light_intensity": random.choice([
                "increase intensity",
                "decrease intensity",
                "change spectrum",
                "maintain",
            ]),
            "adjust_pH": random.choice(["raise pH", "lower pH", "maintain"]),
            "adjust_water_temp": random.choice(["increase", "decrease", "maintain"]),
            "adjust_water_flow_rate": random.choice(["increase", "decrease", "maintain"]),
            "adjust_audio_frequency": random.choice(["increase frequency", "decrease frequency", "maintain"]),
            "adjust_audio_decibels": random.choice(["increase volume", "decrease volume", "maintain"]),
            "adjust_light_cycle": random.choice(["extend photoperiod", "shorten photoperiod", "maintain"]),
            "adjust_light_brightness": random.choice(["increase", "decrease", "maintain"]),
            "adjust_light_pulse_freq": random.choice(["increase frequency", "decrease frequency", "maintain"]),
        }
    else:
        return {
            "adjust_co2": None,
            "adjust_air_temp": None,
            "adjust_humidity": None,
            "adjust_light_intensity": None,
            "adjust_pH": None,
            "adjust_water_temp": None,
            "adjust_water_flow_rate": None,
            "adjust_audio_frequency": None,
            "adjust_audio_decibels": None,
            "adjust_light_cycle": None,
            "adjust_light_brightness": None,
            "adjust_light_pulse_freq": None,
        }

@app.get("/plants")
def get_plants():
    """Return a list of available plants for the current mode."""
    if MODE == "demo":
        return [r["plant"] for r in demo_recipes]
    else:
        return [r["plant"] for r in real_recipes]

@app.get("/recipes")
def get_recipes():
    """Return all recipe records depending on the current mode."""
    return demo_recipes if MODE == "demo" else real_recipes

@app.post("/recipes")
def add_recipe(recipe: Recipe):
    """Add a recipe record in real mode. Raises an error if called in demo mode."""
    if MODE != "real":
        raise HTTPException(status_code=400, detail="Can only add recipes in real mode")
    real_recipes.append(recipe.dict())
    return {"status": "added", "count": len(real_recipes)}

@app.get("/recipes/export")
def export_recipes():
    """Export the current recipe database as a CSV file suitable for opening in Excel."""
    data = demo_recipes if MODE == "demo" else real_recipes
    output = io.StringIO()
    writer = csv.writer(output)
    # Write header
    writer.writerow([
        "plant",
        "traditional_time_days",
        "aquaponics_time_days",
        "traditional_size_cm",
        "aquaponics_size_cm",
    ])
    for rec in data:
        writer.writerow([
            rec["plant"],
            rec["traditional_time_days"],
            rec["aquaponics_time_days"],
            rec["traditional_size_cm"],
            rec["aquaponics_size_cm"],
        ])
    csv_content = output.getvalue()
    output.close()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=recipes.csv"},
    )

@app.get("/traditional_vs_aquaponics")
def get_traditional_vs_aquaponics():
    """Return a comparison of traditional versus aquaponics growth metrics for each plant."""
    data = demo_recipes if MODE == "demo" else real_recipes
    return [
        {
            "plant": rec["plant"],
            "traditional_time_days": rec["traditional_time_days"],
            "aquaponics_time_days": rec["aquaponics_time_days"],
            "traditional_size_cm": rec["traditional_size_cm"],
            "aquaponics_size_cm": rec["aquaponics_size_cm"],
        }
        for rec in data
    ]

# ---------------------------------------------------------------------------
# History and actuator endpoints
#
# The following endpoints provide additional functionality for the frontend.
# /sensors/history returns a limited number of recent sensor readings in real
# mode. /actuators and /actuators/{device} allow the frontend to query and
# set the state of hardware devices. Actuator control is only permitted in
# real mode to avoid accidentally toggling devices during demonstration.
# ---------------------------------------------------------------------------

@app.get("/sensors/history")
def get_sensor_history(limit: int = 100):
    """Return the most recent sensor readings.

    The `limit` query parameter specifies how many history entries to return.
    The default is 100. If called in demo mode or no history exists, an
    empty list is returned. Each entry includes a timestamp and a dictionary
    of sensor readings.
    """
    if MODE != "real" or not history_readings:
        return []
    # Clamp limit between 1 and length of history
    limit = max(1, min(limit, len(history_readings)))
    # Return the last `limit` entries
    return history_readings[-limit:]

@app.get("/actuators")
def get_all_actuators():
    """Return the current state of all actuators."""
    return actuator_states

@app.get("/actuators/{device}")
def get_actuator(device: str):
    """Return the state of a single actuator.

    Raises 404 if the device name is unknown.
    """
    if device not in actuator_states:
        raise HTTPException(status_code=404, detail="Unknown actuator")
    return {device: actuator_states[device]}

@app.post("/actuators/{device}")
def set_actuator(device: str, state: dict):
    """Update the state of a given actuator in real mode.

    The request body should be a JSON object with a single `state` key
    representing the desired new value. For example:

    {
      "state": "on"
    }

    or for actuators controlled by a percentage (0-100):

    {
      "state": 75
    }

    Returns the updated actuator state. Raises a 400 error if called in
    demo mode or if the device name is unknown.
    """
    if MODE != "real":
        raise HTTPException(status_code=400, detail="Can only control actuators in real mode")
    if device not in actuator_states:
        raise HTTPException(status_code=404, detail="Unknown actuator")
    # Only update the state if the key 'state' is provided
    if "state" not in state:
        raise HTTPException(status_code=400, detail="Request body must include a 'state' field")
    actuator_states[device] = state["state"]
    return {device: actuator_states[device]}

