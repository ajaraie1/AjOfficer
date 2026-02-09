from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.modules.daily_operations.schemas import (
    DailyLog, DailyLogCreate, DailyLogUpdate, DailyLogStart, DailyLogComplete,
    Deviation, DeviationCreate
)
from app.modules.daily_operations import service

router = APIRouter()


@router.get("/logs", response_model=List[DailyLog])
async def list_logs(
    execution_date: date = Query(..., description="Date to get logs for"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all daily logs for a specific date."""
    # Smart Logic: Generate logs for active steps if they don't exist
    await service.generate_daily_logs(db, user_id, execution_date)
    
    logs = await service.get_logs_by_date(db, user_id, execution_date)
    return logs


@router.get("/logs/range", response_model=List[DailyLog])
async def list_logs_range(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all daily logs in a date range."""
    logs = await service.get_logs_in_range(db, user_id, start_date, end_date)
    return logs


@router.post("/logs", response_model=DailyLog, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: DailyLogCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new daily log entry for a step."""
    log = await service.create_daily_log(db, user_id, log_data)
    return log


@router.get("/logs/{log_id}", response_model=DailyLog)
async def get_log(
    log_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific daily log."""
    log = await service.get_log_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


@router.post("/logs/{log_id}/start", response_model=DailyLog)
async def start_log(
    log_id: str,
    start_data: DailyLogStart,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Mark a log as started."""
    log = await service.get_log_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    updated_log = await service.start_execution(db, log, start_data)
    return updated_log


@router.post("/logs/{log_id}/complete", response_model=DailyLog)
async def complete_log(
    log_id: str,
    complete_data: DailyLogComplete,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark a log as completed with execution details."""
    log = await service.get_log_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    updated_log = await service.complete_execution(db, log, complete_data)
    return updated_log


@router.patch("/logs/{log_id}", response_model=DailyLog)
async def update_log(
    log_id: str,
    log_data: DailyLogUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a daily log."""
    log = await service.get_log_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    updated_log = await service.update_daily_log(db, log, log_data)
    return updated_log


@router.post("/logs/{log_id}/deviations", response_model=Deviation, status_code=status.HTTP_201_CREATED)
async def add_deviation(
    log_id: str,
    deviation_data: DeviationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add a deviation to a daily log."""
    log = await service.get_log_by_id(db, log_id, user_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    deviation = await service.add_deviation(db, log_id, deviation_data)
    return deviation
