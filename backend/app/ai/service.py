"""Centralized AI Service for IGAMS."""

from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import json

from app.config import get_settings
from app.ai.prompts.process_engineer import PROCESS_ENGINEER_SYSTEM_PROMPT, get_process_engineer_prompt
from app.ai.prompts.quality_inspector import QUALITY_INSPECTOR_SYSTEM_PROMPT, get_quality_inspector_prompt
from app.ai.prompts.control_system import CONTROL_SYSTEM_PROMPT, get_control_system_prompt

settings = get_settings()


class AIService:
    """Centralized AI service with role-based prompting."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = "gpt-4o"
    
    async def _call_ai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Make an AI API call."""
        if not self.client:
            # Return mock response if no API key
            return {"error": "AI service not configured", "mock": True}
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)}
    
    async def design_processes(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Process Engineer role to design processes for a goal."""
        user_prompt = get_process_engineer_prompt(goal_data)
        return await self._call_ai(PROCESS_ENGINEER_SYSTEM_PROMPT, user_prompt)
    
    async def inspect_quality(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Quality Inspector role to analyze execution quality."""
        user_prompt = get_quality_inspector_prompt(execution_data)
        return await self._call_ai(QUALITY_INSPECTOR_SYSTEM_PROMPT, user_prompt)
    
    async def get_control_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Control System role to get process improvement recommendations."""
        user_prompt = get_control_system_prompt(analysis_data)
        return await self._call_ai(CONTROL_SYSTEM_PROMPT, user_prompt)


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get the AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
