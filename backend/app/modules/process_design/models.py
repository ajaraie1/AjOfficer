from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class ProcessStatus(str, enum.Enum):
    """Process status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class ProcessModel(Base):
    """Process database model - represents a designed process for a goal."""
    __tablename__ = "processes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    purpose = Column(Text)  # Why this process matters for the goal
    sequence_order = Column(Integer, default=0)  # Order in which processes should be executed
    
    status = Column(Enum(ProcessStatus), default=ProcessStatus.DRAFT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    goal = relationship("GoalModel", back_populates="processes")
    steps = relationship("ProcessStepModel", back_populates="process", cascade="all, delete-orphan")


class StepFrequency(str, enum.Enum):
    """Step frequency enum."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class ProcessStepModel(Base):
    """Process Step database model - represents a daily step with quality criteria."""
    __tablename__ = "process_steps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    process_id = Column(String, ForeignKey("processes.id"), nullable=False, index=True)
    
    # Step details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    action_verb = Column(String(50))  # e.g., "Write", "Review", "Create"
    
    # Execution details
    sequence_order = Column(Integer, default=0)
    frequency = Column(Enum(StepFrequency), default=StepFrequency.DAILY)
    estimated_duration_minutes = Column(Integer)
    
    # Quality criteria - essential for measurement
    quality_criteria = Column(Text)  # What defines a quality execution
    expected_output = Column(Text)  # What should be produced
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    process = relationship("ProcessModel", back_populates="steps")
    daily_logs = relationship("DailyLogModel", back_populates="step", cascade="all, delete-orphan")
