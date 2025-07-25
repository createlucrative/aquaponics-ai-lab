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
    if MODE == "demo":
        return {
            "co2": round(random.uniform(300, 800), 2),
            "air_temp": round(random.uniform(18, 30), 2),
            "humidity": round(random.uniform(30, 70), 2),
            "light_intensity": round(random.uniform(0, 1000), 2),
            "pH": round(random.uniform(6, 8), 2),
            "water_temp": round(random.uniform(18, 28), 2),
        }
    else:
        return {
            "co2": None,
            "air_temp": None,
            "humidity": None,
            "light_intensity": None,
            "pH": None,
            "water_temp": None,
        }

@app.get("/ai")
def get_ai_recommendations():
    """Provide AI-driven recommendations. In demo mode returns random suggestions; in real mode placeholders."""
    if MODE == "demo":
        return {
            "adjust_co2": random.choice(["increase", "decrease", "maintain"]),
            "adjust_light": random.choice([
                "increase intensity",
                "decrease intensity",
                "change spectrum",
                "maintain",
            ]),
            "adjust_watering": random.choice(["increase flow", "decrease flow", "maintain"]),
        }
    else:
        return {
            "adjust_co2": None,
            "adjust_light": None,
            "adjust_watering": None,
        }
