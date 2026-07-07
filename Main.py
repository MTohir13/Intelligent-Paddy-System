import streamlit as st
from utils.supabase_db import db

# ======================================================
# LANGUAGE DICTIONARY
# ======================================================
TEXT = {
    "EN": {
        "title": "🌾 Intelligence Paddy System",
        "subtitle": "Smart Monitoring, Field Intelligence, and Digital Support for Sustainable Paddy Agriculture",
        "hero_desc": (
            "A digital agriculture platform designed to support officers in monitoring paddy conditions, "
            "reviewing reports, and strengthening communication with farmers through data-driven decisions."
        ),
        "cta": "Login to access the officer dashboard",
        "monitoring_title": "🌱 Smart Monitoring",
        "monitoring_desc": "Monitor paddy field conditions, crop health, and potential risks with structured insights tailored to real farming environments.",
        "insights_title": "📊 Actionable Insights",
        "insights_desc": "Turn field data and reports into clear decisions that help reduce crop loss, improve response speed, and strengthen field support.",
        "ecosystem_title": "🤝 Connected Ecosystem",
        "ecosystem_desc": "Connect farmers, officers, and advisory support into one trusted digital agriculture platform.",
        "overview_title": "Why This System Matters",
        "overview_desc": (
            "Paddy agriculture depends on timely monitoring, clear communication, and practical intervention. "
            "This system helps officers organize information better so field issues can be identified earlier and managed more effectively."
        ),
        "pillar_1_title": "Disease Awareness",
        "pillar_1_desc": "Support early awareness of common paddy disease symptoms and field abnormalities before issues become more serious.",
        "pillar_2_title": "Officer Efficiency",
        "pillar_2_desc": "Centralize key information for reports, profiles, and farmer communication so daily tasks become more structured.",
        "pillar_3_title": "Sustainable Support",
        "pillar_3_desc": "Promote stronger decision-making that supports crop health, productivity, and long-term food security.",
        "stats_title": "Focused on Better Agriculture Operations",
        "stat_1_label": "Crop Monitoring",
        "stat_1_value": "Field-first",
        "stat_2_label": "Officer Workflow",
        "stat_2_value": "Organized",
        "stat_3_label": "Farmer Support",
        "stat_3_value": "Connected",
        "main_cta": "Supporting the Future of Paddy Farming",
        "sub_cta": "Make informed decisions. Improve sustainability. Strengthen food security.",
        "cta_panel_desc": (
            "Access officer tools for profile management, report handling, forum communication, "
            "and AI-assisted guidance in one integrated environment."
        ),
        "footer": "Intelligence Paddy System © 2026<br>Growing Paddy. Empowering Agriculture."
    },
    "BM": {
        "title": "🌾 Penjaga Padi Pintar",
        "subtitle": "Pemantauan Pintar, Kecerdasan Lapangan, dan Sokongan Digital untuk Pertanian Padi Mampan",
        "hero_desc": (
            "Platform pertanian digital yang direka untuk membantu pegawai memantau keadaan padi, "
            "menyemak laporan, dan mengukuhkan komunikasi dengan petani melalui keputusan berasaskan data."
        ),
        "cta": "Log masuk untuk akses papan pemuka pegawai",
        "monitoring_title": "🌱 Pemantauan Pintar",
        "monitoring_desc": "Pantau keadaan sawah padi, kesihatan tanaman, dan risiko potensi dengan panduan berstruktur yang disesuaikan dengan persekitaran pertanian sebenar.",
        "insights_title": "📊 Panduan Boleh Tindak",
        "insights_desc": "Tukar data dan laporan ladang kepada keputusan jelas yang membantu mengurangkan kehilangan hasil, mempercepat tindakan, dan mengukuhkan sokongan lapangan.",
        "ecosystem_title": "🤝 Ekosistem Terhubung",
        "ecosystem_desc": "Hubungkan petani, pegawai, dan sokongan nasihat dalam satu platform pertanian digital yang dipercayai.",
        "overview_title": "Mengapa Sistem Ini Penting",
        "overview_desc": (
            "Pertanian padi memerlukan pemantauan tepat pada masa, komunikasi yang jelas, dan intervensi yang praktikal. "
            "Sistem ini membantu pegawai mengurus maklumat dengan lebih baik supaya isu lapangan dapat dikenal pasti lebih awal dan diurus dengan lebih berkesan."
        ),
        "pillar_1_title": "Kesedaran Penyakit",
        "pillar_1_desc": "Menyokong pengesanan awal simptom penyakit padi dan keabnormalan lapangan sebelum isu menjadi lebih serius.",
        "pillar_2_title": "Kecekapan Pegawai",
        "pillar_2_desc": "Memusatkan maklumat penting untuk laporan, profil, dan komunikasi petani supaya tugasan harian lebih tersusun.",
        "pillar_3_title": "Sokongan Mampan",
        "pillar_3_desc": "Menggalakkan keputusan yang lebih baik untuk menyokong kesihatan tanaman, produktiviti, dan keselamatan makanan jangka panjang.",
        "stats_title": "Berfokus kepada Operasi Pertanian yang Lebih Baik",
        "stat_1_label": "Pemantauan Tanaman",
        "stat_1_value": "Berteraskan Lapangan",
        "stat_2_label": "Aliran Kerja Pegawai",
        "stat_2_value": "Tersusun",
        "stat_3_label": "Sokongan Petani",
        "stat_3_value": "Terhubung",
        "main_cta": "Menyokong Masa Depan Pertanian Padi",
        "sub_cta": "Buat keputusan berinformasi. Tingkatkan kemampanan. Kukuhkan keselamatan makanan.",
        "cta_panel_desc": (
            "Akses alat pegawai untuk pengurusan profil, pengendalian laporan, komunikasi forum, "
            "dan panduan berbantu AI dalam satu persekitaran bersepadu."
        ),
        "footer": "Penjaga Padi Pintar © 2026<br>Menanam Padi. Memperkasakan Pertanian."
    }
}

# ======================================================
# ORIGINAL IMPORTS
# ======================================================
import base64

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Intelligence Paddy System",
    layout="wide"
)

# ======================================================
# BACKGROUND FUNCTION
# ======================================================
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

# ======================================================
# APPLY BACKGROUND
# ======================================================
set_background("assets/Background.jpg")

# ======================================================
# GLOBAL UNIFIED STYLES
# ======================================================
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

.ips-shell {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    backdrop-filter: none;
    box-shadow: none;
}

/* navigation container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 24px !important;
}

/* navigation buttons */
.ips-nav-btn div[data-testid="stButton"] > button {
    width: 100%;
    height: 54px;
    border-radius: 16px !important;
    border: 1px solid rgba(47, 107, 71, 0.10) !important;
    background: rgba(255,255,255,0.82) !important;
    color: #163c2c !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(22, 60, 44, 0.06) !important;
    transition: all 0.2s ease;
}

.ips-nav-btn div[data-testid="stButton"] > button:hover {
    border: 1px solid rgba(47, 107, 71, 0.18) !important;
    background: rgba(255,255,255,0.94) !important;
    color: #163c2c !important;
    transform: translateY(-1px);
}

.ips-nav-btn.active div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #2f6b47 0%, #3b874f 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 12px 24px rgba(47, 107, 71, 0.22) !important;
}

.ips-nav-btn.active div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #2f6b47 0%, #3b874f 100%) !important;
    color: white !important;
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
    font-size: 24px;
    font-weight: 800;
    color: var(--ips-green);
    margin-bottom: 12px;
}

.ips-card-text {
    font-size: 16px;
    line-height: 1.8;
    color: #5c6b61;
}

.ips-section-card {
    background: var(--ips-white-glass);
    border: 1px solid var(--ips-border);
    border-radius: 24px;
    padding: 28px 30px;
    box-shadow: 0 14px 32px rgba(22, 60, 44, 0.08);
    backdrop-filter: blur(8px);
}

.ips-section-title {
    font-size: 32px;
    font-weight: 800;
    color: var(--ips-green-dark);
    margin-bottom: 10px;
}

.ips-section-text {
    font-size: 16px;
    line-height: 1.85;
    color: #5f6f64;
}

.ips-mini-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--ips-border);
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 10px 24px rgba(22, 60, 44, 0.07);
    height: 100%;
}

.ips-mini-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--ips-green);
    margin-bottom: 10px;
}

.ips-mini-text {
    font-size: 15px;
    line-height: 1.75;
    color: #617065;
}

.ips-stats-wrap {
    background: linear-gradient(135deg, rgba(22,60,44,0.95) 0%, rgba(47,107,71,0.92) 100%);
    border-radius: 24px;
    padding: 0 30px;
    color: white;
    box-shadow: 0 16px 34px rgba(22, 60, 44, 0.16);
    min-height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-bottom: 22px;
}

.ips-stats-title {
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 0;
}

.ips-stat-card {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 18px 16px;
    text-align: center;
    height: 100%;
}

.ips-stat-value {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 6px;
    color: white;
}

.ips-stat-label {
    font-size: 13px;
    color: rgba(255,255,255,0.88);
    font-weight: 600;
}

.ips-cta {
    background: linear-gradient(135deg, rgba(255,255,255,0.88) 0%, rgba(248,245,234,0.92) 100%);
    color: var(--ips-green-dark);
    padding: 34px 36px;
    border-radius: 24px;
    text-align: center;
    border: 1px solid rgba(47, 107, 71, 0.12);
    box-shadow: var(--ips-shadow);
}

.ips-cta-title {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 10px;
}

.ips-cta-sub {
    font-size: 18px;
    color: #536256;
    margin-bottom: 12px;
}

.ips-cta-extra {
    font-size: 15px;
    color: #5a675d;
    line-height: 1.75;
    max-width: 900px;
    margin: 0 auto 18px auto;
}

.ips-footer {
    text-align: center;
    color: #5f6e62;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 8px;
}

div[data-testid="stButton"] > button {
    border-radius: 14px !important;
    font-weight: 700 !important;
    border: 1px solid rgba(47, 107, 71, 0.12) !important;
    background: #fffaf0 !important;
    color: var(--ips-green-dark) !important;
    box-shadow: 0 8px 18px rgba(22, 60, 44, 0.08) !important;
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
    .ips-stats-title,
    .ips-cta-title {
        font-size: 26px;
    }

    .ips-nav-btn div[data-testid="stButton"] > button {
        height: 48px;
        font-size: 14px !important;
        border-radius: 14px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LANGUAGE STATE
# ======================================================
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# ======================================================
# PAGE STATE
# ======================================================
if "main_nav_selected" not in st.session_state:
    st.session_state["main_nav_selected"] = "Home"

# ======================================================
# HEADER
# ======================================================
col1, col2 = st.columns([8, 2])
with col2:
    lang_label = "EN / BM" if st.session_state.lang == "BM" else "BM / EN"
    if st.button(lang_label):
        st.session_state.lang = "BM" if st.session_state.lang == "EN" else "EN"
        st.rerun()

# ======================================================
# INLINE NAVBAR
# ======================================================
nav_items = ["Home", "About", "FAQ", "Login"]

with st.container(border=False):
    nav_cols = st.columns(len(nav_items), gap="small")
    selected = st.session_state["main_nav_selected"]

    for col, label in zip(nav_cols, nav_items):
        with col:
            is_active = selected == label
            active_class = "active" if is_active else ""
            st.markdown(f'<div class="ips-nav-btn {active_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state["main_nav_selected"] = label
                selected = label
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

selected = st.session_state["main_nav_selected"]

# ======================================================
# HOME
# ======================================================
if selected == "Home":
    lang = st.session_state.lang

    st.markdown('<div class="ips-shell">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ips-hero">
        <div class="ips-badge">Digital Agriculture Platform</div>
        <div class="ips-title">{TEXT[lang]['title']}</div>
        <div class="ips-subtitle">{TEXT[lang]['subtitle']}</div>
        <div class="ips-desc">{TEXT[lang]['hero_desc']}</div>
        <div class="ips-chip-row">
            <span class="ips-chip">🌾 Paddy Monitoring</span>
            <span class="ips-chip">📋 Officer Decision Support</span>
            <span class="ips-chip">🤝 Farmer Connectivity</span>
            <span class="ips-chip">📈 Sustainable Agriculture</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="ips-card">
            <div class="ips-card-title">{TEXT[lang]['monitoring_title']}</div>
            <div class="ips-card-text">{TEXT[lang]['monitoring_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="ips-card">
            <div class="ips-card-title">{TEXT[lang]['insights_title']}</div>
            <div class="ips-card-text">{TEXT[lang]['insights_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="ips-card">
            <div class="ips-card-title">{TEXT[lang]['ecosystem_title']}</div>
            <div class="ips-card-text">{TEXT[lang]['ecosystem_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ips-section-card">
        <div class="ips-section-title">{TEXT[lang]['overview_title']}</div>
        <div class="ips-section-text">{TEXT[lang]['overview_desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)

    with p1:
        st.markdown(f"""
        <div class="ips-mini-card">
            <div class="ips-mini-title">🦠 {TEXT[lang]['pillar_1_title']}</div>
            <div class="ips-mini-text">{TEXT[lang]['pillar_1_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="ips-mini-card">
            <div class="ips-mini-title">🧑‍💼 {TEXT[lang]['pillar_2_title']}</div>
            <div class="ips-mini-text">{TEXT[lang]['pillar_2_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown(f"""
        <div class="ips-mini-card">
            <div class="ips-mini-title">🌍 {TEXT[lang]['pillar_3_title']}</div>
            <div class="ips-mini-text">{TEXT[lang]['pillar_3_desc']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ips-stats-wrap">
        <div class="ips-stats-title">{TEXT[lang]['stats_title']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="ips-stat-card">
            <div class="ips-stat-value">{TEXT[lang]['stat_1_value']}</div>
            <div class="ips-stat-label">{TEXT[lang]['stat_1_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="ips-stat-card">
            <div class="ips-stat-value">{TEXT[lang]['stat_2_value']}</div>
            <div class="ips-stat-label">{TEXT[lang]['stat_2_label']}</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="ips-stat-card">
            <div class="ips-stat-value">{TEXT[lang]['stat_3_value']}</div>
            <div class="ips-stat-label">{TEXT[lang]['stat_3_label']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ips-cta">
        <div class="ips-cta-title">{TEXT[lang]['main_cta']}</div>
        <div class="ips-cta-sub">{TEXT[lang]['sub_cta']}</div>
        <div class="ips-cta-extra">{TEXT[lang]['cta_panel_desc']}</div>
        <div><b>{TEXT[lang]['cta']}</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ips-footer">
        {TEXT[lang]['footer']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PAGE ROUTING
# ======================================================
elif selected == "About":
    st.switch_page("pages/1_About.py")

elif selected == "FAQ":
    st.switch_page("pages/2_FAQ.py")

elif selected == "Login":
    st.switch_page("pages/3_Login.py")