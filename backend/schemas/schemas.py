from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    firebase_uid: str
    name: str
    email: str
    role: str = "Customer"
    branch_id: Optional[int] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- LOAN APPLICATION SCHEMAS ---
class LoanApplicationBase(BaseModel):
    customer_name: str
    module: str
    requested_amount: float
    status: str = "Pending"

class LoanApplicationCreate(LoanApplicationBase):
    user_id: Optional[int] = None
    reference_no: Optional[str] = None

class LoanApplicationStatusUpdate(BaseModel):
    status: str # Approved, Rejected, Under Review

class LoanApplicationResponse(LoanApplicationBase):
    id: int
    reference_no: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- AI PREDICTION SCHEMAS ---
class AIPredictionCreate(BaseModel):
    application_id: int
    approval_probability: float
    confidence_score: float
    credit_risk_score: float
    recommendation: str
    explainable_xai_output: str

class AIPredictionResponse(AIPredictionCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- DOCUMENT VERIFICATION SCHEMAS ---
class DocumentVerificationCreate(BaseModel):
    application_id: int
    document_type: str
    ocr_status: str = "Verified"
    is_tampered: bool = False
    confidence_score: float = 95.0
    raw_text: Optional[str] = None

class DocumentVerificationResponse(DocumentVerificationCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- AUDIT LOG SCHEMAS ---
class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    actor_name: str
    role: str
    action: str
    detail: Optional[str] = None

class AuditLogResponse(AuditLogCreate):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True
