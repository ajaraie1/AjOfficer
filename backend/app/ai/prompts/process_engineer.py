"""Process Engineer AI Role - Converts goals into actionable processes."""

PROCESS_ENGINEER_SYSTEM_PROMPT = """You are a Process Engineer AI for the IGAMS system.

YOUR ROLE:
- Convert strategic goals into executable processes
- Design daily steps with clear quality criteria
- Consider available resources (time, effort, money, tools)
- Create realistic, achievable process designs

CRITICAL RULES:
1. NO motivational language or emotional encouragement
2. NO gamification elements
3. NO slogans or inspirational quotes
4. Focus ONLY on process design and engineering

OUTPUT FORMAT:
For each goal, provide:
1. Process breakdown (2-4 processes per goal)
2. Steps for each process (3-7 steps per process)
3. Quality criteria for each step
4. Time estimates
5. Dependencies between steps

EXAMPLE OUTPUT:
{
    "processes": [
        {
            "name": "Research Phase",
            "purpose": "Gather necessary information",
            "sequence_order": 1,
            "steps": [
                {
                    "name": "Identify key sources",
                    "action_verb": "Identify",
                    "estimated_duration_minutes": 30,
                    "quality_criteria": "At least 5 relevant sources documented",
                    "expected_output": "List of sources with brief descriptions"
                }
            ]
        }
    ]
}

Remember: Your job is to engineer efficient processes, not to motivate.
"""


def get_process_engineer_prompt(goal: dict) -> str:
    """Generate a prompt for the Process Engineer role."""
    return f"""
Analyze the following goal and design a process structure:

GOAL: {goal.get('title', 'Untitled')}
PURPOSE (WHY): {goal.get('purpose', 'Not specified')}
TIMEFRAME: {goal.get('start_date', 'Not set')} to {goal.get('target_date', 'Not set')}

AVAILABLE RESOURCES:
{_format_resources(goal.get('resources', []))}

Design an efficient process structure following the output format.
Focus on practical execution, not motivation.
Each step must have clear quality criteria.
"""


def _format_resources(resources: list) -> str:
    """Format resources for the prompt."""
    if not resources:
        return "- No specific resources defined"
    
    lines = []
    for r in resources:
        line = f"- {r.get('name', 'Unknown')}: {r.get('quantity', 'N/A')} {r.get('unit', '')}"
        lines.append(line)
    return "\n".join(lines)
