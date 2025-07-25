from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

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
def get_sensors():
    """Return sensor readings. In demo mode returns simulated data; in real mode returns placeholders."""
    # Define the keys for all sensors we support. This ensures real mode returns a consistent shape
    sensor_keys = {
        "co2_ppm": lambda: round(random.uniform(300, 800), 2),
        "air_temp_celsius": lambda: round(random.uniform(18, 30), 2),
        "humidity_percent": lambda: round(random.uniform(30, 70), 2),
        "light_intensity_lux": lambda: round(random.uniform(200, 1000), 2),
        "pH": lambda: round(random.uniform(6, 8), 2),
        "water_temp_celsius": lambda: round(random.uniform(18, 28), 2),
        # New sensors with appropriate units
        "water_flow_rate_lpm": lambda: round(random.uniform(0.5, 5.0), 2),  # liters per minute
        "audio_frequency_hz": lambda: round(random.uniform(200, 2000), 2),  # frequency in hertz
        "audio_decibels_db": lambda: round(random.uniform(30, 90), 2),  # sound level in decibels
        "light_cycle_hours": lambda: round(random.uniform(8, 18), 2),  # hours of light per day
        "light_brightness_percent": lambda: round(random.uniform(10, 100), 2),  # brightness percentage
        "light_pulse_freq_hz": lambda: round(random.uniform(0.5, 5.0), 2),  # pulse frequency in hertz
    }

    if MODE == "demo":
        # Generate simulated readings for each sensor key
        return {k: gen() for k, gen in sensor_keys.items()}
    else:
        # Return None for each sensor when running in real mode without connected hardware.
        return {k: None for k in sensor_keys}

@app.get("/ai")
def get_ai_recommendations():
    """Provide AI-driven recommendations. In demo mode returns random suggestions; in real mode placeholders."""
    if MODE == "demo":
        # Provide recommendations for every sensor parameter. These are simple heuristics chosen at random.
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
            # New recommendations corresponding to new sensors
            "adjust_water_flow_rate": random.choice(["increase", "decrease", "maintain"]),
            "adjust_audio_frequency": random.choice([
                "increase frequency",
                "decrease frequency",
                "maintain",
            ]),
            "adjust_audio_decibels": random.choice([
                "increase volume",
                "decrease volume",
                "maintain",
            ]),
            "adjust_light_cycle": random.choice([
                "extend photoperiod",
                "shorten photoperiod",
                "maintain",
            ]),
            "adjust_light_brightness": random.choice(["increase", "decrease", "maintain"]),
            "adjust_light_pulse_freq": random.choice([
                "increase frequency",
                "decrease frequency",
                "maintain",
            ]),
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
