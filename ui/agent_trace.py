"""
Visual representation of the LangGraph Multi-Agent execution pipeline and execution trace.
"""
from typing import Dict, Any, List
import streamlit as st


def render_agent_pipeline_visual(execution_trace: List[Dict[str, Any]], revision_count: int = 0) -> None:
    """
    Render visual node graph of the agent execution sequence.
    Nodes: Orchestrator -> Planner -> Researcher -> Preference -> Budget -> Builder -> Validator -> [Revision] -> Final.
    """
    agents_executed = [step.get("agent", "") for step in execution_trace]

    nodes = [
        {"id": "orchestrator", "name": "Orchestrator", "icon": "👑", "match": "Orchestrator"},
        {"id": "planner", "name": "Planner", "icon": "📋", "match": "Planner"},
        {"id": "researcher", "name": "Research", "icon": "🔍", "match": "Research"},
        {"id": "preference", "name": "Preferences", "icon": "🧠", "match": "Preference"},
        {"id": "budget", "name": "Budget", "icon": "🧮", "match": "Budget"},
        {"id": "builder", "name": "Builder", "icon": "🗺️", "match": "Itinerary"},
        {"id": "validator", "name": "Validator", "icon": "⚖️", "match": "Validation"},
    ]

    has_revision = revision_count > 0 or any("Revision" in a for a in agents_executed)
    if has_revision:
        nodes.append({"id": "revision", "name": f"Revision ({revision_count}x)", "icon": "🔄", "match": "Revision"})

    nodes.append({"id": "final", "name": "Ready", "icon": "✅", "match": "completed"})

    st.markdown("""
    <div class="agent-workflow-container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
            <div>
                <span style="font-size: 0.76rem; font-weight: 800; color: #2563EB; text-transform: uppercase; letter-spacing: 0.08em;">
                    Autonomous Pipeline Architecture
                </span>
                <div style="font-size: 1.15rem; font-weight: 800; color: #0F172A;">
                    LangGraph State Machine Execution Flow
                </div>
            </div>
            <span class="nav-status-pill">
                <span class="status-dot"></span> Pipeline Completed
            </span>
        </div>
        <div class="agent-node-row">
    """, unsafe_allow_html=True)

    node_html_list = []
    for idx, node in enumerate(nodes):
        matched = False
        if node["id"] == "final":
            matched = len(execution_trace) > 0
        else:
            matched = any(node["match"].lower() in a.lower() for a in agents_executed)

        css_class = "completed" if matched else "active"
        symbol = "✓" if matched else node["icon"]

        node_box = f"""
        <div class="agent-node {css_class}">
            <div class="agent-node-circle">{symbol}</div>
            <div class="agent-node-name">{node["name"]}</div>
        </div>
        """
        node_html_list.append(node_box)

    # Join with connector lines
    rendered_row = '<div class="agent-connector"></div>'.join(node_html_list)
    st.markdown(f'<div class="agent-node-row">{rendered_row}</div></div>', unsafe_allow_html=True)

    # Collapsible detailed reasoning log
    with st.expander("📜 View Safe Agentic Execution Log (High-Level Actions)", expanded=False):
        for step in execution_trace:
            agent = step.get("agent", "Agent")
            action = step.get("action", "")
            time_str = step.get("timestamp", "")
            status = step.get("status", "completed")
            status_icon = "🟢" if status == "completed" else "🟡"
            st.markdown(f"""
            <div style="padding: 0.4rem 0; border-bottom: 1px solid #F1F5F9; font-size: 0.86rem;">
                {status_icon} <b>{agent}</b> <span style="color:#64748B;">({time_str})</span>: {action}
            </div>
            """, unsafe_allow_html=True)
