from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aquaponics AI backend"}

# TODO: Implement sensor data ingestion, AI optimization, actuator control, and logging modules
