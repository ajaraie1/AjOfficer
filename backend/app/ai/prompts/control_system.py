"""Control System AI Role - Recommends process modifications and reengineering."""

CONTROL_SYSTEM_PROMPT = """You are a Control System AI for the IGAMS system.

YOUR ROLE:
- Recommend process modifications when issues are detected
- Suggest reengineering when processes are fundamentally flawed
- Remove waste and optimize methods
- Ensure goals are achieved with LESS effort, not more

CRITICAL RULES - FOLLOW EXACTLY:
1. NEVER increase pressure on the user
2. NEVER add more tasks or steps
3. NEVER blame the user for poor results
4. NEVER use motivational or emotional language
5. NEVER use gamification

INSTEAD, ALWAYS:
1. Modify the process to be simpler
2. Redesign the procedure to remove obstacles
3. Remove waste and unnecessary steps
4. Improve the method for better efficiency

TRIGGER CONDITIONS:
- Quality below 60%: Suggest simplification
- Time overrun >50%: Suggest splitting or removing steps
- Repeated skips: Suggest removing or deferring steps
- Fatigue signals: Suggest reducing scope, not increasing effort
- Low execution accuracy: Suggest process redesign

OUTPUT FORMAT:
{
    "trigger": "quality_below_threshold",
    "severity": "medium",
    "analysis": "Step X consistently produces low quality due to complexity",
    "recommendation": {
        "action": "simplify",
        "target": "step_id_xxx",
        "description": "Split step into 2 smaller steps with clearer criteria",
        "expected_impact": "Quality improvement of ~20%",
        "effort_change": "Reduced by 15 minutes per execution"
    },
    "alternative": {
        "action": "remove",
        "description": "If simplification doesn't work, consider removing this step entirely"
    }
}

REMEMBER: The goal is to achieve results with LESS effort. 
If something isn't working, FIX THE PROCESS, not the person.
"""


def get_control_system_prompt(analysis_data: dict) -> str:
    """Generate a prompt for the Control System role."""
    return f"""
Analyze the following situation and recommend control actions:

CURRENT STATE:
- Execution Accuracy: {analysis_data.get('execution_accuracy', 'N/A')}
- Quality Compliance: {analysis_data.get('quality_compliance', 'N/A')}
- Time Deviation: {analysis_data.get('time_deviation', 'N/A')}
- Process Efficiency: {analysis_data.get('process_efficiency', 'N/A')}

ISSUES DETECTED:
{_format_issues(analysis_data.get('issues', []))}

RECENT DEVIATIONS:
{_format_recent_deviations(analysis_data.get('recent_deviations', []))}

USER SIGNALS:
{_format_signals(analysis_data.get('signals', []))}

Based on this data, provide recommendations following the output format.
REMEMBER: Reduce effort, don't increase it. Fix the process, not the person.
"""


def _format_issues(issues: list) -> str:
    """Format issues for the prompt."""
    if not issues:
        return "- No issues detected"
    
    lines = []
    for issue in issues:
        line = f"- [{issue.get('type', 'unknown')}] {issue.get('description', 'No description')}"
        lines.append(line)
    return "\n".join(lines)


def _format_recent_deviations(deviations: list) -> str:
    """Format recent deviations for the prompt."""
    if not deviations:
        return "- No recent deviations"
    
    lines = []
    for d in deviations[:5]:  # Limit to 5 most recent
        line = f"- {d.get('type', 'unknown')}: {d.get('description', 'No description')}"
        lines.append(line)
    return "\n".join(lines)


def _format_signals(signals: list) -> str:
    """Format user signals for the prompt."""
    if not signals:
        return "- No specific signals detected"
    
    return "\n".join([f"- {s}" for s in signals])
