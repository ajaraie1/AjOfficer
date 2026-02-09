from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime

from app.modules.daily_operations.models import DailyLogModel, DeviationModel, ExecutionStatus
from app.modules.daily_operations.schemas import (
    DailyLogCreate, DailyLogUpdate, DailyLogStart, DailyLogComplete, DeviationCreate
)


async def get_logs_by_date(db: AsyncSession, user_id: str, execution_date: date) -> List[DailyLogModel]:
    """Get all daily logs for a user on a specific date."""
    result = await db.execute(
        select(DailyLogModel)
        .where(
            DailyLogModel.user_id == user_id,
            DailyLogModel.execution_date == execution_date
        )
        .options(selectinload(DailyLogModel.deviations))
        .order_by(DailyLogModel.created_at)
    )
    return result.scalars().all()


async def get_log_by_id(db: AsyncSession, log_id: str, user_id: str) -> Optional[DailyLogModel]:
    """Get a specific daily log by ID."""
    result = await db.execute(
        select(DailyLogModel)
        .where(DailyLogModel.id == log_id, DailyLogModel.user_id == user_id)
        .options(selectinload(DailyLogModel.deviations))
    )
    return result.scalar_one_or_none()


async def create_daily_log(db: AsyncSession, user_id: str, log_data: DailyLogCreate) -> DailyLogModel:
    """Create a new daily log entry."""
    log = DailyLogModel(
        step_id=log_data.step_id,
        user_id=user_id,
        execution_date=log_data.execution_date,
        planned_start=log_data.planned_start,
        status=ExecutionStatus.PENDING
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def start_execution(db: AsyncSession, log: DailyLogModel, start_data: DailyLogStart) -> DailyLogModel:
    """Mark a log as started."""
    log.status = ExecutionStatus.IN_PROGRESS
    log.actual_start = start_data.actual_start
    await db.flush()
    await db.refresh(log)
    return log


async def complete_execution(db: AsyncSession, log: DailyLogModel, complete_data: DailyLogComplete) -> DailyLogModel:
    """Mark a log as completed with details."""
    log.status = ExecutionStatus.COMPLETED
    log.actual_end = complete_data.actual_end
    log.actual_execution = complete_data.actual_execution
    log.output_produced = complete_data.output_produced
    log.quality_score = complete_data.quality_score
    log.quality_notes = complete_data.quality_notes
    await db.flush()
    await db.refresh(log)
    return log


async def update_daily_log(db: AsyncSession, log: DailyLogModel, log_data: DailyLogUpdate) -> DailyLogModel:
    """Update a daily log."""
    update_data = log_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)
    await db.flush()
    await db.refresh(log)
    return log


async def add_deviation(db: AsyncSession, log_id: str, deviation_data: DeviationCreate) -> DeviationModel:
    """Add a deviation to a daily log."""
    deviation = DeviationModel(
        daily_log_id=log_id,
        deviation_type=deviation_data.deviation_type,
        description=deviation_data.description,
        impact_level=deviation_data.impact_level,
        root_cause=deviation_data.root_cause
    )
    db.add(deviation)
    await db.flush()
    await db.refresh(deviation)
    return deviation


async def get_logs_in_range(
    db: AsyncSession, 
    user_id: str, 
    start_date: date, 
    end_date: date
) -> List[DailyLogModel]:
    """Get all logs in a date range."""
    result = await db.execute(
        select(DailyLogModel)
        .where(
            DailyLogModel.user_id == user_id,
            DailyLogModel.execution_date >= start_date,
            DailyLogModel.execution_date <= end_date
        )
        .options(selectinload(DailyLogModel.deviations))
        .order_by(DailyLogModel.execution_date, DailyLogModel.created_at)
    )
    return result.scalars().all()
