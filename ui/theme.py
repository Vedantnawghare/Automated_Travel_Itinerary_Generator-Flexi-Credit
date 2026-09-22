"""
Theme and custom styling for TravelAI.
Injects premium CSS, responsive layouts, glassmorphism surfaces, and 3D hover effects.
"""
import streamlit as st


def inject_custom_theme() -> None:
    """Inject custom styles, fonts, animations, and responsive rules."""
    st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

    :root {
        --primary-blue: #2563EB;
        --deep-teal: #0D9488;
        --teal-dark: #115E59;
        --sunset-amber: #F59E0B;
        --emerald-green: #10B981;
        --slate-dark: #0F172A;
        --slate-card: #1E293B;
        --text-primary: #1E293B;
        --text-muted: #64748B;
        --border-subtle: rgba(226, 232, 240, 0.8);
        --glass-bg: rgba(255, 255, 255, 0.88);
        --glass-border: rgba(255, 255, 255, 0.6);
        --shadow-soft: 0 10px 25px -5px rgba(15, 23, 42, 0.06), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
        --shadow-hover: 0 20px 30px -10px rgba(15, 23, 42, 0.12), 0 10px 15px -5px rgba(13, 148, 136, 0.1);
    }

    /* Base App Styling */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 1280px;
    }

    /* Top Brand Navigation Bar */
    .travel-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.9rem 1.6rem;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        text-decoration: none;
    }

    .nav-brand-logo {
        font-size: 1.6rem;
        background: linear-gradient(135deg, #2563EB, #0D9488);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .nav-brand-badge {
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border: 1px solid #BFDBFE;
    }

    .nav-links {
        display: flex;
        align-items: center;
        gap: 1.4rem;
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-muted);
    }

    .nav-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: #F0FDF4;
        color: #166534;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #BBF7D0;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
        animation: pulse-dot 2s infinite ease-in-out;
    }

    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.25); opacity: 0.7; }
    }

    /* Hero Section */
    .travel-hero {
        position: relative;
        border-radius: 24px;
        overflow: hidden;
        margin-bottom: 2.2rem;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 3rem 2.5rem;
        box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.2);
        background-color: #0F172A;
    }

    .hero-bg-img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.75;
        transition: transform 12s cubic-bezier(0.25, 1, 0.5, 1);
        z-index: 1;
    }

    .travel-hero:hover .hero-bg-img {
        transform: scale(1.06);
    }

    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.2) 0%, rgba(15, 23, 42, 0.85) 90%);
        z-index: 2;
    }

    .hero-content {
        position: relative;
        z-index: 3;
        max-width: 780px;
        color: #FFFFFF;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        color: #F8FAFC;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }

    .hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        margin-bottom: 0.7rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    .hero-subtitle {
        font-size: 1.12rem;
        line-height: 1.5;
        color: #E2E8F0;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Section Cards & Form Containers */
    .form-group-card {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 20px;
        padding: 1.6rem;
        margin-bottom: 1.4rem;
        box-shadow: var(--shadow-soft);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .form-group-card:hover {
        border-color: rgba(13, 148, 136, 0.3);
        box-shadow: var(--shadow-hover);
    }

    .form-section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 1.08rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 1.2rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #F1F5F9;
    }

    .form-icon-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
        color: #4F46E5;
        font-size: 1.05rem;
    }

    /* Destination Result Hero Header */
    .dest-hero-card {
        position: relative;
        border-radius: 22px;
        overflow: hidden;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 2.2rem 2.2rem;
        margin-bottom: 2rem;
        box-shadow: 0 16px 32px -10px rgba(15, 23, 42, 0.2);
        background-color: #0F172A;
    }

    .dest-hero-bg {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.82;
        transition: transform 0.6s ease;
        z-index: 1;
    }

    .dest-hero-card:hover .dest-hero-bg {
        transform: scale(1.03);
    }

    .dest-hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.1) 0%, rgba(15, 23, 42, 0.88) 95%);
        z-index: 2;
    }

    .dest-hero-content {
        position: relative;
        z-index: 3;
        color: #FFFFFF;
    }

    .dest-chips-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.9rem;
    }

    .dest-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 255, 255, 0.22);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #FFFFFF;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* 3D Interactive Itinerary Cards */
    .day-travel-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        perspective: 1000px;
    }

    .day-travel-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 35px -8px rgba(15, 23, 42, 0.12), 0 8px 16px -4px rgba(13, 148, 136, 0.08);
        border-color: #CBD5E1;
    }

    .day-banner-container {
        position: relative;
        height: 180px;
        overflow: hidden;
        background-color: #1E293B;
    }

    .day-banner-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .day-travel-card:hover .day-banner-img {
        transform: scale(1.05);
    }

    .day-banner-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1.2rem 1.4rem 0.8rem 1.4rem;
        background: linear-gradient(180deg, transparent 0%, rgba(15, 23, 42, 0.85) 100%);
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }

    .day-badge-title {
        color: #FFFFFF;
        font-size: 1.28rem;
        font-weight: 700;
        text-shadow: 0 1px 4px rgba(0,0,0,0.4);
    }

    .day-cost-tag {
        background: rgba(16, 185, 129, 0.92);
        color: #FFFFFF;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 0.28rem 0.75rem;
        border-radius: 9999px;
        backdrop-filter: blur(4px);
    }

    .day-card-body {
        padding: 1.4rem;
    }

    .time-slot-card {
        background: #F8FAFC;
        border: 1px solid #EEF2F6;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.9rem;
        transition: background 0.2s ease;
    }

    .time-slot-card:hover {
        background: #F1F5F9;
    }

    .time-slot-header {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.92rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }

    .activity-bullet {
        position: relative;
        padding-left: 1.1rem;
        font-size: 0.9rem;
        line-height: 1.5;
        color: #334155;
        margin-bottom: 0.45rem;
    }

    .activity-bullet::before {
        content: "•";
        position: absolute;
        left: 0.2rem;
        color: var(--deep-teal);
        font-weight: bold;
        font-size: 1.1rem;
    }

    .day-tips-box {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1rem;
        font-size: 0.84rem;
        color: #92400E;
        margin-top: 1rem;
    }

    /* Budget Visualization Cards */
    .metric-grid-card {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: var(--shadow-soft);
        transition: transform 0.2s ease;
    }

    .metric-grid-card:hover {
        transform: translateY(-2px);
    }

    .metric-grid-val {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
    }

    .metric-grid-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }

    .progress-track {
        width: 100%;
        height: 12px;
        background-color: #E2E8F0;
        border-radius: 9999px;
        overflow: hidden;
        margin: 0.8rem 0;
    }

    .progress-fill {
        height: 100%;
        border-radius: 9999px;
        transition: width 1s ease-in-out;
    }

    /* Agentic Workflow Execution Stepper */
    .agent-workflow-container {
        background: #FFFFFF;
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-soft);
    }

    .agent-node-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        padding: 0.8rem 0;
    }

    .agent-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        min-width: 90px;
    }

    .agent-node-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #F1F5F9;
        color: #64748B;
        border: 2px solid #CBD5E1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        transition: all 0.3s ease;
    }

    .agent-node.active .agent-node-circle {
        background: #EFF6FF;
        color: #2563EB;
        border-color: #3B82F6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
    }

    .agent-node.completed .agent-node-circle {
        background: #ECFDF5;
        color: #059669;
        border-color: #10B981;
    }

    .agent-node-name {
        font-size: 0.74rem;
        font-weight: 700;
        color: #334155;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .agent-connector {
        flex: 0 0 20px;
        height: 2px;
        background-color: #CBD5E1;
        margin-bottom: 1.4rem;
    }

    /* Research Source Cards */
    .source-clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.25s ease;
    }

    .source-clean-card:hover {
        border-color: #93C5FD;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    }

    .source-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1E40AF;
        text-decoration: none;
        margin-bottom: 0.4rem;
        display: inline-block;
    }

    .source-card-domain {
        font-size: 0.76rem;
        font-weight: 600;
        color: #64748B;
        background: #F1F5F9;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
        display: inline-block;
    }

    /* Profile / Memory Badges */
    .memory-stat-card {
        background: linear-gradient(135deg, #F8FAFC, #FFFFFF);
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }

    .memory-badge-pill {
        display: inline-block;
        background: #EFF6FF;
        color: #1E40AF;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 8px;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    /* Mobile Responsive Breakpoints */
    @media (max-width: 768px) {
        .travel-navbar {
            flex-direction: column;
            gap: 0.8rem;
            align-items: flex-start;
            padding: 1rem;
        }

        .nav-links {
            width: 100%;
            justify-content: space-between;
        }

        .travel-hero {
            padding: 2rem 1.4rem;
            min-height: 280px;
        }

        .hero-title {
            font-size: 1.9rem;
        }

        .hero-subtitle {
            font-size: 0.98rem;
        }

        .agent-node-row {
            overflow-x: auto;
            justify-content: flex-start;
            padding-bottom: 1rem;
        }

        .agent-node {
            min-width: 75px;
        }

        .dest-hero-card {
            padding: 1.5rem 1.2rem;
            min-height: 240px;
        }

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    /* Accessibility: Reduced Motion */
    @media (prefers-reduced-motion: reduce) {
        *, ::before, ::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
