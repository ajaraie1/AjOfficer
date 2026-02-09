from sqlalchemy import Column, String, DateTime, Text, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class GoalStatus(str, enum.Enum):
    """Goal status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalModel(Base):
    """Goal database model - represents a strategic goal."""
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Core attributes
    title = Column(String(255), nullable=False)
    description = Column(Text)
    purpose = Column(Text, nullable=False)  # WHY - the deep reason
    
    # Timeframe
    start_date = Column(DateTime(timezone=True))
    target_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(Enum(GoalStatus), default=GoalStatus.DRAFT)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resources = relationship("ResourceModel", back_populates="goal", cascade="all, delete-orphan")
    processes = relationship("ProcessModel", back_populates="goal", cascade="all, delete-orphan")


class ResourceType(str, enum.Enum):
    """Resource type enum."""
    TIME = "time"
    EFFORT = "effort"
    MONEY = "money"
    TOOL = "tool"
    OTHER = "other"


class ResourceModel(Base):
    """Resource database model - represents allocated resources for a goal."""
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String, ForeignKey("goals.id"), nullable=False, index=True)
    
    resource_type = Column(Enum(ResourceType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    quantity = Column(Float)
    unit = Column(String(50))  # hours, dollars, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    goal = relationship("GoalModel", back_populates="resources")
