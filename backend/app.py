from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os
import json

from backend.model import predict_route_severity_risk

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/maps-api-key")
def get_maps_api_key():
    return {"key": os.getenv("GOOGLE_MAPS_API_KEY")}

@app.get("/data/obstacles.json")
def get_obstacles():
    with open(FRONTEND_DIR / "data" / "obstacles.json") as f:
        return json.load(f)

class RoutePoints(BaseModel):
    points: list[list[float]]

@app.post("/predict-route-severity")
def predict_route(route: RoutePoints):
    severity = predict_route_severity_risk(route.points)
    return {"severity": severity}

@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",

)
