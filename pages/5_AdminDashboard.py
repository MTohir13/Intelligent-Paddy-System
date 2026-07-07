import io
import textwrap
import pandas as pd
import streamlit as st
from datetime import datetime
from utils.supabase_db import db

try:
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Admin Dashboard | Intelligence Paddy System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION VALIDATION
# =========================================================
def validate_admin_session():
    is_logged_in = st.session_state.get("logged_in") or st.session_state.get("user_logged_in")
    if not is_logged_in:
        st.error("🔒 Session expired. Please log in again.")
        st.switch_page("pages/3_Login.py")

    user_role = st.session_state.get("role") or st.session_state.get("user_role")
    if user_role != "admin":
        st.error("⛔ Unauthorized access. Admin privileges required.")
        st.switch_page("main.py")


validate_admin_session()


# =========================================================
# HELPERS
# =========================================================
def safe_dt(value):
    if not value:
        return "-"
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(value)


def status_label(is_active):
    return "Active" if is_active else "Suspended"


def render_status_chip(is_active):
    if is_active:
        st.markdown(
            """
            <span style="
                display:inline-block;
                padding:6px 14px;
                border-radius:999px;
                background:#e8f5e9;
                color:#1b5e20;
                font-weight:700;
                font-size:13px;
            ">Active</span>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <span style="
                display:inline-block;
                padding:6px 14px;
                border-radius:999px;
                background:#ffebee;
                color:#b71c1c;
                font-weight:700;
                font-size:13px;
            ">Suspended</span>
            """,
            unsafe_allow_html=True,
        )


def log_admin_action(action, description, metadata=None):
    db.log_activity(
        user_id=st.session_state.get("user_id"),
        email=st.session_state.get("email"),
        action=action,
        description=description,
        metadata=metadata or {}
    )


def _clean_pdf_value(value):
    if pd.isna(value):
        return "-"
    text = str(value).strip()
    return text if text else "-"


def _estimate_col_widths(df, available_width, min_width=48, max_width=220):
    estimated = []
    for col in df.columns:
        header_len = len(str(col))
        max_cell_len = df[col].astype(str).map(len).max() if not df.empty else 0
        char_len = max(header_len, min(max_cell_len, 60))
        width = min(max(min_width, char_len * 5.2), max_width)
        estimated.append(width)

    total_width = sum(estimated)
    if total_width > available_width and total_width > 0:
        scale = available_width / total_width
        estimated = [max(min_width, w * scale) for w in estimated]

    return estimated


def build_pdf_report(title: str, subtitle: str, df: pd.DataFrame):
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()

    page_size = landscape(A3)
    left_margin = 18
    right_margin = 18
    top_margin = 20
    bottom_margin = 20

    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin
    )

    page_width = page_size[0]
    available_width = page_width - left_margin - right_margin

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.fontSize = 20
    title_style.leading = 24

    normal_style = styles["Normal"]

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=normal_style,
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=10,
        leading=12
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=normal_style,
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=8.6,
        textColor=colors.white,
        alignment=0,
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=normal_style,
        fontSize=6.6,
        leading=8.2,
        textColor=colors.HexColor("#222222"),
        alignment=0,
        wordWrap="CJK",
    )

    elements = []
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 8))

    if df.empty:
        elements.append(Paragraph("No data available.", normal_style))
    else:
        pdf_df = df.copy().fillna("-")

        for col in pdf_df.columns:
            pdf_df[col] = pdf_df[col].apply(_clean_pdf_value)

        col_widths = _estimate_col_widths(pdf_df, available_width)

        table_data = []
        table_data.append([Paragraph(str(col), header_style) for col in pdf_df.columns])

        for _, row in pdf_df.iterrows():
            table_data.append([
                Paragraph(_clean_pdf_value(row[col]), cell_style)
                for col in pdf_df.columns
            ])

        table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1,
            splitByRow=1
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b5e20")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.30, colors.HexColor("#c7d4c7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f5f9f5")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def render_category_card(category_name: str, image_url: str | None):
    if image_url:
        image_html = f'<img src="{image_url}" style="width:100%;height:220px;object-fit:cover;border-radius:14px;display:block;">'
    else:
        image_html = """
<div style="
    width:100%;
    height:220px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#f5f7f5;
    border-radius:14px;
    color:#7a7a7a;
    font-size:13px;
    text-align:center;
">
    No image available
</div>
""".strip()

    html = f"""
<div class="report-photo-card">
    {image_html}
    <div style="
        font-size:15px;
        font-weight:800;
        color:#1b5e20;
        margin-top:12px;
        text-align:center;
        line-height:1.35;
    ">
        {category_name}
    </div>
</div>
"""
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)


def get_farmer_activity_logs(limit=200):
    try:
        response = (
            db.service_client.table("activity_logs_farmer")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.warning(f"Failed to load farmer activity logs: {e}")
        return []


def lookup_profile_url(selected_user_row):
    # Try existing combined dataframe fields first
    profile_url = (
        selected_user_row.get("profile_image_url")
        or selected_user_row.get("profile_img_link")
        or selected_user_row.get("profile_img_url")
        or ""
    )
    if str(profile_url).strip():
        return str(profile_url).strip()

    # Officer fallback: query officers table directly using code/email/id
    try:
        if selected_user_row.get("user_type") == "officer":
            code = selected_user_row.get("code", "")
            email = selected_user_row.get("email", "")
            user_id = selected_user_row.get("id", "")

            query = db.service_client.table("officers").select("profile_img_link")

            response = None
            if user_id:
                response = query.eq("id", user_id).limit(1).execute()
            elif code:
                response = query.eq("officer_id", code).limit(1).execute()
            elif email:
                response = query.eq("email", email).limit(1).execute()

            if response and response.data:
                direct_url = response.data[0].get("profile_img_link")
                if direct_url:
                    return str(direct_url).strip()
    except Exception:
        pass

    # Farmer fallback: query users table directly
    try:
        if selected_user_row.get("user_type") == "farmer":
            user_id = selected_user_row.get("id", "")
            email = selected_user_row.get("email", "")

            query = db.service_client.table("users").select("profile_image_url")

            response = None
            if user_id:
                response = query.eq("id", user_id).limit(1).execute()
            elif email:
                response = query.eq("email", email).limit(1).execute()

            if response and response.data:
                direct_url = response.data[0].get("profile_image_url")
                if direct_url:
                    return str(direct_url).strip()
    except Exception:
        pass

    return ""


def render_profile_box(profile_url, user_name):
    if profile_url and str(profile_url).strip():
        st.markdown(
            f"""
            <div class="profile-preview-box">
                <img src="{profile_url}" class="profile-preview-img">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        first_char = str(user_name).strip()[:1].upper() if user_name else "U"
        st.markdown(
            f"""
            <div class="profile-preview-box profile-preview-placeholder">
                <div class="profile-preview-avatar">{first_char}</div>
                <div class="profile-preview-text">No profile image</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# STYLES
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f7fbf7 0%, #eef6ef 100%);
    }

    .block-container {
        padding-top: 3.4rem !important;
        padding-bottom: 2.2rem !important;
    }

    .hero-card {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        color: white;
        border-radius: 26px;
        padding: 34px 32px;
        box-shadow: 0 12px 32px rgba(27,94,32,0.18);
        margin-top: 1rem;
        margin-bottom: 18px;
    }

    .metric-card {
        background: rgba(255,255,255,0.92);
        border-radius: 18px;
        padding: 20px;
        border: 1px solid #e6eee6;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        min-height: 128px;
    }

    .section-shell {
        background: rgba(255,255,255,0.82);
        border: 1px solid #e9f0e9;
        box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        border-radius: 22px;
        padding: 18px;
        margin-top: 1rem;
        margin-bottom: 14px;
    }

    .mini-title {
        color: #687076;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .big-number {
        font-size: 34px;
        font-weight: 800;
        color: #1b5e20;
        line-height: 1.1;
    }

    .mini-sub {
        color: #8a9499;
        font-size: 13px;
        margin-top: 10px;
    }

    .user-card-shell {
        background: linear-gradient(180deg, #ffffff 0%, #f9fcf9 100%);
        border-radius: 25px;
        padding: 22px;
        border: 1px solid #e8efe8;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        min-height: 270px;
    }

    .user-name {
        font-size: 28px;
        font-weight: 800;
        color: #1b5e20;
        line-height: 1.2;
    }

    .user-meta {
        font-size: 15px;
        color: #5f6b63;
        margin-top: 8px;
        line-height: 1.9;
    }

    .profile-preview-box {
    width: 100%;
    height: 240px;

    border-radius: 20px;
    border: 1px solid #e0e9e0;
    background: #f5faf5;

    overflow: hidden;

    display: flex;
    align-items: center;
    justify-content: center;

    margin-top: -40px;
   }

    .profile-preview-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
    }

    .profile-box-lift {
        margin-top: -20px;
    }

    .profile-preview-placeholder {
        flex-direction: column;
        gap: 12px;
    }

    .profile-preview-avatar {
        width: 74px;
        height: 74px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1b5e20 0%, #43a047 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        font-weight: 800;
        box-shadow: 0 10px 24px rgba(27,94,32,0.18);
    }

    .profile-preview-text {
        color: #6d786f;
        font-size: 13px;
        font-weight: 600;
    }

    .report-photo-card {
        background: #ffffff;
        border: 1px solid #e7eee7;
        border-radius: 18px;
        padding: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        min-height: 290px;
        height: 100%;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
    }

    .stDownloadButton > button {
        border-radius: 12px;
        font-weight: 700;
    }

    div[data-baseweb="tab-list"] {
        gap: 10px;
    }

    button[data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 10px 16px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================
stats = db.get_system_stats()
farmers = db.get_all_farmers_with_users()
officers = db.get_all_officers_with_users()
reports = db.get_all_detection_history()
officer_logs = db.get_officer_activity_logs(limit=200)
farmer_logs = get_farmer_activity_logs(limit=200)


# =========================================================
# HEADER
# =========================================================
top1, top2 = st.columns([4.5, 1.1], gap="large")

with top1:
    hero_html = f"""
<div class="hero-card">
    <div style="font-size:18px;font-weight:700;opacity:0.9;">🌾 Intelligence Paddy System</div>
    <div style="font-size:36px;font-weight:800;margin-top:4px;">Agricultural Administration Dashboard</div>
    <div style="font-size:15px;opacity:0.92;margin-top:12px;line-height:1.6;">
        View detection history, manage farmer and officer accounts, monitor account access,
        and generate clean PDF reports from real Supabase data.
    </div>
</div>
"""
    st.markdown(textwrap.dedent(hero_html).strip(), unsafe_allow_html=True)

with top2:
    right_html = f"""
<div class="section-shell" style="padding:20px;">
    <div style="font-size:13px;color:#687076;">Logged in as</div>
    <div style="font-size:18px;font-weight:800;color:#1b5e20;margin-top:6px;">
        {st.session_state.get('full_name', 'Administrator')}
    </div>
    <div style="font-size:13px;color:#7b868c;margin-top:4px;word-break:break-word;">
        {st.session_state.get('email', 'admin@paddy.com')}
    </div>
    <div style="margin-top:12px;">
        <span style="background:#e8f5e9;color:#1b5e20;padding:6px 12px;border-radius:999px;font-weight:700;font-size:12px;">
            ADMIN
        </span>
    </div>
</div>
"""
    st.markdown(textwrap.dedent(right_html).strip(), unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        log_admin_action("LOGOUT", "Admin logged out of the system")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("main.py")


# =========================================================
# OVERVIEW
# =========================================================
st.markdown("## Dashboard Overview")

m1, m2, m3, m4, m5 = st.columns(5, gap="medium")

with m1:
    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
    <div class="mini-title">Total Farmers</div>
    <div class="big-number">{stats.get('total_farmers', 0)}</div>
    <div class="mini-sub">Registered farmer accounts</div>
</div>
""").strip(), unsafe_allow_html=True)

with m2:
    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
    <div class="mini-title">Total Officers</div>
    <div class="big-number">{stats.get('total_officers', 0)}</div>
    <div class="mini-sub">Agricultural officers</div>
</div>
""").strip(), unsafe_allow_html=True)

with m3:
    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
    <div class="mini-title">Detection Reports</div>
    <div class="big-number">{stats.get('total_reports', 0)}</div>
    <div class="mini-sub">All submitted detections</div>
</div>
""").strip(), unsafe_allow_html=True)

with m4:
    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
    <div class="mini-title">Active Accounts</div>
    <div class="big-number">{stats.get('active_users', 0)}</div>
    <div class="mini-sub">Currently allowed access</div>
</div>
""").strip(), unsafe_allow_html=True)

with m5:
    st.markdown(textwrap.dedent(f"""
<div class="metric-card">
    <div class="mini-title">Suspended Accounts</div>
    <div class="big-number">{stats.get('suspended_users', 0)}</div>
    <div class="mini-sub">Currently blocked users</div>
</div>
""").strip(), unsafe_allow_html=True)

st.markdown("---")


# =========================================================
# MAIN TABS
# =========================================================
tab_reports, tab_users, tab_logs = st.tabs([
    "📄 Detection History",
    "👥 Users",
    "📝 Activity Logs"
])


# =========================================================
# TAB 1 - DETECTION HISTORY
# =========================================================
with tab_reports:
    st.markdown("### Detection History")

    report_df = pd.DataFrame(reports)

    if report_df.empty:
        st.info("No detection history found in Supabase.")
    else:
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            report_search = st.text_input(
                "Search detection history",
                placeholder="Farmer, disease, region, area, report ID",
                key="report_search"
            )

        with c2:
            disease_options = ["All"] + sorted(
                [d for d in report_df["disease"].dropna().unique().tolist() if d]
            ) if "disease" in report_df.columns else ["All"]
            selected_disease = st.selectbox("Disease", disease_options, key="selected_disease")

        with c3:
            region_options = ["All"] + sorted(
                [r for r in report_df["region"].dropna().unique().tolist() if r]
            ) if "region" in report_df.columns else ["All"]
            selected_region = st.selectbox("Region", region_options, key="selected_region")

        with c4:
            status_options = ["All"] + sorted(
                [s for s in report_df["status"].dropna().unique().tolist() if s]
            ) if "status" in report_df.columns else ["All"]
            selected_status = st.selectbox("Status", status_options, key="selected_status")

        filtered_report_df = report_df.copy()

        if report_search:
            search_lower = report_search.lower()
            filtered_report_df = filtered_report_df[
                filtered_report_df.astype(str).apply(
                    lambda row: row.str.lower().str.contains(search_lower, na=False).any(),
                    axis=1
                )
            ]

        if selected_disease != "All" and "disease" in filtered_report_df.columns:
            filtered_report_df = filtered_report_df[filtered_report_df["disease"] == selected_disease]

        if selected_region != "All" and "region" in filtered_report_df.columns:
            filtered_report_df = filtered_report_df[filtered_report_df["region"] == selected_region]

        if selected_status != "All" and "status" in filtered_report_df.columns:
            filtered_report_df = filtered_report_df[filtered_report_df["status"] == selected_status]

        display_report_df = filtered_report_df.copy()
        if "created_at" in display_report_df.columns:
            display_report_df["created_at"] = display_report_df["created_at"].apply(safe_dt)

        report_columns = [
            col for col in [
                "report_id", "farmer_id", "farmer_name", "disease", "confidence",
                "status", "region", "area", "summary", "advice",
                "likely_issue", "officer_followup_note", "created_at"
            ] if col in display_report_df.columns
        ]

        st.dataframe(
            display_report_df[report_columns],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Detection Photo Preview by Category")

        category_order = [
            "Bacterial Leaf Blight",
            "Blast",
            "Brown Spot",
            "Healthy",
            "Leaf Scald",
            "Sheath Blight"
        ]

        preview_source_df = report_df.copy()

        if "disease" in preview_source_df.columns:
            preview_cols = st.columns(6, gap="small")

            for idx, category in enumerate(category_order):
                with preview_cols[idx]:
                    category_rows = preview_source_df[
                        preview_source_df["disease"].fillna("").str.strip().str.lower() == category.lower()
                    ]

                    image_url = None
                    if not category_rows.empty:
                        preview_row = category_rows.iloc[0]
                        image_url = preview_row.get("image_url")

                    render_category_card(category, image_url)

        st.markdown("<div style='margin-top:22px;'></div>", unsafe_allow_html=True)

        pdf_df = display_report_df.copy()
        pdf_export_columns = [
            col for col in [
                "report_id", "farmer_id", "farmer_name", "disease",
                "confidence", "status", "region", "area", "summary", "created_at"
            ] if col in pdf_df.columns
        ]

        if REPORTLAB_AVAILABLE:
            pdf_bytes = build_pdf_report(
                title="Intelligence Paddy System - Detection History Report",
                subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                df=pdf_df[pdf_export_columns]
            )
            st.download_button(
                "📄 Download Detection History PDF",
                data=pdf_bytes,
                file_name="detection_history_report.pdf",
                mime="application/pdf",
                key="download_detection_pdf"
            )
        else:
            st.warning("PDF export requires reportlab. Install it using: pip install reportlab")


# =========================================================
# TAB 2 - USERS
# =========================================================
with tab_users:
    st.markdown("### User Management")

    farmer_df = pd.DataFrame(farmers)
    officer_df = pd.DataFrame(officers)

    combined_users = []
    if not farmer_df.empty:
        combined_users.extend(farmer_df.to_dict("records"))
    if not officer_df.empty:
        combined_users.extend(officer_df.to_dict("records"))

    user_df = pd.DataFrame(combined_users)

    if user_df.empty:
        st.info("No users found.")
    else:
        u1, u2, u3 = st.columns(3)

        with u1:
            user_search = st.text_input(
                "Search user",
                placeholder="Name, email, code, region",
                key="user_search"
            )

        with u2:
            type_options = ["All", "farmer", "officer"]
            selected_user_type = st.selectbox("User Type", type_options, key="selected_user_type")

        with u3:
            region_options = ["All"] + sorted(
                [r for r in user_df["region"].dropna().unique().tolist() if r]
            ) if "region" in user_df.columns else ["All"]
            selected_user_region = st.selectbox("Region", region_options, key="selected_user_region")

        filtered_user_df = user_df.copy()

        if user_search:
            search_lower = user_search.lower()
            filtered_user_df = filtered_user_df[
                filtered_user_df.astype(str).apply(
                    lambda row: row.str.lower().str.contains(search_lower, na=False).any(),
                    axis=1
                )
            ]

        if selected_user_type != "All":
            filtered_user_df = filtered_user_df[filtered_user_df["user_type"] == selected_user_type]

        if selected_user_region != "All":
            filtered_user_df = filtered_user_df[filtered_user_df["region"] == selected_user_region]

        display_user_df = filtered_user_df.copy()
        display_user_df["status"] = display_user_df["is_active"].apply(status_label)
        display_user_df["created_at"] = display_user_df["created_at"].apply(safe_dt)
        display_user_df["last_login"] = display_user_df["last_login"].apply(safe_dt)

        st.dataframe(
            display_user_df[[
                "user_type", "code", "name", "email", "phone",
                "region", "area", "status", "last_login", "created_at"
            ]],
            use_container_width=True,
            hide_index=True
        )

        if not filtered_user_df.empty:
            user_options = [
                f"{row['name']} ({row['code']}) - {row['user_type'].title()} - {status_label(row['is_active'])}"
                for _, row in filtered_user_df.iterrows()
            ]

            selected_user_option = st.selectbox(
                "Select user to manage",
                user_options,
                key="selected_user_to_manage"
            )

            selected_code = selected_user_option.split("(")[-1].split(")")[0].strip()
            selected_user_row = filtered_user_df[filtered_user_df["code"] == selected_code].iloc[0]

            profile_url = lookup_profile_url(selected_user_row)

            c_manage1, c_manage2 = st.columns([3.2, 1], gap="large")

            with c_manage1:
                with st.container(border=True):
                    st.markdown("<div style='padding:14px 10px 14px 10px;'></div>", unsafe_allow_html=True)
                    info_col, image_col = st.columns([2.6, 1], gap="large")

                    with info_col:
                        st.markdown(
                            f"""
                            <div class="user-name">{selected_user_row['name']}</div>
                            <div class="user-meta">
                                {selected_user_row['user_type'].title()} • {selected_user_row['code']}<br>
                                {selected_user_row['email']}<br>
                                Region: {selected_user_row.get('region', '-')} | Area: {selected_user_row.get('area', '-')}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                        render_status_chip(bool(selected_user_row["is_active"]))

                    with image_col:
                        st.markdown('<div class="profile-box-lift">', unsafe_allow_html=True)
                        render_profile_box(profile_url, selected_user_row.get("name", "User"))
                        st.markdown('</div>', unsafe_allow_html=True)

            with c_manage2:
                st.markdown("#### Account Action")
                action_label = "Suspend User" if selected_user_row["is_active"] else "Activate User"
                if st.button(action_label, type="primary", use_container_width=True, key="toggle_selected_user"):
                    new_status = not bool(selected_user_row["is_active"])
                    success = db.update_user_status(selected_user_row["id"], new_status)

                    if success:
                        log_admin_action(
                            "UPDATE_USER_STATUS",
                            f"{'Activated' if new_status else 'Suspended'} {selected_user_row['user_type']} {selected_user_row['name']} ({selected_user_row['code']})",
                            {
                                "user_type": selected_user_row["user_type"],
                                "code": selected_user_row["code"],
                                "new_status": new_status
                            }
                        )
                        st.success(f"User status updated to {status_label(new_status)}.")
                        st.rerun()
                    else:
                        st.error("Failed to update user status.")

                if REPORTLAB_AVAILABLE:
                    single_user_pdf_df = pd.DataFrame([{
                        "User Type": selected_user_row["user_type"],
                        "Code": selected_user_row["code"],
                        "Name": selected_user_row["name"],
                        "Email": selected_user_row["email"],
                        "Phone": selected_user_row.get("phone", "-"),
                        "Region": selected_user_row.get("region", "-"),
                        "Area": selected_user_row.get("area", "-"),
                        "Status": status_label(bool(selected_user_row["is_active"])),
                        "Last Login": safe_dt(selected_user_row.get("last_login")),
                    }])

                    user_pdf = build_pdf_report(
                        title="Intelligence Paddy System - User Profile Report",
                        subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        df=single_user_pdf_df
                    )

                    st.download_button(
                        "📄 Download User PDF",
                        data=user_pdf,
                        file_name=f"{selected_user_row['code']}_profile_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_single_user_pdf"
                    )

                if st.button("Refresh Users", use_container_width=True, key="refresh_users"):
                    st.rerun()


# =========================================================
# TAB 3 - ACTIVITY LOGS
# =========================================================
with tab_logs:
    st.markdown("### Activity Logs")

    log_choice = st.radio(
        "Choose log source",
        ["Officer Logs", "Farmer Logs"],
        horizontal=True
    )

    if log_choice == "Officer Logs":
        officer_log_df = pd.DataFrame(officer_logs)

        if officer_log_df.empty:
            st.info("No officer logs found.")
        else:
            officer_log_df["created_at"] = officer_log_df["created_at"].apply(safe_dt)
            st.dataframe(
                officer_log_df[["created_at", "officer_id", "officer_name", "action", "description"]],
                use_container_width=True,
                hide_index=True
            )

            if REPORTLAB_AVAILABLE:
                officer_log_pdf = build_pdf_report(
                    title="Intelligence Paddy System - Officer Activity Logs",
                    subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    df=officer_log_df[["created_at", "officer_id", "officer_name", "action", "description"]]
                )
                st.download_button(
                    "📄 Download Officer Logs PDF",
                    data=officer_log_pdf,
                    file_name="officer_logs_report.pdf",
                    mime="application/pdf",
                    key="download_officer_logs_pdf"
                )

    else:
        farmer_log_df = pd.DataFrame(farmer_logs)

        if farmer_log_df.empty:
            st.info("No farmer logs found.")
        else:
            farmer_log_df["created_at"] = farmer_log_df["created_at"].apply(safe_dt)
            st.dataframe(
                farmer_log_df[["created_at", "farmer_id", "farmer_name", "action", "description"]],
                use_container_width=True,
                hide_index=True
            )

            if REPORTLAB_AVAILABLE:
                farmer_log_pdf = build_pdf_report(
                    title="Intelligence Paddy System - Farmer Activity Logs",
                    subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    df=farmer_log_df[["created_at", "farmer_id", "farmer_name", "action", "description"]]
                )
                st.download_button(
                    "📄 Download Farmer Logs PDF",
                    data=farmer_log_pdf,
                    file_name="farmer_logs_report.pdf",
                    mime="application/pdf",
                    key="download_farmer_logs_pdf"
                )


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center;color:#7f8a80;padding:10px 0 28px 0;">
        Intelligence Paddy System • Admin Dashboard • Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """,
    unsafe_allow_html=True
)