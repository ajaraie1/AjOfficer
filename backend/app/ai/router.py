"""AI API Router - Endpoints for AI operations."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database import get_db
from app.auth.jwt import get_current_user_id
from app.ai.orchestrator import get_orchestrator

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/goals/{goal_id}/auto-design")
async def auto_design_processes(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Use AI Process Engineer to automatically design processes for a goal."""
    orchestrator = get_orchestrator()
    result = await orchestrator.auto_design_processes(db, user_id, goal_id)
    
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result


@router.get("/analyze/{target_date}")
async def full_analysis(
    target_date: date,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Run full AI analysis (Quality Inspection + Control Recommendations)."""
    orchestrator = get_orchestrator()
    result = await orchestrator.full_analysis(db, user_id, target_date)
    return result


@router.get("/health")
async def ai_health():
    """Check AI service health."""
    from app.ai.service import get_ai_service
    service = get_ai_service()
    return {
        "configured": service.client is not None,
        "model": service.model
    }
