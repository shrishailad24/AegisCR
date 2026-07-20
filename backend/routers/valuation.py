from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.valuation_service import evaluate_property_value
from backend.services.kaveri_service import fetch_guideline_rate

router = APIRouter(
    prefix="/api",
    tags=["AI Property Valuation & Loan Modules"]
)

class PredictPropertyValueInput(BaseModel):
    state: str = "Karnataka"
    district: str
    taluk: str = ""
    village: str = ""
    latitude: float = 12.9716
    longitude: float = 77.5946
    area: float
    guidance_value: float
    property_type: str

class GuidanceLookupInput(BaseModel):
    state: str = "Karnataka"
    district: str
    taluk: str = ""
    village: str = ""
    land_type: str = "Residential"

class EvaluateLoanModuleInput(BaseModel):
    module: str # "home", "agriculture", "commercial", "gold", "farm_equipment", "vehicle"
    district: str = ""
    taluk: str = ""
    village: str = ""
    survey_number: str = ""
    plot_area: float = 0.0 # sqft or acres
    built_up_area: float = 0.0
    land_type: str = "Residential" # Dry Land, Black Soil Dry, Wet Land, Bagayat, Commercial, etc.
    construction_year: int = 2018
    property_type: str = "Independent House"
    gold_weight_grams: float = 0.0
    gold_purity: str = "22K"
    
    # Farm Equipment parameters
    equipment_type: str = "Tractor"
    equipment_brand: str = "Mahindra"
    equipment_cost: float = 0.0
    down_payment: float = 0.0
    farm_size_acres: float = 0.0
    annual_income: float = 0.0
    subsidy_amount: float = 0.0
    
    # Vehicle parameters
    vehicle_category: str = "SUV"
    vehicle_make: str = "Mahindra"
    vehicle_model: str = "Thar ROXX"
    vehicle_variant: str = "AX7L 4WD Diesel MT"
    vehicle_year: int = 2024
    fuel_type: str = "Diesel"
    transmission: str = "Manual"
    engine_cc: str = "2184 cc"
    body_type: str = "SUV"
    ex_showroom_price: float = 0.0
    on_road_price: float = 0.0
    insurance_cost: float = 0.0
    registration_cost: float = 0.0
    
    # Loan Structure & Guarantor parameters
    loan_structure: str = "Secured Loan"
    loan_purpose: str = "Home Purchase"
    collateral_type: str = "Property"
    collateral_value: float = 0.0
    guarantor_name: str = ""
    guarantor_relation: str = ""
    guarantor_income: float = 0.0
    guarantor_cibil: int = 750
    
    requested_loan: float = 0.0
    interest_rate: float = 9.5
    tenure_months: int = 60

@router.post("/predict-property-value")
def predict_property_value(payload: PredictPropertyValueInput):
    """
    POST /api/predict-property-value
    ML-driven AI collateral asset property valuation prediction.
    """
    try:
        return evaluate_property_value(
            state=payload.state,
            district=payload.district,
            taluk=payload.taluk,
            village=payload.village,
            latitude=payload.latitude,
            longitude=payload.longitude,
            area=payload.area,
            guidance_value=payload.guidance_value,
            property_type=payload.property_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kaveri-guidance-by-type")
def get_kaveri_guidance_by_type(payload: GuidanceLookupInput):
    """
    POST /api/kaveri-guidance-by-type
    Fetches guidance value from Kaveri guidelines.db for specific land types (Dry Land, Black Soil Dry, Wet Land, Bagayat, Commercial, Residential).
    """
    try:
        return fetch_guideline_rate(
            district=payload.district,
            taluk=payload.taluk,
            village=payload.village,
            land_type=payload.land_type,
            state=payload.state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate-loan-module")
def evaluate_loan_module(payload: EvaluateLoanModuleInput):
    """
    POST /api/evaluate-loan-module
    Evaluates financial metrics, LTV, EMI, and risk for Home, Agriculture, Commercial, Gold, Farm Equipment, and Vehicle Loans.
    """
    try:
        mod = payload.module.lower()
        if mod == "home":
            guidance_info = fetch_guideline_rate(payload.district, payload.taluk, payload.village, "Residential", "Karnataka")
            rate_sqft = guidance_info.get("guideline_rate_per_sqft", 2500.0) or 2500.0
            land_value = payload.plot_area * rate_sqft
            age = max(0, 2026 - payload.construction_year)
            depreciation = max(0.4, 1.0 - (age * 0.015))
            bldg_rate = 1800.0 * depreciation
            bldg_value = payload.built_up_area * bldg_rate
            total_prop_val = land_value + bldg_value
            rec_loan = total_prop_val * 0.80
            req_loan = payload.requested_loan or rec_loan
            ltv = (req_loan / total_prop_val * 100.0) if total_prop_val > 0 else 0.0
            
            return {
                "module": "home",
                "rate_per_sqft": round(rate_sqft, 2),
                "land_value": round(land_value, 2),
                "building_value": round(bldg_value, 2),
                "total_property_value": round(total_prop_val, 2),
                "recommended_loan": round(rec_loan, 2),
                "eligible_loan": round(rec_loan, 2),
                "ltv": round(ltv, 1),
                "status": "Eligible" if ltv <= 85 else "High LTV Warning"
            }
        elif mod == "agriculture":
            guidance_info = fetch_guideline_rate(payload.district, payload.taluk, payload.village, payload.land_type, "Karnataka")
            rate_acre = guidance_info.get("guideline_rate_per_sqft", 150000.0) or 150000.0
            total_land_val = payload.plot_area * rate_acre
            rec_loan = total_land_val * 0.75
            req_loan = payload.requested_loan or rec_loan
            ltv = (req_loan / total_land_val * 100.0) if total_land_val > 0 else 0.0
            risk_score = 15 if payload.land_type in ["Bagayat Land", "Wet Land"] else 30
            
            return {
                "module": "agriculture",
                "land_type": payload.land_type,
                "rate_per_acre": round(rate_acre, 2),
                "total_land_value": round(total_land_val, 2),
                "eligible_loan": round(rec_loan, 2),
                "ltv": round(ltv, 1),
                "risk_score": risk_score,
                "matched_classification": guidance_info.get("matched_classification", payload.land_type)
            }
        elif mod == "commercial":
            guidance_info = fetch_guideline_rate(payload.district, payload.taluk, payload.village, "Commercial", "Karnataka")
            rate_sqft = guidance_info.get("guideline_rate_per_sqft", 4500.0) or 4500.0
            land_val = payload.plot_area * rate_sqft
            bldg_val = payload.built_up_area * 2500.0
            total_val = land_val + bldg_val
            eligible_loan = total_val * 0.65
            req_loan = payload.requested_loan or eligible_loan
            
            r = (payload.interest_rate / 100.0) / 12.0
            n = payload.tenure_months or 180
            emi = (req_loan * r * ((1 + r)**n)) / (((1 + r)**n) - 1) if r > 0 and n > 0 else 0.0
            
            return {
                "module": "commercial",
                "comm_rate_per_sqft": round(rate_sqft, 2),
                "property_value": round(total_val, 2),
                "eligible_loan": round(eligible_loan, 2),
                "ltv": 65.0,
                "monthly_emi": round(emi, 2),
                "total_interest": round(max(0, (emi * n) - req_loan), 2)
            }
        elif mod == "gold":
            from backend.routers.gold import fetch_live_gold_price
            gold_price_data = fetch_live_gold_price()
            purity = payload.gold_purity
            rate = gold_price_data.get("price_gram_22k", 5850.0)
            if purity == "24K":
                rate = gold_price_data.get("price_gram_24k", 6380.0)
            elif purity == "18K":
                rate = gold_price_data.get("price_gram_18k", 4780.0)
                
            gold_val = payload.gold_weight_grams * rate
            eligible_loan = gold_val * 0.75
            req_loan = payload.requested_loan or eligible_loan
            
            r = (payload.interest_rate / 100.0) / 12.0
            n = payload.tenure_months or 12
            emi = (req_loan * r * ((1 + r)**n)) / (((1 + r)**n) - 1) if r > 0 and n > 0 else 0.0
            interest = (emi * n) - req_loan
            
            return {
                "module": "gold",
                "rate_per_gram": round(rate, 2),
                "gold_value": round(gold_val, 2),
                "eligible_loan": round(eligible_loan, 2),
                "monthly_emi": round(emi, 2),
                "total_interest": round(max(0, interest), 2),
                "currency": gold_price_data.get("currency", "INR"),
                "last_updated": gold_price_data.get("last_updated", "Just now")
            }
        elif mod == "farm_equipment":
            cost = payload.equipment_cost or 850000.0
            subsidy = payload.subsidy_amount or (cost * 0.25)
            net_cost = max(0, cost - subsidy)
            down_pay = payload.down_payment or (net_cost * 0.15)
            net_loan = payload.requested_loan or max(0, net_cost - down_pay)
            eligible_loan = net_cost * 0.85
            ltv = (net_loan / net_cost * 100.0) if net_cost > 0 else 0.0
            
            r = (payload.interest_rate / 100.0) / 12.0
            n = payload.tenure_months or 60
            emi = (net_loan * r * ((1 + r)**n)) / (((1 + r)**n) - 1) if r > 0 and n > 0 else 0.0
            
            risk_score = 15 if (payload.farm_size_acres >= 5 and payload.annual_income >= 300000) else 25 if payload.farm_size_acres >= 2 else 40
            
            return {
                "module": "farm_equipment",
                "equipment_type": payload.equipment_type,
                "equipment_brand": payload.equipment_brand,
                "equipment_cost": round(cost, 2),
                "subsidy_amount": round(subsidy, 2),
                "net_equipment_cost": round(net_cost, 2),
                "down_payment": round(down_pay, 2),
                "eligible_loan": round(eligible_loan, 2),
                "loan_sanction": round(net_loan, 2),
                "ltv": round(ltv, 1),
                "monthly_emi": round(emi, 2),
                "repayment_risk_score": risk_score
            }
        elif mod == "vehicle":
            ex_price = payload.ex_showroom_price or 1200000.0
            on_road = payload.on_road_price or (ex_price + payload.insurance_cost + payload.registration_cost or (ex_price * 1.14))
            down_pay = payload.down_payment or (on_road * 0.15)
            net_loan = payload.requested_loan or max(0, on_road - down_pay)
            eligible_loan = on_road * 0.85
            ltv = (net_loan / on_road * 100.0) if on_road > 0 else 0.0
            
            r = (payload.interest_rate / 100.0) / 12.0
            n = payload.tenure_months or 60
            emi = (net_loan * r * ((1 + r)**n)) / (((1 + r)**n) - 1) if r > 0 and n > 0 else 0.0
            
            credit_risk = 15 if ltv <= 80 else 30
            
            return {
                "module": "vehicle",
                "vehicle_category": payload.vehicle_category,
                "vehicle_make": payload.vehicle_make,
                "vehicle_model": payload.vehicle_model,
                "vehicle_variant": payload.vehicle_variant,
                "vehicle_year": payload.vehicle_year,
                "fuel_type": payload.fuel_type,
                "transmission": payload.transmission,
                "engine_cc": payload.engine_cc,
                "body_type": payload.body_type,
                "ex_showroom_price": round(ex_price, 2),
                "on_road_price": round(on_road, 2),
                "down_payment": round(down_pay, 2),
                "eligible_loan": round(eligible_loan, 2),
                "loan_sanction": round(net_loan, 2),
                "ltv": round(ltv, 1),
                "monthly_emi": round(emi, 2),
                "credit_risk_score": credit_risk,
                "loan_structure": payload.loan_structure,
                "loan_purpose": payload.loan_purpose,
                "collateral_type": payload.collateral_type,
                "collateral_value": payload.collateral_value,
                "guarantor_name": payload.guarantor_name,
                "guarantor_relation": payload.guarantor_relation,
                "guarantor_income": payload.guarantor_income,
                "guarantor_cibil": payload.guarantor_cibil
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown loan module: {payload.module}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
