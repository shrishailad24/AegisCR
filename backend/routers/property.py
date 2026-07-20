from fastapi import APIRouter, Query, HTTPException
from backend.services.kaveri_service import fetch_districts, fetch_taluks, fetch_villages, fetch_guideline_rate

router = APIRouter(
    prefix="/api",
    tags=["Properties & Guidance Values"]
)

@router.get("/districts")
def get_districts():
    try:
        return {"districts": fetch_districts()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/taluks")
def get_taluks(district: str = Query(..., description="District name")):
    try:
        return {"taluks": fetch_taluks(district)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/villages")
def get_villages(
    district: str = Query(..., description="District name"),
    taluk: str = Query(..., description="Taluk name / Sub-Registrar office")
):
    try:
        return {"villages": fetch_villages(district, taluk)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guideline")
def get_guideline_rate(
    district: str = Query(..., description="District name"),
    taluk: str = Query(..., description="Taluk name"),
    village: str = Query(..., description="Village / area name"),
    land_type: str = Query("Residential", description="Residential, Commercial, Agricultural, Industrial"),
    state: str = Query("Karnataka", description="State name")
):
    try:
        return fetch_guideline_rate(district, taluk, village, land_type, state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
