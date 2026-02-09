from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.modules.process_design.models import ProcessModel, ProcessStepModel, ProcessStatus
from app.modules.process_design.schemas import ProcessCreate, ProcessUpdate, ProcessStepCreate, ProcessStepUpdate
from app.modules.inputs.models import GoalModel


async def get_processes_by_goal(db: AsyncSession, goal_id: str) -> List[ProcessModel]:
    """Get all processes for a goal."""
    result = await db.execute(
        select(ProcessModel)
        .where(ProcessModel.goal_id == goal_id)
        .options(selectinload(ProcessModel.steps))
        .order_by(ProcessModel.sequence_order)
    )
    return result.scalars().all()


async def get_all_processes_for_user(db: AsyncSession, user_id: str) -> List[ProcessModel]:
    """Get all processes for a user across all their goals."""
    result = await db.execute(
        select(ProcessModel)
        .join(GoalModel, ProcessModel.goal_id == GoalModel.id, isouter=True)
        .where(
            (GoalModel.user_id == user_id) | (ProcessModel.goal_id == None)
        )
        .options(selectinload(ProcessModel.steps))
        .order_by(ProcessModel.created_at.desc())
    )
    return result.scalars().all()


async def get_process_by_id(db: AsyncSession, process_id: str) -> Optional[ProcessModel]:
    """Get a specific process by ID."""
    result = await db.execute(
        select(ProcessModel)
        .where(ProcessModel.id == process_id)
        .options(selectinload(ProcessModel.steps))
    )
    return result.scalar_one_or_none()


async def create_process(db: AsyncSession, goal_id: Optional[str], process_data: ProcessCreate) -> ProcessModel:
    """Create a new process with steps."""
    # Use goal_id from parameter if provided, otherwise from process_data
    actual_goal_id = goal_id if goal_id is not None else process_data.goal_id
    
    process = ProcessModel(
        goal_id=actual_goal_id,
        name=process_data.name,
        description=process_data.description,
        purpose=process_data.purpose,
        sequence_order=process_data.sequence_order,
        status=ProcessStatus.DRAFT
    )
    db.add(process)
    await db.flush()
    
    # Add steps
    for step_data in process_data.steps or []:
        step = ProcessStepModel(
            process_id=process.id,
            name=step_data.name,
            description=step_data.description,
            action_verb=step_data.action_verb,
            sequence_order=step_data.sequence_order,
            frequency=step_data.frequency,
            estimated_duration_minutes=step_data.estimated_duration_minutes,
            quality_criteria=step_data.quality_criteria,
            expected_output=step_data.expected_output
        )
        db.add(step)
    
    await db.flush()
    
    # Re-fetch with steps loaded to avoid lazy loading issues
    result = await db.execute(
        select(ProcessModel)
        .where(ProcessModel.id == process.id)
        .options(selectinload(ProcessModel.steps))
    )
    return result.scalar_one()


async def update_process(db: AsyncSession, process: ProcessModel, process_data: ProcessUpdate) -> ProcessModel:
    """Update an existing process."""
    update_data = process_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(process, field, value)
    await db.flush()
    await db.refresh(process)
    return process


async def delete_process(db: AsyncSession, process: ProcessModel) -> None:
    """Delete a process."""
    await db.delete(process)
    await db.flush()


async def add_step_to_process(db: AsyncSession, process_id: str, step_data: ProcessStepCreate) -> ProcessStepModel:
    """Add a step to a process."""
    step = ProcessStepModel(
        process_id=process_id,
        name=step_data.name,
        description=step_data.description,
        action_verb=step_data.action_verb,
        sequence_order=step_data.sequence_order,
        frequency=step_data.frequency,
        estimated_duration_minutes=step_data.estimated_duration_minutes,
        quality_criteria=step_data.quality_criteria,
        expected_output=step_data.expected_output
    )
    db.add(step)
    await db.flush()
    await db.refresh(step)
    return step


async def get_step_by_id(db: AsyncSession, step_id: str) -> Optional[ProcessStepModel]:
    """Get a step by ID."""
    result = await db.execute(
        select(ProcessStepModel).where(ProcessStepModel.id == step_id)
    )
    return result.scalar_one_or_none()


async def update_step(db: AsyncSession, step: ProcessStepModel, step_data: ProcessStepUpdate) -> ProcessStepModel:
    """Update a step."""
    update_data = step_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(step, field, value)
    await db.flush()
    await db.refresh(step)
    return step


async def delete_step(db: AsyncSession, step: ProcessStepModel) -> None:
    """Delete a step."""
    await db.delete(step)
    await db.flush()


async def get_active_steps_for_today(db: AsyncSession, user_id: str) -> List[ProcessStepModel]:
    """Get all active daily steps for a user."""
    result = await db.execute(
        select(ProcessStepModel)
        .join(ProcessModel)
        .join(GoalModel)
        .where(
            GoalModel.user_id == user_id,
            ProcessStepModel.is_active == True,
            ProcessModel.status == ProcessStatus.ACTIVE
        )
        .order_by(ProcessStepModel.sequence_order)
    )
    return result.scalars().all()
