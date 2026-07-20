from fastapi import APIRouter, Query
from typing import Optional
from backend.services.vehicle_service import (
    fetch_carquery_makes,
    fetch_carquery_models,
    fetch_carquery_specs
)

router = APIRouter(prefix="/api/vehicle", tags=["Vehicle Master & CarQuery API"])

@router.get("/makes")
def get_vehicle_makes():
    """Retrieve all available vehicle makes/brands from CarQuery API & Vehicle Master DB."""
    makes = fetch_carquery_makes()
    return {"makes": makes, "total": len(makes)}

@router.get("/models")
def get_vehicle_models(make: str = Query(..., description="Vehicle Brand / Make")):
    """Retrieve vehicle models for a brand from CarQuery API & Vehicle Master DB."""
    models = fetch_carquery_models(make)
    return {"make": make, "models": models, "total": len(models)}

@router.get("/specs")
def get_vehicle_specs(
    make: str = Query(..., description="Vehicle Make"),
    model: str = Query(..., description="Vehicle Model")
):
    """Retrieve specs (engine, transmission, fuel type, body) and prices from CarQuery API & Vehicle Master DB."""
    specs = fetch_carquery_specs(make, model)
    return specs
