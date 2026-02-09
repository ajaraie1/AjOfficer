from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.modules.inputs.models import GoalModel, ResourceModel, GoalStatus
from app.modules.inputs.schemas import GoalCreate, GoalUpdate, ResourceCreate


async def get_goals_by_user(db: AsyncSession, user_id: str) -> List[GoalModel]:
    """Get all goals for a user."""
    result = await db.execute(
        select(GoalModel)
        .where(GoalModel.user_id == user_id)
        .options(selectinload(GoalModel.resources))
        .order_by(GoalModel.created_at.desc())
    )
    return result.scalars().all()


async def get_goal_by_id(db: AsyncSession, goal_id: str, user_id: str) -> Optional[GoalModel]:
    """Get a specific goal by ID."""
    result = await db.execute(
        select(GoalModel)
        .where(GoalModel.id == goal_id, GoalModel.user_id == user_id)
        .options(selectinload(GoalModel.resources))
    )
    return result.scalar_one_or_none()


async def create_goal(db: AsyncSession, user_id: str, goal_data: GoalCreate) -> GoalModel:
    """Create a new goal with resources."""
    goal = GoalModel(
        user_id=user_id,
        title=goal_data.title,
        description=goal_data.description,
        purpose=goal_data.purpose,
        start_date=goal_data.start_date,
        target_date=goal_data.target_date,
        status=GoalStatus.DRAFT
    )
    db.add(goal)
    await db.flush()
    
    # Add resources
    for resource_data in goal_data.resources:
        resource = ResourceModel(
            goal_id=goal.id,
            resource_type=resource_data.resource_type,
            name=resource_data.name,
            description=resource_data.description,
            quantity=resource_data.quantity,
            unit=resource_data.unit
        )
        db.add(resource)
    
    await db.flush()
    
    # Re-fetch with resources loaded to avoid lazy loading issues
    result = await db.execute(
        select(GoalModel)
        .where(GoalModel.id == goal.id)
        .options(selectinload(GoalModel.resources))
    )
    return result.scalar_one()


async def update_goal(db: AsyncSession, goal: GoalModel, goal_data: GoalUpdate) -> GoalModel:
    """Update an existing goal."""
    update_data = goal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    await db.flush()
    await db.refresh(goal)
    return goal


async def delete_goal(db: AsyncSession, goal: GoalModel) -> None:
    """Delete a goal."""
    await db.delete(goal)
    await db.flush()


async def add_resource_to_goal(db: AsyncSession, goal_id: str, resource_data: ResourceCreate) -> ResourceModel:
    """Add a resource to a goal."""
    resource = ResourceModel(
        goal_id=goal_id,
        resource_type=resource_data.resource_type,
        name=resource_data.name,
        description=resource_data.description,
        quantity=resource_data.quantity,
        unit=resource_data.unit
    )
    db.add(resource)
    await db.flush()
    await db.refresh(resource)
    return resource
