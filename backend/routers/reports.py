import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils.pdf_generator import generate_pdf, generate_gold_pdf

router = APIRouter(
    prefix="/api",
    tags=["Reports & Dossiers"]
)

class GeneratePdfInput(BaseModel):
    name: str
    gender: str = "Male"
    married: str = "Yes"
    dependents: str = "0"
    education: str = "Graduate"
    self_emp: str = "No"
    credit: float = 1.0
    property_area: str = "Urban"
    loan_amount: float
    loan_term: float
    app_income: float
    co_income: float = 0.0
    result_text: str = "Approved"
    property_details: dict = None
    ai_explanation: str = ""
    officer_notes: str = ""

class GenerateGoldPdfInput(BaseModel):
    name: str
    weight: float
    purity: str
    rate_per_gram: float
    gold_value: float
    eligible_loan: float
    interest_rate: float = 9.5
    tenure: float = 12.0
    officer_notes: str = ""

@router.post("/generate-sanction-pdf")
def generate_sanction_pdf(payload: GeneratePdfInput):
    """
    POST /api/generate-sanction-pdf
    Exposes reportlab compiler pipeline, streaming underwriting appraisal letter.
    """
    try:
        os.makedirs("assets/generated_letters", exist_ok=True)
        pdf_path = generate_pdf(
            name=payload.name,
            gender=payload.gender,
            married=payload.married,
            dependents=payload.dependents,
            education=payload.education,
            self_emp=payload.self_emp,
            credit=payload.credit,
            property_area=payload.property_area,
            loan_amount=payload.loan_amount,
            loan_term=payload.loan_term,
            app_income=payload.app_income,
            co_income=payload.co_income,
            result_text=payload.result_text,
            property_details=payload.property_details,
            ai_explanation=payload.ai_explanation,
            officer_notes=payload.officer_notes
        )
        if os.path.exists(pdf_path):
            return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
        else:
            raise HTTPException(status_code=404, detail="Generated PDF report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-gold-sanction-pdf")
def generate_gold_sanction_pdf(payload: GenerateGoldPdfInput):
    """
    POST /api/generate-gold-sanction-pdf
    Compiles and returns a PDF report for Gold Appraisal.
    """
    try:
        os.makedirs("assets/generated_letters", exist_ok=True)
        pdf_path = generate_gold_pdf(
            name=payload.name,
            weight=payload.weight,
            purity=payload.purity,
            rate_per_gram=payload.rate_per_gram,
            gold_value=payload.gold_value,
            eligible_loan=payload.eligible_loan,
            interest_rate=payload.interest_rate,
            tenure=int(payload.tenure),
            officer_notes=payload.officer_notes
        )
        if os.path.exists(pdf_path):
            return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
        else:
            raise HTTPException(status_code=404, detail="Generated Gold PDF report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
