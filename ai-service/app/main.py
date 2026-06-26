from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="RoadLancer AI Engine Microservice 🤖",
    description="Calculates AI price floors to eliminate race-to-the-bottom exploitation and suggests nearby return loads (backhaul matching).",
    version="0.1.0"
)

class PriceEstimateRequest(BaseModel):
    distance_km: float = Field(..., gt=0, example=1450.5)
    weight_kg: float = Field(..., gt=0, example=18000.0)
    goods_category: str = Field(..., example="general")
    vehicle_type: str = Field(..., example="heavy_truck")

class PriceEstimateResponse(BaseModel):
    estimated_min: float
    estimated_max: float
    floor_price: float
    confidence: float
    currency: str = "INR"

class BackhaulRequest(BaseModel):
    dropoff_lat: float
    dropoff_lng: float
    vehicle_type: str

class BackhaulSuggestion(BaseModel):
    shipment_id: int
    pickup_city: str
    dropoff_city: str
    distance_from_driver_km: float
    price_range: str

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "RoadLancer AI Microservice"}

@app.post("/price-estimate", response_model=PriceEstimateResponse)
def estimate_price(request: PriceEstimateRequest):
    """Calculate AI price floor and market rate estimates.
    In Phase 0 Alpha, this uses deterministic baseline rate charts.
    In Phase 2, this will load serialized scikit-learn/XGBoost models."""
    base_rate_per_km = 32.0 # INR per km baseline
    weight_multiplier = 1.0 + (request.weight_kg / 20000.0)
    
    category_multipliers = {
        "general": 1.0,
        "fragile": 1.25,
        "perishable": 1.35,
        "heavy_machinery": 1.5,
    }
    cat_mult = category_multipliers.get(request.goods_category.lower(), 1.0)
    
    raw_estimate = request.distance_km * base_rate_per_km * weight_multiplier * cat_mult
    
    # AI Floor is hard-coded at 90% of raw fair estimate
    floor_price = round(raw_estimate * 0.9, -2) # Round to nearest hundred
    est_min = round(raw_estimate, -2)
    est_max = round(raw_estimate * 1.25, -2)
    
    return PriceEstimateResponse(
        estimated_min=est_min,
        estimated_max=est_max,
        floor_price=floor_price,
        confidence=0.88
    )

@app.post("/backhaul-suggest", response_model=List[BackhaulSuggestion])
def suggest_backhaul(request: BackhaulRequest):
    """Return ranked nearby available return loads. Mocked for Phase 0 Alpha."""
    return [
        BackhaulSuggestion(
            shipment_id=101,
            pickup_city="Mumbai",
            dropoff_city="Delhi",
            distance_from_driver_km=12.4,
            price_range="₹45,000 - ₹52,000"
        ),
        BackhaulSuggestion(
            shipment_id=102,
            pickup_city="Thane",
            dropoff_city="Ahmedabad",
            distance_from_driver_km=28.1,
            price_range="₹18,000 - ₹22,000"
        )
    ]
