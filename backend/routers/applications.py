from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.schemas import schemas
from backend.crud import crud

router = APIRouter(prefix="/api/applications", tags=["MySQL Loan Applications"])

@router.post("", response_model=schemas.LoanApplicationResponse)
def submit_loan_application(app_in: schemas.LoanApplicationCreate, db: Session = Depends(get_db)):
    """Submit new loan application and store in MySQL."""
    return crud.create_loan_application(db, app_in)

@router.get("", response_model=List[schemas.LoanApplicationResponse])
def get_all_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all loan applications for officer dashboard from MySQL."""
    return crud.get_all_loan_applications(db, skip=skip, limit=limit)

@router.get("/{app_id}", response_model=schemas.LoanApplicationResponse)
def get_application(app_id: int, db: Session = Depends(get_db)):
    db_app = crud.get_loan_application_by_id(db, app_id)
    if not db_app:
        raise HTTPException(status_code=404, detail="Loan application not found")
    return db_app

@router.put("/{app_id}/status", response_model=schemas.LoanApplicationResponse)
def update_application_status(app_id: int, update_in: schemas.LoanApplicationStatusUpdate, db: Session = Depends(get_db)):
    """Officer approves, rejects, or requests manual review in MySQL."""
    db_app = crud.update_loan_application_status(db, app_id, update_in.status)
    if not db_app:
        raise HTTPException(status_code=404, detail="Loan application not found")
    
    # Audit log entry
    crud.create_audit_log(db, schemas.AuditLogCreate(
        actor_name="Officer Dashboard",
        role="Loan Officer",
        action=f"Application {update_in.status}",
        detail=f"Loan Application ID {app_id} status updated to {update_in.status}"
    ))
    return db_app

@router.post("/ai-prediction", response_model=schemas.AIPredictionResponse)
def store_ai_prediction(pred_in: schemas.AIPredictionCreate, db: Session = Depends(get_db)):
    """Store Explainable AI prediction results in MySQL ai_predictions table."""
    return crud.create_ai_prediction(db, pred_in)
