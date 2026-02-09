from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import date, timedelta

from app.modules.measurement.models import MeasurementModel, InspectionModel, MeasurementType
from app.modules.daily_operations.models import DailyLogModel, DeviationModel, ExecutionStatus
from app.modules.process_design.models import ProcessStepModel


async def calculate_daily_metrics(db: AsyncSession, user_id: str, target_date: date) -> Dict[str, Any]:
    """Calculate metrics for a specific day."""
    # Get all logs for the day
    result = await db.execute(
        select(DailyLogModel)
        .where(
            DailyLogModel.user_id == user_id,
            DailyLogModel.execution_date == target_date
        )
    )
    logs = result.scalars().all()
    
    if not logs:
        return {
            "total_steps": 0,
            "completed_steps": 0,
            "execution_accuracy": 0.0,
            "time_deviation": 0.0,
            "quality_compliance": 0.0,
            "process_efficiency": 0.0
        }
    
    total_steps = len(logs)
    completed_steps = len([l for l in logs if l.status == ExecutionStatus.COMPLETED])
    
    # Calculate execution accuracy
    execution_accuracy = completed_steps / total_steps if total_steps > 0 else 0.0
    
    # Calculate time deviation
    time_deviations = []
    for log in logs:
        if log.actual_start and log.actual_end and log.planned_start:
            planned_duration = 60  # Default 60 mins if not specified
            actual_duration = (log.actual_end - log.actual_start).total_seconds() / 60
            if planned_duration > 0:
                time_deviations.append(actual_duration / planned_duration)
    
    time_deviation = sum(time_deviations) / len(time_deviations) if time_deviations else 1.0
    
    # Calculate quality compliance
    quality_scores = [l.quality_score for l in logs if l.quality_score is not None]
    quality_compliance = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    # Process efficiency (simplified: completed with good quality / total effort)
    high_quality_completed = len([l for l in logs if l.status == ExecutionStatus.COMPLETED and (l.quality_score or 0) >= 0.7])
    process_efficiency = high_quality_completed / total_steps if total_steps > 0 else 0.0
    
    return {
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "execution_accuracy": execution_accuracy,
        "time_deviation": time_deviation,
        "quality_compliance": quality_compliance,
        "process_efficiency": process_efficiency
    }


async def create_daily_measurement(db: AsyncSession, user_id: str, target_date: date) -> MeasurementModel:
    """Create a daily measurement record."""
    metrics = await calculate_daily_metrics(db, user_id, target_date)
    
    measurement = MeasurementModel(
        user_id=user_id,
        measurement_type=MeasurementType.DAILY,
        measurement_date=target_date,
        execution_accuracy=metrics["execution_accuracy"],
        time_deviation=metrics["time_deviation"],
        quality_compliance=metrics["quality_compliance"],
        process_efficiency=metrics["process_efficiency"],
        raw_data=metrics
    )
    db.add(measurement)
    await db.flush()
    await db.refresh(measurement)
    return measurement


async def get_measurements_in_range(
    db: AsyncSession, 
    user_id: str, 
    start_date: date, 
    end_date: date
) -> List[MeasurementModel]:
    """Get measurements in a date range."""
    result = await db.execute(
        select(MeasurementModel)
        .where(
            MeasurementModel.user_id == user_id,
            MeasurementModel.measurement_date >= start_date,
            MeasurementModel.measurement_date <= end_date
        )
        .order_by(MeasurementModel.measurement_date)
    )
    return result.scalars().all()


async def get_measurement_by_id(db: AsyncSession, measurement_id: str, user_id: str) -> Optional[MeasurementModel]:
    """Get a specific measurement."""
    result = await db.execute(
        select(MeasurementModel)
        .where(MeasurementModel.id == measurement_id, MeasurementModel.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def detect_issues(db: AsyncSession, user_id: str, target_date: date) -> List[Dict[str, Any]]:
    """Detect quality issues from daily logs."""
    result = await db.execute(
        select(DailyLogModel)
        .where(
            DailyLogModel.user_id == user_id,
            DailyLogModel.execution_date == target_date
        )
    )
    logs = result.scalars().all()
    
    issues = []
    
    for log in logs:
        # Low quality
        if log.quality_score is not None and log.quality_score < 0.6:
            issues.append({
                "type": "low_quality",
                "log_id": log.id,
                "step_id": log.step_id,
                "score": log.quality_score,
                "description": "Quality score below acceptable threshold"
            })
        
        # Time overrun
        if log.actual_start and log.actual_end:
            actual_duration = (log.actual_end - log.actual_start).total_seconds() / 60
            if actual_duration > 120:  # More than 2 hours
                issues.append({
                    "type": "time_overrun",
                    "log_id": log.id,
                    "step_id": log.step_id,
                    "duration_minutes": actual_duration,
                    "description": "Step took significantly longer than expected"
                })
        
        # Skipped
        if log.status == ExecutionStatus.SKIPPED:
            issues.append({
                "type": "skipped",
                "log_id": log.id,
                "step_id": log.step_id,
                "description": "Step was skipped - investigate reason"
            })
    
    return issues


async def create_inspection(
    db: AsyncSession, 
    user_id: str, 
    target_type: str, 
    target_id: str, 
    inspection_date: date
) -> InspectionModel:
    """Create an inspection record with analysis."""
    # Get relevant data based on target type
    issues = await detect_issues(db, user_id, inspection_date)
    
    # Calculate scores
    metrics = await calculate_daily_metrics(db, user_id, inspection_date)
    
    inspection = InspectionModel(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        inspection_date=inspection_date,
        quality_score=metrics["quality_compliance"],
        compliance_score=metrics["execution_accuracy"],
        findings=issues,
        waste_identified=[],  # Would be populated by AI
        errors_detected=[i for i in issues if i["type"] in ["low_quality", "skipped"]],
        recommendations=[]  # Would be populated by AI
    )
    db.add(inspection)
    await db.flush()
    await db.refresh(inspection)
    return inspection
