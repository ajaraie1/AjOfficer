from sqlalchemy import Column, String, DateTime, Text, Float, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class ExecutionStatus(str, enum.Enum):
    """Execution status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class DailyLogModel(Base):
    """Daily Log database model - represents daily step execution."""
    __tablename__ = "daily_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    step_id = Column(String, ForeignKey("process_steps.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Execution date
    execution_date = Column(Date, nullable=False, index=True)
    
    # Timing
    planned_start = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Execution details
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    actual_execution = Column(Text)  # What was actually done
    output_produced = Column(Text)  # What was the output
    
    # Quality self-assessment (0.0 - 1.0)
    quality_score = Column(Float)
    quality_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    step = relationship("ProcessStepModel", back_populates="daily_logs")
    deviations = relationship("DeviationModel", back_populates="daily_log", cascade="all, delete-orphan")


class DeviationType(str, enum.Enum):
    """Deviation type enum."""
    TIME = "time"  # Time deviation
    QUALITY = "quality"  # Quality deviation
    PROCESS = "process"  # Process deviation (did something different)
    SKIP = "skip"  # Skipped entirely
    EXTERNAL = "external"  # External factor


class DeviationModel(Base):
    """Deviation database model - records deviations from planned execution."""
    __tablename__ = "deviations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    daily_log_id = Column(String, ForeignKey("daily_logs.id"), nullable=False, index=True)
    
    deviation_type = Column(Enum(DeviationType), nullable=False)
    description = Column(Text, nullable=False)
    
    # Impact assessment
    impact_level = Column(Float)  # 0.0 (minor) to 1.0 (critical)
    root_cause = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    daily_log = relationship("DailyLogModel", back_populates="deviations")
