from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ImprovementType(str, Enum):
    """Improvement type enum."""
    SIMPLIFY = "simplify"
    REMOVE = "remove"
    REORDER = "reorder"
    MERGE = "merge"
    SPLIT = "split"
    REPLACE = "replace"
    AUTOMATE = "automate"


class ImprovementStatus(str, Enum):
    """Improvement status enum."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


# Improvement Schemas
class ImprovementBase(BaseModel):
    """Base improvement schema."""
    target_type: str
    target_id: str
    improvement_type: ImprovementType
    title: str
    description: str
    rationale: Optional[str] = None


class ImprovementCreate(ImprovementBase):
    """Schema for creating an improvement."""
    expected_time_savings: Optional[float] = None
    expected_quality_improvement: Optional[float] = None
    expected_effort_reduction: Optional[float] = None


class ImprovementUpdate(BaseModel):
    """Schema for updating an improvement."""
    status: Optional[ImprovementStatus] = None
    implementation_notes: Optional[str] = None


class Improvement(ImprovementBase):
    """Improvement response schema."""
    id: str
    user_id: str
    status: ImprovementStatus
    expected_time_savings: Optional[float] = None
    expected_quality_improvement: Optional[float] = None
    expected_effort_reduction: Optional[float] = None
    trigger_data: Optional[Dict[str, Any]] = None
    implemented_at: Optional[datetime] = None
    implementation_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Control Action Schemas
class ControlActionBase(BaseModel):
    """Base control action schema."""
    trigger_type: str
    trigger_description: Optional[str] = None
    action_type: str
    action_description: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None


class ControlActionCreate(ControlActionBase):
    """Schema for creating a control action."""
    improvement_id: Optional[str] = None


class ControlActionUpdate(BaseModel):
    """Schema for updating a control action."""
    outcome_notes: Optional[str] = None
    was_effective: Optional[bool] = None


class ControlAction(ControlActionBase):
    """Control action response schema."""
    id: str
    user_id: str
    improvement_id: Optional[str] = None
    outcome_notes: Optional[str] = None
    was_effective: Optional[bool] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis Response Schemas
class ProcessAnalysis(BaseModel):
    """Process analysis response."""
    process_id: str
    process_name: str
    health_score: float  # 0.0 - 1.0
    issues: List[Dict[str, Any]]
    suggested_improvements: List[Improvement]


class ControlRecommendation(BaseModel):
    """Control system recommendation."""
    trigger: str
    severity: str  # 'low', 'medium', 'high'
    recommendation: str
    action_type: str
    expected_impact: str
