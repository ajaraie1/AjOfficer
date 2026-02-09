from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class GoalStatus(str, Enum):
    """Goal status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ResourceType(str, Enum):
    """Resource type enum."""
    TIME = "time"
    EFFORT = "effort"
    MONEY = "money"
    TOOL = "tool"
    OTHER = "other"


# Resource Schemas
class ResourceBase(BaseModel):
    """Base resource schema."""
    resource_type: ResourceType
    name: str
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None


class ResourceCreate(ResourceBase):
    """Schema for creating a resource."""
    pass


class Resource(ResourceBase):
    """Resource response schema."""
    id: str
    goal_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Goal Schemas
class GoalBase(BaseModel):
    """Base goal schema."""
    title: str
    description: Optional[str] = None
    purpose: str  # WHY - mandatory
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Schema for creating a goal."""
    resources: Optional[List[ResourceCreate]] = []


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    title: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None


class Goal(GoalBase):
    """Goal response schema."""
    id: str
    user_id: str
    status: GoalStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    resources: List[Resource] = []
    
    class Config:
        from_attributes = True


class GoalWithProcesses(Goal):
    """Goal with processes included."""
    process_count: int = 0
