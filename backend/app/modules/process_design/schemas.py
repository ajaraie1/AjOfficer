from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ProcessStatus(str, Enum):
    """Process status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class StepFrequency(str, Enum):
    """Step frequency enum."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


# Process Step Schemas
class ProcessStepBase(BaseModel):
    """Base process step schema."""
    name: str
    description: Optional[str] = None
    action_verb: Optional[str] = None
    sequence_order: int = 0
    frequency: StepFrequency = StepFrequency.DAILY
    estimated_duration_minutes: Optional[int] = None
    quality_criteria: Optional[str] = None
    expected_output: Optional[str] = None


class ProcessStepCreate(ProcessStepBase):
    """Schema for creating a process step."""
    pass


class ProcessStepUpdate(BaseModel):
    """Schema for updating a process step."""
    name: Optional[str] = None
    description: Optional[str] = None
    action_verb: Optional[str] = None
    sequence_order: Optional[int] = None
    frequency: Optional[StepFrequency] = None
    estimated_duration_minutes: Optional[int] = None
    quality_criteria: Optional[str] = None
    expected_output: Optional[str] = None
    is_active: Optional[bool] = None


class ProcessStep(ProcessStepBase):
    """Process step response schema."""
    id: str
    process_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Process Schemas
class ProcessBase(BaseModel):
    """Base process schema."""
    name: str
    description: Optional[str] = None
    purpose: Optional[str] = None
    sequence_order: int = 0


class ProcessCreate(ProcessBase):
    """Schema for creating a process."""
    goal_id: Optional[str] = None
    steps: Optional[List[ProcessStepCreate]] = []


class ProcessUpdate(BaseModel):
    """Schema for updating a process."""
    name: Optional[str] = None
    description: Optional[str] = None
    purpose: Optional[str] = None
    sequence_order: Optional[int] = None
    status: Optional[ProcessStatus] = None


class Process(ProcessBase):
    """Process response schema."""
    id: str
    goal_id: Optional[str] = None
    status: ProcessStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    steps: List[ProcessStep] = []
    
    class Config:
        from_attributes = True


class ProcessWithMetrics(Process):
    """Process with execution metrics included."""
    completion_rate: float = 0.0
    average_quality_score: float = 0.0
