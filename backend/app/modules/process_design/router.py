from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.modules.process_design.schemas import (
    Process, ProcessCreate, ProcessUpdate,
    ProcessStep, ProcessStepCreate, ProcessStepUpdate
)
from app.modules.process_design import service
from app.modules.inputs.service import get_goal_by_id

router = APIRouter()


@router.get("", response_model=List[Process])
async def list_all_processes(
    goal_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all processes, optionally filtered by goal_id."""
    if goal_id:
        processes = await service.get_processes_by_goal(db, goal_id)
    else:
        processes = await service.get_all_processes_for_user(db, user_id)
    return processes


@router.post("", response_model=Process, status_code=status.HTTP_201_CREATED)
async def create_new_process(
    process_data: ProcessCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new process (optionally linked to a goal via process_data.goal_id)."""
    goal_id = getattr(process_data, 'goal_id', None)
    if goal_id:
        goal = await get_goal_by_id(db, goal_id, user_id)
        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    process = await service.create_process(db, goal_id, process_data)
    return process


@router.get("/goals/{goal_id}/processes", response_model=List[Process])
async def list_processes(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all processes for a goal."""
    # Verify goal ownership
    goal = await get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    processes = await service.get_processes_by_goal(db, goal_id)
    return processes


@router.post("/goals/{goal_id}/processes", response_model=Process, status_code=status.HTTP_201_CREATED)
async def create_process(
    goal_id: str,
    process_data: ProcessCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new process for a goal."""
    goal = await get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    process = await service.create_process(db, goal_id, process_data)
    return process


@router.get("/{process_id}", response_model=Process)
async def get_process(
    process_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific process."""
    process = await service.get_process_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    return process


@router.patch("/{process_id}", response_model=Process)
async def update_process(
    process_id: str,
    process_data: ProcessUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a process."""
    process = await service.get_process_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    updated_process = await service.update_process(db, process, process_data)
    return updated_process


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(
    process_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a process."""
    process = await service.get_process_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    await service.delete_process(db, process)


# Step endpoints
@router.post("/{process_id}/steps", response_model=ProcessStep, status_code=status.HTTP_201_CREATED)
async def add_step(
    process_id: str,
    step_data: ProcessStepCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add a step to a process."""
    process = await service.get_process_by_id(db, process_id)
    if not process:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Process not found")
    step = await service.add_step_to_process(db, process_id, step_data)
    return step


@router.patch("/steps/{step_id}", response_model=ProcessStep)
async def update_step(
    step_id: str,
    step_data: ProcessStepUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a step."""
    step = await service.get_step_by_id(db, step_id)
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step not found")
    updated_step = await service.update_step(db, step, step_data)
    return updated_step


@router.delete("/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_step(
    step_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a step."""
    step = await service.get_step_by_id(db, step_id)
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Step not found")
    await service.delete_step(db, step)


@router.get("/today/steps", response_model=List[ProcessStep])
async def get_today_steps(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all active steps for today."""
    steps = await service.get_active_steps_for_today(db, user_id)
    return steps
