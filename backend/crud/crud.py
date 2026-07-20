import uuid
from sqlalchemy.orm import Session
from backend.models import models
from backend.schemas import schemas

# --- APPLICATION CRUD ---
def create_loan_application(db: Session, app_in: schemas.LoanApplicationCreate):
    ref_no = app_in.reference_no or f"AEGIS-{uuid.uuid4().hex[:8].upper()}"
    db_app = models.LoanApplication(
        reference_no=ref_no,
        user_id=app_in.user_id,
        customer_name=app_in.customer_name,
        module=app_in.module,
        requested_amount=app_in.requested_amount,
        status=app_in.status
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def get_all_loan_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LoanApplication).order_by(models.LoanApplication.created_at.desc()).offset(skip).limit(limit).all()

def get_loan_application_by_id(db: Session, app_id: int):
    return db.query(models.LoanApplication).filter(models.LoanApplication.id == app_id).first()

def update_loan_application_status(db: Session, app_id: int, status: str):
    db_app = db.query(models.LoanApplication).filter(models.LoanApplication.id == app_id).first()
    if db_app:
        db_app.status = status
        db.commit()
        db.refresh(db_app)
    return db_app

# --- AI PREDICTION CRUD ---
def create_ai_prediction(db: Session, pred_in: schemas.AIPredictionCreate):
    db_pred = models.AIPrediction(**pred_in.dict())
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    return db_pred

def get_ai_prediction_by_app_id(db: Session, app_id: int):
    return db.query(models.AIPrediction).filter(models.AIPrediction.application_id == app_id).first()

# --- DOCUMENT VERIFICATION CRUD ---
def create_document_verification(db: Session, doc_in: schemas.DocumentVerificationCreate):
    db_doc = models.DocumentVerification(**doc_in.dict())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_documents_by_app_id(db: Session, app_id: int):
    return db.query(models.DocumentVerification).filter(models.DocumentVerification.application_id == app_id).all()

# --- AUDIT LOG CRUD ---
def create_audit_log(db: Session, log_in: schemas.AuditLogCreate):
    db_log = models.AuditLog(**log_in.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_all_audit_logs(db: Session, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(limit).all()
