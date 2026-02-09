"""Quality Inspector AI Role - Analyzes execution and identifies issues."""

QUALITY_INSPECTOR_SYSTEM_PROMPT = """You are a Quality Inspector AI for the IGAMS system.

YOUR ROLE:
- Analyze daily execution logs
- Identify waste, errors, and inefficiencies
- Score quality compliance
- Detect patterns of poor execution

CRITICAL RULES:
1. NO motivational language or emotional encouragement
2. NO blame or criticism of the user personally
3. NO gamification elements
4. Focus ONLY on process quality and compliance

ANALYSIS FOCUS:
1. Execution Accuracy: Were steps executed as planned?
2. Time Deviation: Did steps take expected time?
3. Quality Compliance: Were quality criteria met?
4. Process Efficiency: Was output proportional to effort?

ISSUE TYPES TO DETECT:
- Waste: Unnecessary steps, duplicate work, waiting time
- Errors: Quality below threshold, missed criteria
- Inefficiency: High effort, low output
- Patterns: Recurring deviations, consistent skips

OUTPUT FORMAT:
{
    "quality_score": 0.75,
    "compliance_score": 0.80,
    "findings": [
        {
            "type": "waste",
            "severity": "medium",
            "description": "Step X duplicates effort from Step Y",
            "recommendation": "Consider merging steps X and Y"
        }
    ],
    "waste_identified": ["duplication", "waiting"],
    "errors_detected": [
        {
            "step_id": "xxx",
            "issue": "Quality criteria not met",
            "actual_vs_expected": "3 sources vs 5 required"
        }
    ]
}

Remember: Inspect the process, not the person.
"""


def get_quality_inspector_prompt(execution_data: dict) -> str:
    """Generate a prompt for the Quality Inspector role."""
    return f"""
Analyze the following execution data:

DATE: {execution_data.get('date', 'Unknown')}

EXECUTION LOGS:
{_format_logs(execution_data.get('logs', []))}

METRICS:
- Execution Accuracy: {execution_data.get('execution_accuracy', 'N/A')}
- Time Deviation: {execution_data.get('time_deviation', 'N/A')}
- Quality Compliance: {execution_data.get('quality_compliance', 'N/A')}

DEVIATIONS RECORDED:
{_format_deviations(execution_data.get('deviations', []))}

Provide a quality inspection report following the output format.
Focus on process issues, not personal criticism.
"""


def _format_logs(logs: list) -> str:
    """Format execution logs for the prompt."""
    if not logs:
        return "- No logs available"
    
    lines = []
    for log in logs:
        status = log.get('status', 'unknown')
        quality = log.get('quality_score', 'N/A')
        line = f"- {log.get('step_name', 'Step')}: {status} (Quality: {quality})"
        if log.get('actual_execution'):
            line += f"\n  Execution: {log.get('actual_execution')}"
        lines.append(line)
    return "\n".join(lines)


def _format_deviations(deviations: list) -> str:
    """Format deviations for the prompt."""
    if not deviations:
        return "- No deviations recorded"
    
    lines = []
    for d in deviations:
        line = f"- [{d.get('type', 'unknown')}] {d.get('description', 'No description')}"
        if d.get('root_cause'):
            line += f"\n  Root cause: {d.get('root_cause')}"
        lines.append(line)
    return "\n".join(lines)
