from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="Customer", nullable=False) # Customer, Loan Officer, Branch Manager, Admin
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("LoanApplication", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    branch_name = Column(String(255), nullable=False)
    branch_code = Column(String(50), unique=True, index=True, nullable=False)
    district = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    reference_no = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    module = Column(String(50), nullable=False, index=True) # home, agri, commercial, gold, farm_equipment, vehicle
    requested_amount = Column(Float, nullable=False)
    status = Column(String(50), default="Pending", index=True) # Pending, Approved, Rejected, Under Review
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    property_valuation = relationship("PropertyValuation", back_populates="application", uselist=False)
    gold_loan = relationship("GoldLoan", back_populates="application", uselist=False)
    ai_prediction = relationship("AIPrediction", back_populates="application", uselist=False)
    document_verifications = relationship("DocumentVerification", back_populates="application")

class KaveriGuidanceValue(Base):
    __tablename__ = "kaveri_guidance_values"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), index=True, nullable=False)
    taluk = Column(String(100), index=True, nullable=False)
    village = Column(String(100), index=True, nullable=False)
    property_classification = Column(String(255), nullable=False)
    guidance_value_sqft = Column(Float, nullable=False)
    rate_per_acre = Column(Float, nullable=True)
    unit = Column(String(50), default="₹/sqft")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_kaveri_location', 'district', 'taluk', 'village'),
    )

class PropertyValuation(Base):
    __tablename__ = "property_valuations"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    district = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    survey_number = Column(String(100), nullable=False)
    plot_area = Column(Float, nullable=False)
    builtup_area = Column(Float, default=0.0)
    market_value = Column(Float, nullable=False)
    guidance_value = Column(Float, nullable=False)
    ltv_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplication", back_populates="property_valuation")

class VehiclePrice(Base):
    __tablename__ = "vehicle_prices"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), index=True, nullable=False)
    model = Column(String(100), index=True, nullable=False)
    variant = Column(String(100))
    year = Column(Integer, default=2024)
    category = Column(String(100))
    fuel_type = Column(String(50))
    transmission = Column(String(50))
    engine_cc = Column(String(50))
    body_type = Column(String(50))
    ex_showroom_price = Column(Float, nullable=False)
    on_road_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_vehicle_brand_model', 'brand', 'model'),
    )

class FarmEquipmentPrice(Base):
    __tablename__ = "farm_equipment_prices"

    id = Column(Integer, primary_key=True, index=True)
    equipment_type = Column(String(100), index=True, nullable=False)
    brand = Column(String(100), nullable=False)
    base_cost = Column(Float, nullable=False)
    subsidy_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class GoldLoan(Base):
    __tablename__ = "gold_loans"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    borrower_name = Column(String(255), nullable=False)
    weight_grams = Column(Float, nullable=False)
    purity = Column(String(50), nullable=False)
    rate_per_gram = Column(Float, nullable=False)
    gold_value = Column(Float, nullable=False)
    eligible_loan = Column(Float, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplication", back_populates="gold_loan")

class DocumentVerification(Base):
    __tablename__ = "document_verifications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False) # Aadhaar, PAN, Salary Slip, Property Deed
    ocr_status = Column(String(50), default="Verified") # Verified, Flagged, Failed
    is_tampered = Column(Boolean, default=False)
    confidence_score = Column(Float, default=95.0)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplication", back_populates="document_verifications")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False)
    approval_probability = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    credit_risk_score = Column(Float, nullable=False)
    recommendation = Column(String(50), nullable=False) # Approve, Manual Review, Reject
    explainable_xai_output = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("LoanApplication", back_populates="ai_prediction")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False, index=True)
    detail = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
