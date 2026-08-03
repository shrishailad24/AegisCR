from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.ocr_service import audit_uploaded_documents

router = APIRouter(
    prefix="/api",
    tags=["OCR & Document Trust"]
)

class VerifyDocumentsInput(BaseModel):
    aadhaar_name: str
    pan_name: str
    sale_deed_name: str
    rtc_owner_name: str
    has_aadhaar: bool = True
    has_pan: bool = True
    has_income: bool = True
    has_deed: bool = True
    has_rtc: bool = True

@router.post("/verify-documents")
def verify_documents(payload: VerifyDocumentsInput):
    """
    POST /api/verify-documents
    Runs identity verification matching checks and documents trust auditing.
    """
    return audit_uploaded_documents(
        aadhaar_name=payload.aadhaar_name,
        pan_name=payload.pan_name,
        sale_deed_name=payload.sale_deed_name,
        rtc_owner_name=payload.rtc_owner_name,
        has_aadhaar=payload.has_aadhaar,
        has_pan=payload.has_pan,
        has_income=payload.has_income,
        has_deed=payload.has_deed,
        has_rtc=payload.has_rtc
    )
