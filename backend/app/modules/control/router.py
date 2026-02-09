from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.modules.control.schemas import (
    Improvement, ImprovementCreate, ImprovementUpdate,
    ControlAction, ControlActionCreate, ControlActionUpdate
)
from app.modules.control import service

router = APIRouter()


@router.get("/improvements", response_model=List[Improvement])
async def list_improvements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all improvement suggestions."""
    improvements = await service.get_improvements_by_user(db, user_id)
    return improvements


@router.post("/improvements", response_model=Improvement, status_code=status.HTTP_201_CREATED)
async def create_improvement(
    improvement_data: ImprovementCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new improvement suggestion."""
    improvement = await service.create_improvement(db, user_id, improvement_data)
    return improvement


@router.get("/improvements/{improvement_id}", response_model=Improvement)
async def get_improvement(
    improvement_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific improvement."""
    improvement = await service.get_improvement_by_id(db, improvement_id, user_id)
    if not improvement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Improvement not found")
    return improvement


@router.patch("/improvements/{improvement_id}", response_model=Improvement)
async def update_improvement(
    improvement_id: str,
    update_data: ImprovementUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update an improvement (approve, implement, reject)."""
    improvement = await service.get_improvement_by_id(db, improvement_id, user_id)
    if not improvement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Improvement not found")
    updated = await service.update_improvement(db, improvement, update_data)
    return updated


@router.post("/actions", response_model=ControlAction, status_code=status.HTTP_201_CREATED)
async def create_control_action(
    action_data: ControlActionCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Record a control action."""
    action = await service.create_control_action(db, user_id, action_data)
    return action


@router.get("/actions", response_model=List[ControlAction])
async def list_control_actions(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all control actions."""
    actions = await service.get_control_actions(db, user_id)
    return actions


@router.get("/analyze")
async def analyze_and_suggest(
    target_date: date = Query(..., description="Date to analyze"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Analyze execution data and get improvement suggestions.
    
    This endpoint implements the control logic:
    - Does NOT increase pressure
    - Does NOT add more tasks
    - Does NOT blame the user
    
    Instead suggests:
    - Process modifications
    - Procedure redesigns
    - Waste removal
    - Method improvements
    """
    suggestions = await service.analyze_and_suggest_improvements(db, user_id, target_date)
    return {
        "date": target_date,
        "suggestions": suggestions,
        "count": len(suggestions),
        "note": "Focused on reducing effort and improving method, not adding pressure"
    }
