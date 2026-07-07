import streamlit as st
from utils.supabase_db import db
import base64

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="FAQ | Intelligence Paddy System",
    layout="wide"
)

# =====================================================
# BACKGROUND FUNCTION (UNIFIED)
# =====================================================
def set_background(image_path=None):
    if image_path is None:
        return

    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# APPLY BACKGROUND
# =====================================================
set_background("assets/Background.jpg")

# =====================================================
# UNIFIED STYLES
# =====================================================
st.markdown("""
<style>
:root {
    --ips-green-dark: #163c2c;
    --ips-green: #2f6b47;
    --ips-green-soft: #5f8f68;
    --ips-cream: #f8f5ea;
    --ips-white-glass: rgba(255, 255, 255, 0.72);
    --ips-white-strong: rgba(255, 255, 255, 0.88);
    --ips-border: rgba(47, 107, 71, 0.12);
    --ips-shadow: 0 18px 40px rgba(22, 60, 44, 0.10);
}

.block-container {
    max-width: 1280px;
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

/* remove extra outer rectangle visually, keep wrapper structure */
.ips-shell {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    backdrop-filter: none;
    box-shadow: none;
}

.ips-hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.82) 0%, rgba(248,245,234,0.85) 100%);
    border: 1px solid var(--ips-border);
    border-radius: 28px;
    padding: 38px 40px;
    box-shadow: var(--ips-shadow);
    position: relative;
    overflow: hidden;
}

.ips-hero::after {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    right: -70px;
    top: -70px;
    background: radial-gradient(circle, rgba(95,143,104,0.18) 0%, rgba(95,143,104,0.02) 70%);
    border-radius: 50%;
    pointer-events: none;
}

.ips-badge {
    display: inline-block;
    padding: 8px 14px;
    background: #eaf3eb;
    border: 1px solid rgba(47, 107, 71, 0.10);
    color: var(--ips-green-dark);
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.ips-title {
    font-size: 52px;
    line-height: 1.08;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 10px;
    letter-spacing: -0.02em;
}

.ips-subtitle {
    font-size: 22px;
    color: #55665c;
    margin-bottom: 14px;
    line-height: 1.5;
}

.ips-desc {
    font-size: 16px;
    line-height: 1.8;
    color: #617066;
    max-width: 980px;
}

.ips-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 22px;
}

.ips-chip {
    display: inline-block;
    padding: 10px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.78);
    border: 1px solid var(--ips-border);
    color: var(--ips-green-dark);
    font-size: 13px;
    font-weight: 700;
}

.ips-intro-card {
    background: var(--ips-white-glass);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 26px 28px;
    box-shadow: 0 14px 32px rgba(22, 60, 44, 0.08);
    backdrop-filter: blur(8px);
}

.ips-intro-title {
    font-size: 28px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 10px;
}

.ips-intro-text {
    font-size: 16px;
    line-height: 1.8;
    color: #5c6b61;
}

.ips-section-card {
    background: var(--ips-white-glass);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 22px 24px 10px 24px;
    box-shadow: 0 12px 28px rgba(22, 60, 44, 0.08);
    backdrop-filter: blur(8px);
    margin-bottom: 22px;
}

.ips-section-title {
    font-size: 30px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 4px;
}

.ips-section-subtitle {
    font-size: 14px;
    color: #6b7b71;
    margin-bottom: 14px;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(47, 107, 71, 0.10) !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,0.72) !important;
    overflow: hidden;
    margin-bottom: 12px;
    box-shadow: 0 8px 18px rgba(22, 60, 44, 0.05);
}

div[data-testid="stExpander"] details {
    border-radius: 18px !important;
}

div[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: var(--ips-green-dark) !important;
    font-size: 16px !important;
    padding-top: 2px !important;
    padding-bottom: 2px !important;
}

div[data-testid="stExpander"] p,
div[data-testid="stExpander"] li,
div[data-testid="stExpander"] div {
    color: #55665c !important;
    line-height: 1.8 !important;
    font-size: 15px !important;
}

.ips-footer-card {
    background: linear-gradient(135deg, rgba(22,60,44,0.95) 0%, rgba(47,107,71,0.92) 100%);
    border-radius: 24px;
    padding: 30px 32px;
    text-align: center;
    color: white;
    box-shadow: 0 16px 34px rgba(22, 60, 44, 0.16);
}

.ips-footer-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
}

.ips-footer-text {
    font-size: 17px;
    color: rgba(255,255,255,0.90);
    line-height: 1.7;
}

@media (max-width: 768px) {
    .ips-hero {
        padding: 26px 20px;
    }

    .ips-title {
        font-size: 36px;
    }

    .ips-subtitle {
        font-size: 18px;
    }

    .ips-section-title,
    .ips-intro-title,
    .ips-footer-title {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# PAGE WRAPPER START
# =====================================================
st.markdown('<div class="ips-shell">', unsafe_allow_html=True)

# =====================================================
# HERO
# =====================================================
st.markdown("""
<div class="ips-hero">
    <div class="ips-badge">Support & Guidance</div>
    <div class="ips-title">❓ Frequently Asked Questions</div>
    <div class="ips-subtitle">Everything you need to know about Intelligence Paddy System</div>
    <div class="ips-desc">
        Explore common questions about paddy monitoring, farmer support, digital reporting,
        intelligent assistance, and sustainable agriculture workflows in one place.
    </div>
    <div class="ips-chip-row">
        <span class="ips-chip">🌾 Paddy Agriculture</span>
        <span class="ips-chip">📄 Reporting Support</span>
        <span class="ips-chip">🤖 AI Guidance</span>
        <span class="ips-chip">🔐 Platform Trust</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# INTRO BOX
# =====================================================
st.markdown("""
<div class="ips-intro-card">
    <div class="ips-intro-title">Helping Users Understand the Platform</div>
    <div class="ips-intro-text">
        We understand that modern agriculture comes with many questions.
        This FAQ section is designed to help farmers, agriculture officers,
        and stakeholders quickly understand how Intelligence Paddy System supports
        better paddy farming decisions.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# GENERAL INFORMATION
# =====================================================
st.markdown("""
<div class="ips-section-card">
    <div class="ips-section-title">🌾 General Information</div>
    <div class="ips-section-subtitle">Overview of the platform and who it supports.</div>
""", unsafe_allow_html=True)

with st.expander("What is Intelligence Paddy System?"):
    st.write("""
    Intelligence Paddy System is a digital agriculture platform designed to support
    paddy farming through field monitoring, agricultural insights, and intelligent
    decision support. It helps users better understand crop conditions and respond
    to issues efficiently.
    """)

with st.expander("Who can use Intelligence Paddy System?"):
    st.write("""
    Intelligence Paddy System is suitable for farmers, agriculture officers,
    and stakeholders involved in paddy cultivation who want clearer insights
    into field conditions and crop health.
    """)

with st.expander("Which areas does Intelligence Paddy System focus on?"):
    st.write("""
    The platform focuses on major paddy-producing regions, especially
    Kedah’s MADA agricultural area, including Kota Setar, Pendang,
    Kubang Pasu, Pokok Sena, and parts of Padang Terap.
    """)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# PADDY FARMING & CROP HEALTH
# =====================================================
st.markdown("""
<div class="ips-section-card">
    <div class="ips-section-title">🌱 Paddy Farming & Crop Health</div>
    <div class="ips-section-subtitle">Questions related to crop conditions and field support.</div>
""", unsafe_allow_html=True)

with st.expander("What kind of crop issues can be monitored?"):
    st.write("""
    The system helps identify common paddy issues such as leaf discoloration,
    pest damage, fungal infections, and abnormal growth patterns through
    structured monitoring and reporting.
    """)

with st.expander("How does Intelligence Paddy System help prevent crop loss?"):
    st.write("""
    By providing early insights and timely recommendations,
    the platform helps users take preventive action before
    issues spread and cause significant yield loss.
    """)

with st.expander("Can this system support sustainable farming?"):
    st.write("""
    Yes. Intelligence Paddy System encourages better water management,
    responsible fertilizer usage, and early disease detection,
    supporting more sustainable and environmentally friendly practices.
    """)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# REPORTING & MONITORING
# =====================================================
st.markdown("""
<div class="ips-section-card">
    <div class="ips-section-title">📄 Reporting & Monitoring</div>
    <div class="ips-section-subtitle">How reports and field records support officer decisions.</div>
""", unsafe_allow_html=True)

with st.expander("How are paddy field reports used?"):
    st.write("""
    Field reports allow agriculture officers to understand on-ground conditions,
    review crop issues, and provide informed recommendations to improve farm outcomes.
    """)

with st.expander("Can officers respond to farmer reports?"):
    st.write("""
    Yes. Officers can review submitted reports and provide guidance,
    recommendations, and follow-up actions based on observed conditions.
    """)

with st.expander("Is historical data useful?"):
    st.write("""
    Historical records help track recurring issues, seasonal patterns,
    and long-term field performance, enabling better planning and decision-making.
    """)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# AI SUPPORT
# =====================================================
st.markdown("""
<div class="ips-section-card">
    <div class="ips-section-title">🤖 Intelligent Assistance</div>
    <div class="ips-section-subtitle">Understanding the role of AI inside the platform.</div>
""", unsafe_allow_html=True)

with st.expander("What is the AI Assistant used for?"):
    st.write("""
    The AI Assistant provides quick answers to common agriculture questions,
    including paddy diseases, crop management practices, and general farming advice.
    """)

with st.expander("Is the AI meant to replace agriculture officers?"):
    st.write("""
    No. The AI Assistant is designed to support users with basic guidance
    and knowledge, while complex decisions should always involve
    professional agricultural expertise.
    """)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# SECURITY & TRUST
# =====================================================
st.markdown("""
<div class="ips-section-card">
    <div class="ips-section-title">🔐 Security & Reliability</div>
    <div class="ips-section-subtitle">Privacy, trust, and future scalability of the platform.</div>
""", unsafe_allow_html=True)

with st.expander("Is user information handled responsibly?"):
    st.write("""
    Intelligence Paddy System is designed with responsible data handling in mind.
    User information and reports are managed to ensure privacy and trust.
    """)

with st.expander("Can this platform grow in the future?"):
    st.write("""
    Yes. Intelligence Paddy System is built with scalability in mind,
    allowing future enhancements such as deeper analytics,
    expanded region coverage, and advanced advisory features.
    """)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# FOOTER MESSAGE
# =====================================================
st.markdown("""
<div class="ips-footer-card">
    <div class="ips-footer-title">Still have questions?</div>
    <div class="ips-footer-text">
        Intelligence Paddy System is here to support smarter paddy farming decisions.
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# PAGE WRAPPER END
# =====================================================
st.markdown('</div>', unsafe_allow_html=True)