"""
Deterministic budget allocation and financial feasibility visualization.
"""
from typing import Dict, Any
import streamlit as st


def render_budget_section(budget_breakdown: Dict[str, Any], user_budget: float) -> None:
    """Render premium financial overview cards, visual progress bar, and breakdown table."""
    total_cost = float(budget_breakdown.get("total", 0.0))
    user_bud = float(user_budget or budget_breakdown.get("budget", 0.0))
    remaining = float(budget_breakdown.get("remaining", user_bud - total_cost))
    within_budget = budget_breakdown.get("within_budget", total_cost <= user_bud)

    # Calculate percentage safely
    pct = min(100.0, max(0.0, (total_cost / user_bud * 100))) if user_bud > 0 else 100.0
    bar_color = "#10B981" if within_budget else "#EF4444"

    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h3 style="font-size: 1.35rem; font-weight: 800; color: #0F172A; margin-bottom: 0.2rem;">
            💰 Financial Feasibility & Budget Breakdown
        </h3>
        <p style="font-size: 0.88rem; color: #64748B;">
            All expenses are deterministically computed by the Budget Agent based on travel dates, tier rates, and group size.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3 Summary Metric Cards
    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(f"""
        <div class="metric-grid-card">
            <div class="metric-grid-label">Total User Budget</div>
            <div class="metric-grid-val" style="color: #2563EB;">₹{user_bud:,.0f}</div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:0.2rem;">Allocated ceiling</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-grid-card">
            <div class="metric-grid-label">Estimated Total Cost</div>
            <div class="metric-grid-val" style="color: #0F172A;">₹{total_cost:,.0f}</div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:0.2rem;">Computed line items</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        diff_color = "#10B981" if remaining >= 0 else "#DC2626"
        diff_label = "Surplus / Buffer" if remaining >= 0 else "Over Budget By"
        st.markdown(f"""
        <div class="metric-grid-card">
            <div class="metric-grid-label">{diff_label}</div>
            <div class="metric-grid-val" style="color: {diff_color};">₹{abs(remaining):,.0f}</div>
            <div style="font-size:0.75rem; color:{diff_color}; font-weight:600; margin-top:0.2rem;">
                {'✓ Within Budget' if within_budget else '⚠ Exceeds Budget Limit'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Visual Budget Utilization Gauge / Progress Bar
    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.2rem; margin: 1.2rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 0.4rem;">
            <span>Budget Utilization: {pct:.1f}%</span>
            <span>Target: ₹{user_bud:,.0f}</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width: {pct}%; background-color: {bar_color};"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748B;">
            <span>₹0</span>
            <span>{'Safe margin' if within_budget else 'Over-budget adjustment required'}</span>
            <span>₹{user_bud:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Itemized Breakdown Table & Calculation Notes
    b_col1, b_col2 = st.columns([1.1, 0.9])

    with b_col1:
        st.markdown("#### Itemized Category Allocations")
        cat_data = {
            "Expense Category": [
                "Intercity Transit",
                "Accommodation / Lodging",
                "Dining & Food",
                "Activities & Entry Fees",
                "Local Transportation",
                "Buffer / Contingency (6%)",
                "Total Estimated Spend"
            ],
            "Allocated Amount": [
                f"₹{budget_breakdown.get('transportation', 0):,.0f}",
                f"₹{budget_breakdown.get('accommodation', 0):,.0f}",
                f"₹{budget_breakdown.get('food', 0):,.0f}",
                f"₹{budget_breakdown.get('activities', 0):,.0f}",
                f"₹{budget_breakdown.get('local_transport', 0):,.0f}",
                f"₹{budget_breakdown.get('miscellaneous', 0):,.0f}",
                f"₹{total_cost:,.0f}",
            ]
        }
        st.table(cat_data)

    with b_col2:
        st.markdown("#### Calculation Rationale & Formulas")
        notes = budget_breakdown.get("breakdown_notes", [])
        if notes:
            for n in notes:
                st.markdown(f"- {n}")
        else:
            st.write("Deterministic calculation based on traveler count and duration.")
