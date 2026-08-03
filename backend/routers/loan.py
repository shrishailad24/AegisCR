from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/api",
    tags=["AI Underwriting & Credit Risk"]
)

class PredictUnderwritingInput(BaseModel):
    monthly_income: float
    loan_amount: float
    dti: float
    ltv: float
    risk_score: float
    trust_score: float = 98

@router.post("/predict-underwriting")
def predict_underwriting(payload: PredictUnderwritingInput):
    """
    POST /api/predict-underwriting
    AI loan risk analysis and credit decision engine.
    """
    reasons = []
    if payload.dti <= 40:
        reasons.append("✓ Stable debt-to-income servicing profile")
    else:
        reasons.append("✗ Elevated monthly EMI service ratio")
        
    if payload.ltv <= 75:
        reasons.append("✓ Low loan leverage exposure")
    else:
        reasons.append("✗ High loan-to-value collateral exposure")
        
    if payload.trust_score >= 80:
        reasons.append("✓ Verified applicant identity credentials")
    else:
        reasons.append("✗ Identity verification credential mismatch")
        
    if payload.dti <= 45 and payload.ltv <= 80 and payload.trust_score >= 80:
        recommendation = "Approve"
        confidence = 96
        overall_risk = "Low"
    elif payload.dti > 55 or payload.ltv > 85 or payload.trust_score < 50:
        recommendation = "Reject"
        confidence = 90
        overall_risk = "High"
    else:
        recommendation = "Manual Review"
        confidence = 85
        overall_risk = "Medium"
        
    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "overall_risk": overall_risk,
        "probability_of_default": 4 if overall_risk == "Low" else 15 if overall_risk == "Medium" else 35,
        "reasons": reasons
    }

@router.get("/analytics-stats")
def get_analytics_stats():
    """
    GET /api/analytics-stats
    Exposes aggregated portfolio indicators and trends for charts.
    """
    return {
        "loans_approved": 142,
        "loans_rejected": 28,
        "avg_property_value": 7850000,
        "high_risk_applications": 14,
        "district_distribution": [
            {"district": "Bengaluru", "value": 52},
            {"district": "Mysore", "value": 24},
            {"district": "Ramanagara", "value": 18},
            {"district": "Bagalkote", "value": 15},
            {"district": "Belagavi", "value": 12}
        ],
        "monthly_trends": [
            {"month": "Jan", "approved": 18, "rejected": 3},
            {"month": "Feb", "approved": 22, "rejected": 2},
            {"month": "Mar", "approved": 25, "rejected": 4},
            {"month": "Apr", "approved": 29, "rejected": 6},
            {"month": "May", "approved": 32, "rejected": 8},
            {"month": "Jun", "approved": 16, "rejected": 5}
        ]
    }
