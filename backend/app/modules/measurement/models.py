from sqlalchemy import Column, String, DateTime, Text, Float, Enum, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class MeasurementType(str, enum.Enum):
    """Measurement type enum."""
    DAILY = "daily"
    WEEKLY = "weekly"
    PROCESS = "process"
    GOAL = "goal"


class MeasurementModel(Base):
    """Measurement database model - stores calculated metrics."""
    __tablename__ = "measurements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    measurement_type = Column(Enum(MeasurementType), nullable=False)
    reference_id = Column(String, index=True)  # goal_id, process_id, or date
    measurement_date = Column(Date, nullable=False, index=True)
    
    # Core Metrics (as specified in requirements)
    execution_accuracy = Column(Float)  # Planned vs Actual steps ratio
    time_deviation = Column(Float)  # Planned vs Actual time ratio
    quality_compliance = Column(Float)  # Met quality criteria ratio
    process_efficiency = Column(Float)  # Output/Effort ratio
    
    # Raw data for calculations
    raw_data = Column(JSON)  # Store detailed breakdown
    
    # Analysis
    analysis_summary = Column(Text)
    issues_detected = Column(JSON)  # List of detected issues
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InspectionModel(Base):
    """Inspection database model - individual quality checks."""
    __tablename__ = "inspections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # What was inspected
    target_type = Column(String(50))  # 'step', 'process', 'goal'
    target_id = Column(String, index=True)
    inspection_date = Column(Date, nullable=False)
    
    # Inspection results
    quality_score = Column(Float)  # 0.0 - 1.0
    compliance_score = Column(Float)  # 0.0 - 1.0
    
    # Findings
    findings = Column(JSON)  # List of findings
    waste_identified = Column(JSON)  # Types of waste found
    errors_detected = Column(JSON)  # Errors found
    
    # Recommendations (not motivational - process-focused)
    recommendations = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
