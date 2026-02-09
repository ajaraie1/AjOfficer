from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class DeviationType(str, Enum):
    """Deviation type enum."""
    TIME = "time"
    QUALITY = "quality"
    PROCESS = "process"
    SKIP = "skip"
    EXTERNAL = "external"


# Deviation Schemas
class DeviationBase(BaseModel):
    """Base deviation schema."""
    deviation_type: DeviationType
    description: str
    impact_level: Optional[float] = None
    root_cause: Optional[str] = None


class DeviationCreate(DeviationBase):
    """Schema for creating a deviation."""
    pass


class Deviation(DeviationBase):
    """Deviation response schema."""
    id: str
    daily_log_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Daily Log Schemas
class DailyLogBase(BaseModel):
    """Base daily log schema."""
    execution_date: date
    planned_start: Optional[datetime] = None


class DailyLogCreate(DailyLogBase):
    """Schema for creating a daily log."""
    step_id: str


class DailyLogStart(BaseModel):
    """Schema for starting execution."""
    actual_start: datetime


class DailyLogComplete(BaseModel):
    """Schema for completing execution."""
    actual_end: datetime
    actual_execution: str
    output_produced: Optional[str] = None
    quality_score: Optional[float] = None  # 0.0 - 1.0
    quality_notes: Optional[str] = None


class DailyLogUpdate(BaseModel):
    """Schema for updating a daily log."""
    status: Optional[ExecutionStatus] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_execution: Optional[str] = None
    output_produced: Optional[str] = None
    quality_score: Optional[float] = None
    quality_notes: Optional[str] = None


class DailyLog(DailyLogBase):
    """Daily log response schema."""
    id: str
    step_id: str
    user_id: str
    status: ExecutionStatus
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_execution: Optional[str] = None
    output_produced: Optional[str] = None
    quality_score: Optional[float] = None
    quality_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deviations: List[Deviation] = []
    
    class Config:
        from_attributes = True


class DailyLogWithStep(DailyLog):
    """Daily log with step information."""
    step_name: Optional[str] = None
    step_quality_criteria: Optional[str] = None
    process_name: Optional[str] = None
    goal_title: Optional[str] = None
