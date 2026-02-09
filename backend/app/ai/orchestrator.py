"""AI Orchestrator - Coordinates AI roles for complex operations."""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.service import get_ai_service
from app.modules.inputs.service import get_goal_by_id
from app.modules.process_design.service import create_process
from app.modules.process_design.schemas import ProcessCreate, ProcessStepCreate, StepFrequency
from app.modules.measurement.service import calculate_daily_metrics, detect_issues
from app.modules.control.service import create_improvement
from app.modules.control.schemas import ImprovementCreate


class AIOrchestrator:
    """Orchestrates AI roles for complex multi-step operations."""
    
    def __init__(self):
        self.ai = get_ai_service()
    
    async def auto_design_processes(
        self, 
        db: AsyncSession, 
        user_id: str, 
        goal_id: str
    ) -> Dict[str, Any]:
        """Automatically design processes for a goal using AI Process Engineer."""
        from app.modules.inputs.models import GoalModel
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Get goal with resources
        result = await db.execute(
            select(GoalModel)
            .where(GoalModel.id == goal_id, GoalModel.user_id == user_id)
            .options(selectinload(GoalModel.resources))
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            return {"error": "Goal not found"}
        
        # Prepare goal data for AI
        goal_data = {
            "title": goal.title,
            "description": goal.description,
            "purpose": goal.purpose,
            "start_date": str(goal.start_date) if goal.start_date else None,
            "target_date": str(goal.target_date) if goal.target_date else None,
            "resources": [
                {
                    "name": r.name,
                    "type": r.resource_type.value if r.resource_type else None,
                    "quantity": r.quantity,
                    "unit": r.unit
                }
                for r in goal.resources
            ]
        }
        
        # Get AI-designed processes
        ai_result = await self.ai.design_processes(goal_data)
        
        if "error" in ai_result:
            return ai_result
        
        # Create processes in database
        created_processes = []
        for process_data in ai_result.get("processes", []):
            steps = [
                ProcessStepCreate(
                    name=step.get("name", "Untitled Step"),
                    description=step.get("description"),
                    action_verb=step.get("action_verb"),
                    sequence_order=idx,
                    frequency=StepFrequency.DAILY,
                    estimated_duration_minutes=step.get("estimated_duration_minutes"),
                    quality_criteria=step.get("quality_criteria"),
                    expected_output=step.get("expected_output")
                )
                for idx, step in enumerate(process_data.get("steps", []))
            ]
            
            process_create = ProcessCreate(
                name=process_data.get("name", "Untitled Process"),
                description=process_data.get("description"),
                purpose=process_data.get("purpose"),
                sequence_order=process_data.get("sequence_order", 0),
                steps=steps
            )
            
            process = await create_process(db, goal_id, process_create)
            created_processes.append({
                "id": process.id,
                "name": process.name,
                "steps_count": len(steps)
            })
        
        return {
            "success": True,
            "processes_created": len(created_processes),
            "processes": created_processes
        }
    
    async def full_analysis(
        self, 
        db: AsyncSession, 
        user_id: str, 
        target_date
    ) -> Dict[str, Any]:
        """Run full analysis using all AI roles."""
        from datetime import date
        
        # Step 1: Get metrics
        metrics = await calculate_daily_metrics(db, user_id, target_date)
        issues = await detect_issues(db, user_id, target_date)
        
        # Step 2: Quality inspection
        execution_data = {
            "date": str(target_date),
            "execution_accuracy": metrics.get("execution_accuracy"),
            "time_deviation": metrics.get("time_deviation"),
            "quality_compliance": metrics.get("quality_compliance"),
            "logs": [],  # Would be populated with actual logs
            "deviations": []
        }
        quality_report = await self.ai.inspect_quality(execution_data)
        
        # Step 3: Control recommendations
        analysis_data = {
            **metrics,
            "issues": issues,
            "recent_deviations": [],
            "signals": []
        }
        control_recommendations = await self.ai.get_control_recommendations(analysis_data)
        
        return {
            "date": str(target_date),
            "metrics": metrics,
            "issues_detected": issues,
            "quality_report": quality_report,
            "control_recommendations": control_recommendations
        }


# Singleton instance
_orchestrator = None


def get_orchestrator() -> AIOrchestrator:
    """Get the AI orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
