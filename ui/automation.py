"""
Action panel for n8n automated webhook integration (Google Calendar & Gmail).
"""
from typing import Dict, Any
import streamlit as st
from tools.n8n_webhook import send_to_n8n_webhook, get_n8n_webhook_url


def render_automation_panel(state: Dict[str, Any]) -> None:
    """Render the n8n automation panel and execute webhook triggers cleanly."""
    n8n_url = get_n8n_webhook_url()
    is_configured = bool(n8n_url and "your-n8n-instance" not in n8n_url)
    user_email = state.get("email") or "traveler@example.com"
    destination = state.get("destination", "Trip")
    budget_breakdown = state.get("budget_breakdown", {})
    itinerary = state.get("itinerary", [])

    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.8rem;">
            <div>
                <span style="font-size: 0.76rem; font-weight: 800; color: #D97706; text-transform: uppercase; letter-spacing: 0.08em;">
                    ⚡ External Workflow Automation
                </span>
                <div style="font-size: 1.2rem; font-weight: 800; color: #0F172A;">
                    Export & Automate Your Trip via n8n
                </div>
            </div>
    """, unsafe_allow_html=True)

    status_pill = (
        '<span class="nav-status-pill"><span class="status-dot"></span> Ready to Dispatch</span>'
        if is_configured else
        '<span style="background:#F1F5F9; color:#64748B; font-size:0.75rem; font-weight:600; padding:0.25rem 0.6rem; border-radius:9999px;">Webhook Not Configured</span>'
    )
    st.markdown(f"{status_pill}</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 1.2rem;">
        Triggers your n8n workflow to create Google Calendar schedule blocks and dispatch an itemized travel brief to <b>{user_email}</b>.
    </p>
    """, unsafe_allow_html=True)

    act_col1, act_col2 = st.columns([1, 1])

    with act_col1:
        if st.button("🔄 Plan Another Trip / Reset", use_container_width=True):
            if "trip_result" in st.session_state:
                del st.session_state["trip_result"]
            st.rerun()

    with act_col2:
        dispatch_btn = st.button("🚀 Dispatch to n8n (Calendar + Gmail)", type="primary", use_container_width=True)
        if dispatch_btn:
            if not is_configured:
                st.warning("⚠️ n8n Webhook URL is not configured yet. Set `N8N_WEBHOOK_URL` in `.env` or Streamlit Cloud Secrets to enable live automation.")
            else:
                webhook_payload = {
                    "destination": destination,
                    "origin": state.get("origin"),
                    "start_date": state.get("start_date"),
                    "end_date": state.get("end_date"),
                    "duration": state.get("duration"),
                    "travellers": state.get("travellers"),
                    "budget": state.get("budget"),
                    "total_estimated_cost": budget_breakdown.get("total"),
                    "currency": "INR",
                    "preferences": state.get("preferences", {}),
                    "itinerary": itinerary,
                    "email": user_email,
                    "create_calendar_events": True,
                    "send_email": True,
                }
                with st.spinner("Connecting to n8n webhook and dispatching payload..."):
                    res = send_to_n8n_webhook(webhook_payload)
                    if res.get("success"):
                        st.success(f"✅ {res.get('message')}")
                    else:
                        st.error(f"❌ {res.get('message')}")

    st.markdown("</div>", unsafe_allow_html=True)
