from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.schemas import schemas
from backend.crud import crud

router = APIRouter(prefix="/api/audit-logs", tags=["MySQL Audit Logs"])

@router.get("", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve system audit trail logs from MySQL."""
    return crud.get_all_audit_logs(db, limit=limit)

@router.post("", response_model=schemas.AuditLogResponse)
def record_audit_log(log_in: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    """Record an audit trail event in MySQL."""
    return crud.create_audit_log(db, log_in)
