from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
import asyncio
import json
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

# Initialise Q-values for a simple reinforcement-learning controller.
# For each sensor we track three possible actions: -1 (decrease),
# 0 (maintain) and +1 (increase). The Q-value represents the expected
# reward (negative absolute error) associated with taking that action.
q_values: dict[str, dict[int, float]] = {}

# Target configuration used for automatic optimisation in real mode. When
# optimisation is enabled, the backend will compare incoming sensor
# readings against this target and adjust actuators accordingly. The
# default target is initialised to the optimal config of the first
# demo recipe (e.g. Radish). The frontend can update this via the
# /target-config endpoint by specifying a plant name.
TARGET_CONFIG = demo_recipes[0]["optimal_config"].copy()

# Helper functions for the simple RL controller
def choose_action(sensor: str, value: float, target: float) -> int:
    """Choose an action (-1, 0, or +1) for a given sensor using a greedy policy.

    If no Q-values exist for the sensor, they are initialised to zero.
    The action with the highest Q-value is returned. In practice this
    controller favours actions that historically reduced the absolute error
    between the sensor value and the target.
    """
    if sensor not in q_values:
        q_values[sensor] = {-1: 0.0, 0: 0.0, 1: 0.0}
    # Select the action with the highest expected reward
    actions = q_values[sensor]
    best_action = max(actions, key=actions.get)
    return best_action

def update_q(sensor: str, action: int, value: float, target: float, lr: float = 0.1):
    """Update the Q-value for a given sensor and action based on observed reward.

    The reward is defined as the negative absolute error between the
    current sensor reading and the target. Q-values are updated via
    incremental gradient descent towards the observed reward.
    """
    if sensor not in q_values:
        q_values[sensor] = {-1: 0.0, 0: 0.0, 1: 0.0}
    reward = -abs(value - target)
    current_q = q_values[sensor][action]
    q_values[sensor][action] = current_q + lr * (reward - current_q)

def auto_adjust_actuators():
    """Automatically adjust actuators based on the latest sensor readings and
    target configuration.

    This simple rule‑based controller compares each sensor value against
    the corresponding target value in TARGET_CONFIG and sets actuator
    states accordingly. It is invoked whenever new sensor readings are
    ingested in real mode. If a reading or target is missing, the
    actuator is not modified. You can refine these rules to implement
    PID control or more advanced algorithms as needed.
    """
    # Only adjust in real mode
    if MODE != "real":
        return
    # Mapping of sensor keys to actuator update logic. Each value is a
    # callable that takes an action (-1 decrease, 0 maintain, 1 increase)
    # and performs the appropriate actuator adjustments. If a sensor or
    # target value is missing, the mapping is skipped.
    mappings = {
        "co2_ppm": lambda a: actuator_states.__setitem__("co2_valve", "on" if a == 1 else "off"),
        "air_temp_celsius": lambda a: (
            actuator_states.__setitem__("heaters", "on" if a == 1 else "off"),
            actuator_states.__setitem__("fans", 50 if a == -1 else 0),
        ),
        "humidity_percent": lambda a: actuator_states.__setitem__("fans", 75 if a == 1 else (25 if a == -1 else actuator_states.get("fans", 0))),
        "water_flow_rate_lpm": lambda a: actuator_states.__setitem__("water_pump", "on" if a == 1 else "off"),
        "audio_decibels_db": lambda a: actuator_states.__setitem__("audio_transducers", TARGET_CONFIG.get("audio_decibels_db", 0)),
        "light_brightness_percent": lambda a: actuator_states.__setitem__("grow_lights", TARGET_CONFIG.get("light_brightness_percent", 0)),
    }
    for sensor_key, apply_action in mappings.items():
        target = TARGET_CONFIG.get(sensor_key)
        value = latest_readings.get(sensor_key)
        if target is None or value is None:
            continue
        # Choose an action based on current Q-values
        action = choose_action(sensor_key, value, target)
        # Apply the action to the associated actuator(s)
        apply_action(action)
        # Update the Q-values using the observed reward
        update_q(sensor_key, action, value, target)

    # Note: light cycle hours, light pulse frequency and other parameters
    # may require scheduling or more complex control logic. These can
    # be integrated into the mapping above as needed.


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
    """Provide AI-driven recommendations based on current readings and target values.

    In demo mode the recommendations are random to simulate experimentation. In
    real mode this function compares the latest sensor readings against the
    TARGET_CONFIG and suggests whether to increase, decrease or maintain
    each parameter. When a reading or target is missing, the suggestion
    returns None.
    """
    # Helper to compare value against target and return action
    def recommend(key: str, threshold: float = 0.05):
        """Return 'increase', 'decrease' or 'maintain' based on deviation from target.

        If the sensor reading is within +/- threshold (5%) of the target, the
        recommendation is 'maintain'. Otherwise, recommend increasing or
        decreasing the parameter accordingly. Returns None if either value
        is unavailable.
        """
        target = TARGET_CONFIG.get(key)
        value = latest_readings.get(key)
        if target is None or value is None:
            return None
        # Avoid division by zero; treat threshold as absolute difference when target is zero
        delta = abs(value - target)
        # Determine acceptable range
        acceptable = threshold * abs(target) if abs(target) > 0 else threshold
        if delta <= acceptable:
            return "maintain"
        return "increase" if value < target else "decrease"

    if MODE == "demo":
        # Random suggestions for demo mode to simulate experimentation
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
    # Real mode: compute recommendations based on deviations
    return {
        "adjust_co2": recommend("co2_ppm"),
        "adjust_air_temp": recommend("air_temp_celsius"),
        "adjust_humidity": recommend("humidity_percent"),
        "adjust_light_intensity": recommend("light_intensity_lux"),
        "adjust_pH": recommend("pH"),
        "adjust_water_temp": recommend("water_temp_celsius"),
        "adjust_water_flow_rate": recommend("water_flow_rate_lpm"),
        "adjust_audio_frequency": recommend("audio_frequency_hz"),
        "adjust_audio_decibels": recommend("audio_decibels_db"),
        "adjust_light_cycle": recommend("light_cycle_hours"),
        "adjust_light_brightness": recommend("light_brightness_percent"),
        "adjust_light_pulse_freq": recommend("light_pulse_freq_hz"),
    }

@app.get("/stream/sensors")
async def stream_sensors():
    """Stream the latest sensor readings as server-sent events (SSE).

    Clients can connect to this endpoint via EventSource to receive
    near real-time updates without polling. The server sends the
    current `latest_readings` dictionary every two seconds. In demo
    mode the stream returns simulated random values similar to the
    /sensors endpoint, while in real mode it streams the most recent
    readings stored in `latest_readings`.
    """
    async def event_generator():
        # Define ranges for random demo values
        demo_ranges = {
            "co2_ppm": (300, 800),
            "air_temp_celsius": (18, 30),
            "humidity_percent": (30, 70),
            "light_intensity_lux": (200, 1000),
            "pH": (6, 8),
            "water_temp_celsius": (18, 28),
            "water_flow_rate_lpm": (0.5, 5.0),
            "audio_frequency_hz": (200, 2000),
            "audio_decibels_db": (30, 90),
            "light_cycle_hours": (8, 18),
            "light_brightness_percent": (10, 100),
            "light_pulse_freq_hz": (0.5, 5.0),
        }
        while True:
            if MODE == "demo":
                # Generate random demo values for streaming
                data = {k: round(random.uniform(a, b), 2) for k, (a, b) in demo_ranges.items()}
            else:
                # Return latest readings (may include None)
                data = latest_readings.copy()
            # Yield SSE formatted message
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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

@app.get("/target-config")
def get_target_config():
    """Return the current target configuration used for automatic optimisation.

    The target configuration defines the desired sensor values for the
    optimisation loop in real mode. It is initialised to the optimal
    configuration of the first demo recipe (Radish) but can be updated
    via the POST /target-config endpoint. The returned dictionary maps
    sensor keys to their target values.
    """
    return TARGET_CONFIG

class TargetConfigRequest(BaseModel):
    plant: str

@app.post("/target-config")
def set_target_config(req: TargetConfigRequest):
    """Update the target configuration based on a plant name.

    Accepts a JSON body with a `plant` field specifying the name of a
    plant. The backend searches the demo_recipes (and real_recipes if
    in real mode) for a matching plant and updates TARGET_CONFIG to its
    optimal configuration. If no matching recipe is found, a 404 error
    is raised. Returns the updated target configuration.
    """
    plant_name = req.plant.strip().lower()
    # Search in demo recipes (always available) and real recipes if in real mode
    all_recipes = demo_recipes + real_recipes
    match = next((r for r in all_recipes if r["plant"].lower() == plant_name), None)
    if not match:
        raise HTTPException(status_code=404, detail="Plant not found in recipe database")
    # Update TARGET_CONFIG by copying the matching optimal config
    TARGET_CONFIG.clear()
    TARGET_CONFIG.update(match["optimal_config"])
    return TARGET_CONFIG

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

@app.get("/vision")
def get_vision(plant: str | None = None):
    """Return plant health metrics derived from camera analysis.

    In demo mode this endpoint returns a plausible plant size (in cm)
    and a colour index (0–1) representing leaf greenness for the selected
    plant. If a plant name is provided and exists in the demo database,
    its aquaponics_size_cm value is used; otherwise the first demo
    recipe's size is used. In real mode this endpoint returns values
    from the latest_readings dictionary, which are expected to be
    provided by an external vision system via the /sensor/readings
    endpoint. If no such values exist, None is returned for each key.
    """
    if MODE == "demo":
        # Use known optimal size for the specified plant if available
        if plant:
            match = next((r for r in demo_recipes if r["plant"].lower() == plant.lower()), None)
            if match:
                return {
                    "plant_size_cm": match["aquaponics_size_cm"],
                    "plant_color_index": 0.8,
                }
        # Default to first recipe's size
        rec = demo_recipes[0]
        return {
            "plant_size_cm": rec["aquaponics_size_cm"],
            "plant_color_index": 0.8,
        }
    # Real mode: return vision metrics from latest readings
    return {
        "plant_size_cm": latest_readings.get("plant_size_cm"),
        "plant_color_index": latest_readings.get("plant_color_index"),
    }

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

