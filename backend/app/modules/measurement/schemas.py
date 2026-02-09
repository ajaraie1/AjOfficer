from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


class MeasurementType(str, Enum):
    """Measurement type enum."""
    DAILY = "daily"
    WEEKLY = "weekly"
    PROCESS = "process"
    GOAL = "goal"


# Measurement Schemas
class MeasurementBase(BaseModel):
    """Base measurement schema."""
    measurement_type: MeasurementType
    measurement_date: date


class MeasurementCreate(MeasurementBase):
    """Schema for creating a measurement."""
    reference_id: Optional[str] = None


class Measurement(MeasurementBase):
    """Measurement response schema."""
    id: str
    user_id: str
    reference_id: Optional[str] = None
    
    # Core Metrics
    execution_accuracy: Optional[float] = None
    time_deviation: Optional[float] = None
    quality_compliance: Optional[float] = None
    process_efficiency: Optional[float] = None
    
    raw_data: Optional[Dict[str, Any]] = None
    analysis_summary: Optional[str] = None
    issues_detected: Optional[List[Dict[str, Any]]] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inspection Schemas
class InspectionBase(BaseModel):
    """Base inspection schema."""
    target_type: str
    target_id: str
    inspection_date: date


class InspectionCreate(InspectionBase):
    """Schema for creating an inspection."""
    pass


class Inspection(InspectionBase):
    """Inspection response schema."""
    id: str
    user_id: str
    
    quality_score: Optional[float] = None
    compliance_score: Optional[float] = None
    
    findings: Optional[List[Dict[str, Any]]] = None
    waste_identified: Optional[List[Dict[str, Any]]] = None
    errors_detected: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard Summary Schemas
class DailyMetrics(BaseModel):
    """Daily metrics summary."""
    date: date
    total_steps: int
    completed_steps: int
    completion_rate: float
    average_quality: float
    total_deviations: int
    time_deviation_avg: float


class ProcessMetrics(BaseModel):
    """Process-level metrics."""
    process_id: str
    process_name: str
    execution_accuracy: float
    quality_compliance: float
    efficiency_score: float
    issues_count: int


class MetricsSummary(BaseModel):
    """Overall metrics summary."""
    period_start: date
    period_end: date
    overall_execution_accuracy: float
    overall_quality_compliance: float
    overall_efficiency: float
    trend: str  # "improving", "stable", "declining"
    key_issues: List[str]
