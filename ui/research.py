"""
Presentation of verified live research sources and Tavily findings.
"""
from typing import List, Dict
from urllib.parse import urlparse
import streamlit as st


def render_research_sources(research_results: List[Dict[str, str]]) -> None:
    """Render clean, elegant research source cards without raw URL dumping."""
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem;">
            🌐 Live Web Research & Verified Knowledge
        </h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            Live travel intelligence retrieved by the Research Agent via Tavily Search tool.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not research_results:
        st.info("No external web research articles recorded for this run.")
        return

    for item in research_results:
        title = item.get("title", "Travel Intelligence Source")
        url = item.get("url", "")
        content = item.get("content", "").strip()

        domain = "Verified Guide"
        if url:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace("www.", "") or "Verified Source"
            except Exception:
                domain = "Web Source"

        st.markdown(f"""
        <div class="source-clean-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
                <div>
                    <span class="source-card-domain">🔗 {domain}</span>
                    <div style="font-size: 1.08rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem;">
                        {title}
                    </div>
                </div>
                {f'<a href="{url}" target="_blank" style="font-size: 0.8rem; font-weight: 600; color: #2563EB; background: #EFF6FF; padding: 0.3rem 0.7rem; border-radius: 8px; text-decoration: none; border: 1px solid #BFDBFE;">Visit Source ↗</a>' if url and url != '#' else ''}
            </div>
            <p style="font-size: 0.9rem; line-height: 1.6; color: #475569; margin: 0.4rem 0 0 0;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)
