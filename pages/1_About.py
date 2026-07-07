import streamlit as st
from utils.supabase_db import db
import base64

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="About | Intelligence Paddy System",
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
    --ips-white-strong: rgba(255, 255, 255, 0.90);
    --ips-border: rgba(47, 107, 71, 0.12);
    --ips-shadow: 0 18px 40px rgba(22, 60, 44, 0.10);
}

.block-container {
    max-width: 1280px;
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

/* remove extra outer rectangle */
.ips-shell {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    backdrop-filter: none;
    box-shadow: none;
}

.ips-hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.84) 0%, rgba(248,245,234,0.86) 100%);
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

.ips-card {
    background: var(--ips-white-glass);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 26px 28px;
    box-shadow: 0 14px 32px rgba(22, 60, 44, 0.08);
    backdrop-filter: blur(8px);
}

.ips-card-title {
    font-size: 30px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 12px;
}

.ips-card-text {
    font-size: 16px;
    line-height: 1.85;
    color: #5c6b61;
}

.ips-highlight-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.90) 0%, rgba(248,245,234,0.95) 100%);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 28px 30px;
    box-shadow: 0 14px 30px rgba(22, 60, 44, 0.08);
    position: relative;
    overflow: hidden;
}

.ips-highlight-bar {
    width: 70px;
    height: 6px;
    border-radius: 999px;
    background: linear-gradient(90deg, #2f6b47, #7ba77e);
    margin-bottom: 16px;
}

.ips-section-title {
    font-size: 36px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 16px;
    line-height: 1.15;
}

.ips-list {
    font-size: 17px;
    line-height: 1.9;
    color: #56675c;
    margin: 0;
    padding-left: 22px;
}

.ips-feature-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--ips-border);
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 10px 24px rgba(22, 60, 44, 0.07);
    height: 100%;
}

.ips-feature-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--ips-green);
    margin-bottom: 10px;
}

.ips-feature-list {
    font-size: 16px;
    line-height: 1.8;
    color: #5c6b61;
    margin: 0;
    padding-left: 20px;
}

.ips-ai-card {
    background: linear-gradient(135deg, rgba(232,245,233,0.92) 0%, rgba(255,255,255,0.88) 100%);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 30px 32px;
    box-shadow: 0 14px 30px rgba(22, 60, 44, 0.08);
}

.ips-ai-title {
    font-size: 30px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 10px;
}

.ips-ai-text {
    font-size: 16px;
    line-height: 1.85;
    color: #58685d;
}

.ips-footer {
    background: linear-gradient(135deg, rgba(22,60,44,0.95) 0%, rgba(47,107,71,0.92) 100%);
    border-radius: 24px;
    padding: 28px 30px;
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
    .ips-card-title,
    .ips-ai-title,
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
# HERO SECTION
# =====================================================
st.markdown("""
<div class="ips-hero">
    <div class="ips-badge">About the Platform</div>
    <div class="ips-title">🌾 Intelligence Paddy System</div>
    <div class="ips-subtitle">Empowering Sustainable Paddy Farming Through Smart Digital Solutions</div>
    <div class="ips-desc">
        Intelligence Paddy System is built to strengthen the connection between agricultural monitoring,
        practical field knowledge, and digital decision-making so paddy farming can become more informed,
        resilient, and future-ready.
    </div>
    <div class="ips-chip-row">
        <span class="ips-chip">🌱 Crop Monitoring</span>
        <span class="ips-chip">📊 Agriculture Insights</span>
        <span class="ips-chip">🤝 Farmer-Officer Support</span>
        <span class="ips-chip">🌍 Sustainable Farming</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# INTRODUCTION
# =====================================================
st.markdown("""
<div class="ips-card">
    <div class="ips-card-title">Digital Support for Modern Paddy Agriculture</div>
    <div class="ips-card-text">
        <b>Intelligence Paddy System</b> is a modern agricultural information and monitoring
        platform designed to support the long-term growth of the paddy farming industry.
        <br><br>
        Our mission is to help farmers and agriculture professionals make better,
        faster, and more informed decisions by providing clear insights into
        crop health, field conditions, and best agricultural practices.
        <br><br>
        By combining digital monitoring, data-driven insights, and expert guidance,
        Intelligence Paddy System aims to strengthen food security while improving
        productivity and sustainability in paddy cultivation.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# WHY PADDY FARMING MATTERS
# =====================================================
st.markdown("""
<div class="ips-highlight-card">
    <div class="ips-highlight-bar"></div>
    <div class="ips-section-title">🌱 Why Paddy Farming Matters</div>
    <div class="ips-card-text">
        Paddy farming is the backbone of food supply for millions of people.
        As demand continues to grow, farmers face increasing challenges such as:
    </div>
    <ul class="ips-list">
        <li>Climate uncertainty</li>
        <li>Crop diseases and pest outbreaks</li>
        <li>Rising production costs</li>
        <li>Limited access to timely information</li>
    </ul>
    <div class="ips-card-text" style="margin-top:12px;">
        Intelligence Paddy System exists to bridge this gap — transforming traditional
        farming into a more resilient, efficient, and data-supported ecosystem.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# REGIONAL FOCUS – KEDAH & MADA
# =====================================================
st.markdown("""
<div class="ips-highlight-card">
    <div class="ips-highlight-bar"></div>
    <div class="ips-section-title">🌾 Supporting Major Paddy Regions</div>
    <div class="ips-card-text">
        Intelligence Paddy System focuses on key paddy-producing regions, particularly
        the <b>Muda Agricultural Development Authority (MADA)</b> area in Kedah —
        Malaysia’s most important rice-growing zone.
    </div>
    <div class="ips-card-text" style="margin-top:12px;">
        <b>Coverage includes:</b>
    </div>
    <ul class="ips-list">
        <li>Kota Setar</li>
        <li>Pendang</li>
        <li>Kubang Pasu</li>
        <li>Pokok Sena</li>
        <li>Parts of Padang Terap</li>
    </ul>
    <div class="ips-card-text" style="margin-top:12px;">
        By focusing on these regions, the platform delivers localized insights that
        match real field conditions and farming practices.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# WHAT INTELLIGENCE PADDY SYSTEM PROVIDES
# =====================================================
st.markdown("""
<div class="ips-section-title">⚙️ What Intelligence Paddy System Provides</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="ips-feature-card">
        <div class="ips-feature-title">🌱 Smart Field Monitoring</div>
        <ul class="ips-feature-list">
            <li>Clear overview of paddy field conditions</li>
            <li>Identification of potential crop issues</li>
            <li>Area-based monitoring insights</li>
            <li>Support for timely decision-making</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="ips-feature-card">
        <div class="ips-feature-title">📊 Actionable Agricultural Insights</div>
        <ul class="ips-feature-list">
            <li>Crop health summaries</li>
            <li>Disease awareness and prevention</li>
            <li>Field-level reporting and tracking</li>
            <li>Better planning and resource management</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# AI ASSISTANCE
# =====================================================
st.markdown("""
<div class="ips-ai-card">
    <div class="ips-ai-title">🤖 Intelligent Agricultural Assistance</div>
    <div class="ips-ai-text">
        Intelligence Paddy System includes intelligent advisory support to help users:
    </div>
    <ul class="ips-list">
        <li>Understand common paddy diseases</li>
        <li>Respond to crop health problems</li>
        <li>Improve farming practices</li>
        <li>Make informed decisions faster</li>
    </ul>
    <div class="ips-ai-text" style="margin-top:12px;">
        This guidance supports both experienced professionals and farmers,
        creating a more connected and knowledgeable farming community.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# VISION
# =====================================================
st.markdown("""
<div class="ips-highlight-card">
    <div class="ips-highlight-bar"></div>
    <div class="ips-section-title">🌍 Our Vision</div>
    <div class="ips-card-text">
        Our vision is to build a trusted digital platform that strengthens the paddy
        farming ecosystem — where technology supports tradition, and data empowers growth.
    </div>
    <div class="ips-card-text" style="margin-top:12px;">
        Intelligence Paddy System strives to:
    </div>
    <ul class="ips-list">
        <li>Increase agricultural productivity</li>
        <li>Reduce crop losses</li>
        <li>Promote sustainable farming practices</li>
        <li>Support the future of food security</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="ips-footer">
    <div class="ips-footer-title">Intelligence Paddy System</div>
    <div class="ips-footer-text">
        Growing Paddy. Empowering Agriculture.
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# PAGE WRAPPER END
# =====================================================
st.markdown('</div>', unsafe_allow_html=True)