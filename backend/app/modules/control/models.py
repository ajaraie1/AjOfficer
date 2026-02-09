from sqlalchemy import Column, String, DateTime, Text, Float, Enum, ForeignKey, Date, JSON, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class ImprovementType(str, enum.Enum):
    """Improvement type enum."""
    SIMPLIFY = "simplify"  # Make step simpler
    REMOVE = "remove"  # Remove waste/redundancy
    REORDER = "reorder"  # Change sequence
    MERGE = "merge"  # Combine steps
    SPLIT = "split"  # Divide into smaller steps
    REPLACE = "replace"  # Replace with better approach
    AUTOMATE = "automate"  # Suggest automation


class ImprovementStatus(str, enum.Enum):
    """Improvement status enum."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class ImprovementModel(Base):
    """Improvement database model - suggested process improvements."""
    __tablename__ = "improvements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Target
    target_type = Column(String(50), nullable=False)  # 'step', 'process', 'goal'
    target_id = Column(String, nullable=False, index=True)
    
    # Improvement details
    improvement_type = Column(Enum(ImprovementType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text)  # Why this improvement is suggested
    
    # Expected impact
    expected_time_savings = Column(Float)  # In minutes
    expected_quality_improvement = Column(Float)  # 0.0 - 1.0
    expected_effort_reduction = Column(Float)  # 0.0 - 1.0
    
    # Data that triggered this suggestion
    trigger_data = Column(JSON)
    
    # Status
    status = Column(Enum(ImprovementStatus), default=ImprovementStatus.PROPOSED)
    
    # Implementation tracking
    implemented_at = Column(DateTime(timezone=True))
    implementation_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ControlActionModel(Base):
    """Control Action database model - records control decisions."""
    __tablename__ = "control_actions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # What triggered the action
    trigger_type = Column(String(50))  # 'quality', 'time', 'fatigue', 'pattern'
    trigger_description = Column(Text)
    
    # The action taken
    action_type = Column(String(50))  # 'modify', 'pause', 'reengineer', 'remove'
    action_description = Column(Text, nullable=False)
    
    # Target
    target_type = Column(String(50))
    target_id = Column(String)
    
    # Related improvement if any
    improvement_id = Column(String, ForeignKey("improvements.id"))
    
    # Outcome
    outcome_notes = Column(Text)
    was_effective = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
