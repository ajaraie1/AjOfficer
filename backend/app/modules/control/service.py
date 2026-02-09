from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

from app.modules.control.models import ImprovementModel, ControlActionModel, ImprovementType, ImprovementStatus
from app.modules.control.schemas import ImprovementCreate, ImprovementUpdate, ControlActionCreate, ControlActionUpdate
from app.modules.measurement.service import calculate_daily_metrics, detect_issues


async def get_improvements_by_user(db: AsyncSession, user_id: str) -> List[ImprovementModel]:
    """Get all improvements for a user."""
    result = await db.execute(
        select(ImprovementModel)
        .where(ImprovementModel.user_id == user_id)
        .order_by(ImprovementModel.created_at.desc())
    )
    return result.scalars().all()


async def get_improvement_by_id(db: AsyncSession, improvement_id: str, user_id: str) -> Optional[ImprovementModel]:
    """Get a specific improvement."""
    result = await db.execute(
        select(ImprovementModel)
        .where(ImprovementModel.id == improvement_id, ImprovementModel.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_improvement(db: AsyncSession, user_id: str, improvement_data: ImprovementCreate) -> ImprovementModel:
    """Create a new improvement suggestion."""
    improvement = ImprovementModel(
        user_id=user_id,
        target_type=improvement_data.target_type,
        target_id=improvement_data.target_id,
        improvement_type=improvement_data.improvement_type,
        title=improvement_data.title,
        description=improvement_data.description,
        rationale=improvement_data.rationale,
        expected_time_savings=improvement_data.expected_time_savings,
        expected_quality_improvement=improvement_data.expected_quality_improvement,
        expected_effort_reduction=improvement_data.expected_effort_reduction,
        status=ImprovementStatus.PROPOSED
    )
    db.add(improvement)
    await db.flush()
    await db.refresh(improvement)
    return improvement


async def update_improvement(db: AsyncSession, improvement: ImprovementModel, update_data: ImprovementUpdate) -> ImprovementModel:
    """Update an improvement."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(improvement, field, value)
    
    if update_data.status == ImprovementStatus.IMPLEMENTED:
        improvement.implemented_at = datetime.utcnow()
    
    await db.flush()
    await db.refresh(improvement)
    return improvement


async def create_control_action(db: AsyncSession, user_id: str, action_data: ControlActionCreate) -> ControlActionModel:
    """Record a control action."""
    action = ControlActionModel(
        user_id=user_id,
        trigger_type=action_data.trigger_type,
        trigger_description=action_data.trigger_description,
        action_type=action_data.action_type,
        action_description=action_data.action_description,
        target_type=action_data.target_type,
        target_id=action_data.target_id,
        improvement_id=action_data.improvement_id
    )
    db.add(action)
    await db.flush()
    await db.refresh(action)
    return action


async def get_control_actions(db: AsyncSession, user_id: str) -> List[ControlActionModel]:
    """Get all control actions for a user."""
    result = await db.execute(
        select(ControlActionModel)
        .where(ControlActionModel.user_id == user_id)
        .order_by(ControlActionModel.created_at.desc())
    )
    return result.scalars().all()


async def analyze_and_suggest_improvements(
    db: AsyncSession, 
    user_id: str, 
    target_date: date
) -> List[Dict[str, Any]]:
    """Analyze data and suggest improvements based on control logic.
    
    Control Logic (from requirements):
    - Does NOT increase pressure
    - Does NOT add more tasks
    - Does NOT blame the user
    
    Instead:
    - Modifies the process
    - Redesigns the procedure
    - Removes waste
    - Improves the method
    """
    suggestions = []
    
    # Get metrics and issues
    metrics = await calculate_daily_metrics(db, user_id, target_date)
    issues = await detect_issues(db, user_id, target_date)
    
    # Low quality → Suggest simplification or better criteria
    if metrics["quality_compliance"] < 0.6:
        suggestions.append({
            "improvement_type": ImprovementType.SIMPLIFY,
            "title": "Simplify Quality Criteria",
            "description": "Quality compliance is low. Consider simplifying the quality criteria or breaking steps into smaller, more achievable parts.",
            "rationale": f"Current quality compliance: {metrics['quality_compliance']:.1%}",
            "expected_quality_improvement": 0.2
        })
    
    # Time overruns → Suggest splitting or removing steps
    if metrics["time_deviation"] > 1.5:
        suggestions.append({
            "improvement_type": ImprovementType.SPLIT,
            "title": "Reduce Step Complexity",
            "description": "Steps are taking significantly longer than planned. Consider splitting complex steps into smaller ones or removing non-essential parts.",
            "rationale": f"Time deviation: {metrics['time_deviation']:.1%}",
            "expected_time_savings": 30
        })
    
    # Low execution accuracy → Suggest process redesign
    if metrics["execution_accuracy"] < 0.5:
        suggestions.append({
            "improvement_type": ImprovementType.REMOVE,
            "title": "Remove Unnecessary Steps",
            "description": "Many steps are not being completed. Review which steps are truly essential and remove or defer those that aren't adding value.",
            "rationale": f"Execution accuracy: {metrics['execution_accuracy']:.1%}",
            "expected_effort_reduction": 0.3
        })
    
    # Repeated skips → Investigate and suggest removal
    skip_issues = [i for i in issues if i["type"] == "skipped"]
    if len(skip_issues) >= 2:
        suggestions.append({
            "improvement_type": ImprovementType.REMOVE,
            "title": "Review Frequently Skipped Steps",
            "description": "Multiple steps are being skipped. This may indicate the process has unnecessary steps or unrealistic expectations. Consider removing or rescheduling these steps.",
            "rationale": f"{len(skip_issues)} steps skipped",
            "expected_effort_reduction": 0.2
        })
    
    return suggestions
