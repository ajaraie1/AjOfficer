from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.modules.inputs.schemas import Goal, GoalCreate, GoalUpdate, Resource, ResourceCreate
from app.modules.inputs import service

router = APIRouter()


@router.get("/goals", response_model=List[Goal])
async def list_goals(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all goals for current user."""
    goals = await service.get_goals_by_user(db, user_id)
    return goals


@router.post("/goals", response_model=Goal, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new goal with purpose and resources."""
    goal = await service.create_goal(db, user_id, goal_data)
    return goal


@router.get("/goals/{goal_id}", response_model=Goal)
async def get_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific goal."""
    goal = await service.get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.patch("/goals/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a goal."""
    goal = await service.get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    updated_goal = await service.update_goal(db, goal, goal_data)
    return updated_goal


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a goal."""
    goal = await service.get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    await service.delete_goal(db, goal)


@router.post("/goals/{goal_id}/resources", response_model=Resource, status_code=status.HTTP_201_CREATED)
async def add_resource(
    goal_id: str,
    resource_data: ResourceCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add a resource to a goal."""
    goal = await service.get_goal_by_id(db, goal_id, user_id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    resource = await service.add_resource_to_goal(db, goal_id, resource_data)
    return resource
