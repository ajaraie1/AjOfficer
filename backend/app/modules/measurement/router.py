from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.modules.measurement.schemas import Measurement, Inspection, DailyMetrics
from app.modules.measurement import service

router = APIRouter()


@router.post("/daily", response_model=Measurement, status_code=status.HTTP_201_CREATED)
async def create_daily_measurement(
    measurement_date: date = Query(..., description="Date to measure"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Calculate and store daily metrics."""
    measurement = await service.create_daily_measurement(db, user_id, measurement_date)
    return measurement


@router.get("/daily/{measurement_date}", response_model=Measurement)
async def get_daily_metrics(
    measurement_date: date,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get metrics for a specific date."""
    metrics = await service.calculate_daily_metrics(db, user_id, measurement_date)
    return {
        "id": "calculated",
        "user_id": user_id,
        "measurement_type": "daily",
        "measurement_date": measurement_date,
        "execution_accuracy": metrics["execution_accuracy"],
        "time_deviation": metrics["time_deviation"],
        "quality_compliance": metrics["quality_compliance"],
        "process_efficiency": metrics["process_efficiency"],
        "raw_data": metrics,
        "created_at": measurement_date
    }


@router.get("/range", response_model=List[Measurement])
async def get_measurements_range(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get measurements in a date range."""
    measurements = await service.get_measurements_in_range(db, user_id, start_date, end_date)
    return measurements


@router.get("/{measurement_id}", response_model=Measurement)
async def get_measurement(
    measurement_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific measurement."""
    measurement = await service.get_measurement_by_id(db, measurement_id, user_id)
    if not measurement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return measurement


@router.post("/inspect", response_model=Inspection, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    target_type: str = Query(..., description="Type: step, process, or goal"),
    target_id: str = Query(..., description="ID of the target"),
    inspection_date: date = Query(..., description="Date to inspect"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create an inspection for a target."""
    inspection = await service.create_inspection(db, user_id, target_type, target_id, inspection_date)
    return inspection


@router.get("/issues/{target_date}")
async def get_issues(
    target_date: date,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get detected issues for a date."""
    issues = await service.detect_issues(db, user_id, target_date)
    return {"date": target_date, "issues": issues, "count": len(issues)}
