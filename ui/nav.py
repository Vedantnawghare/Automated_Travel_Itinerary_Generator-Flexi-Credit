"""
Navigation bar and system status indicators for TravelAI.
"""
import streamlit as st
from tools.image_search import is_pexels_configured
from tools.tavily_search import is_tavily_configured
from tools.n8n_webhook import get_n8n_webhook_url
from utils.llm_client import is_groq_configured, get_groq_model


def render_navbar() -> None:
    """Render the top brand navigation bar with live status indicators."""
    groq_ok = is_groq_configured()
    tavily_ok = is_tavily_configured()
    pexels_ok = is_pexels_configured()
    n8n_url = get_n8n_webhook_url()
    n8n_ok = bool(n8n_url and "your-n8n-instance" not in n8n_url)

    active_services = sum([groq_ok, tavily_ok, pexels_ok, n8n_ok, True])  # SQLite is always active
    total_services = 5
    system_label = f"Operational ({active_services}/{total_services})"

    st.markdown(f"""
    <div class="travel-navbar">
        <div class="nav-brand">
            <span style="font-size: 1.7rem;">✈️</span>
            <div>
                <div class="nav-brand-logo">TravelAI</div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 600; letter-spacing: 0.02em;">Automated Travel Itinerary Generator</div>
            </div>
            <span class="nav-brand-badge">Multi-Agent</span>
        </div>
        <div class="nav-links">
            <span style="display: flex; align-items: center; gap: 0.35rem; color: #475569;">
                <span class="status-dot"></span>
                <span>{system_label}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_status() -> None:
    """Render system status details inside Streamlit sidebar."""
    groq_ok = is_groq_configured()
    tavily_ok = is_tavily_configured()
    pexels_ok = is_pexels_configured()
    n8n_url = get_n8n_webhook_url()
    n8n_ok = bool(n8n_url and "your-n8n-instance" not in n8n_url)

    st.markdown("### ⚡ System Integrations")

    st.markdown(f"""
    <div style="font-size: 0.88rem; line-height: 1.8;">
        <div>{'🟢' if groq_ok else '🟡'} <b>Groq LLM</b>: <span style="color:#64748B;">{get_groq_model() if groq_ok else 'Fallback Mode'}</span></div>
        <div>{'🟢' if tavily_ok else '🟡'} <b>Tavily Search</b>: <span style="color:#64748B;">{'Live Search' if tavily_ok else 'Simulated Mode'}</span></div>
        <div>{'🟢' if pexels_ok else '🟡'} <b>Pexels Imagery</b>: <span style="color:#64748B;">{'Active Dynamic' if pexels_ok else 'Curated Fallbacks'}</span></div>
        <div>{'🟢' if n8n_ok else '⚪'} <b>n8n Automation</b>: <span style="color:#64748B;">{'Connected' if n8n_ok else 'Webhook Unset'}</span></div>
        <div>🟢 <b>SQLite Memory</b>: <span style="color:#64748B;">Local Connected</span></div>
    </div>
    """, unsafe_allow_html=True)

    if not groq_ok or not tavily_ok or not pexels_ok:
        st.caption("💡 Deterministic fallbacks active for unconfigured APIs. Add keys in `.env` or Streamlit Cloud Secrets.")
