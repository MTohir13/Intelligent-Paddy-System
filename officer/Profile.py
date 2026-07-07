import base64
import mimetypes
import os
import time
from urllib.parse import urlparse

import streamlit as st

from utils.supabase_db import db

BUCKET_NAME = "officer-profile-images"
DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
DISPLAY_DEPARTMENT = "Department Of Agriculture"

# =====================================================
# EDIT BACKGROUND IMAGE PATH HERE
# =====================================================
PROFILE_BACKGROUND = "assets/Background3.jpg"


# =====================================================
# BACKGROUND HELPER
# =====================================================
def set_profile_background(image_path=PROFILE_BACKGROUND):
    if not image_path or not os.path.exists(image_path):
        return

    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        print(f"set_profile_background error: {e}")


# =====================================================
# SESSION / ACTIVITY HELPERS
# =====================================================
def get_current_officer_info():
    officer_id = st.session_state.get("officer_id")
    officer_name = st.session_state.get("officer_name") or st.session_state.get("full_name")

    if officer_id and officer_name:
        return officer_id, officer_name

    user_id = st.session_state.get("user_id")
    if not user_id:
        return None, None

    try:
        response = (
            db.service_client.table("officers")
            .select("officer_id, officer_name")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if response.data:
            officer_id = response.data.get("officer_id")
            officer_name = response.data.get("officer_name")

            if officer_id:
                st.session_state["officer_id"] = officer_id
            if officer_name:
                st.session_state["officer_name"] = officer_name

            return officer_id, officer_name
    except Exception as e:
        print(f"get_current_officer_info error: {e}")

    return None, None


def log_officer_activity(action, description):
    officer_id, officer_name = get_current_officer_info()

    if not officer_id or not officer_name:
        return False

    try:
        (
            db.client.table("activity_logs_officer")
            .insert(
                {
                    "officer_id": officer_id,
                    "officer_name": officer_name,
                    "action": action,
                    "description": description,
                }
            )
            .execute()
        )
        return True
    except Exception as e:
        print(f"log_officer_activity error: {e}")
        return False


def log_profile_view_once(user_id):
    session_key = f"profile_view_logged_{user_id}"
    if st.session_state.get(session_key):
        return

    log_officer_activity(
        action="VIEW_PROFILE",
        description="Viewed officer profile page",
    )
    st.session_state[session_key] = True


# =====================================================
# DATA HELPERS
# =====================================================
def get_officer_profile(user_id, user_email, user_name):
    try:
        officer_response = (
            db.service_client.table("officers")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        user_response = (
            db.service_client.table("users")
            .select("full_name, phone, region, profile_image_url, email")
            .eq("id", user_id)
            .execute()
        )

        officer = officer_response.data[0] if officer_response.data else {}
        user_data = user_response.data[0] if user_response.data else {}

        if not officer and not user_data:
            return None

        return {
            "id": user_id,
            "officer_id": officer.get("officer_id", f"OFF-{user_id[:8].upper()}"),
            "officer_name": officer.get("officer_name") or user_data.get("full_name", user_name),
            "region": officer.get("region") or user_data.get("region", ""),
            "role": officer.get("role", "officer"),
            "phone": officer.get("phone") or user_data.get("phone", ""),
            "email": officer.get("email") or user_data.get("email") or user_email,
            "profile_img_link": officer.get("profile_img_link") or user_data.get("profile_image_url"),
        }

    except Exception as e:
        st.error(f"Error loading officer profile: {str(e)}")
        return None


def upload_profile_image(user_id, uploaded_file):
    try:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower() or ".jpg"
        mime_type = uploaded_file.type or mimetypes.guess_type(uploaded_file.name)[0] or "image/jpeg"
        file_path = f"{user_id}/profile_{int(time.time())}{file_ext}"
        file_bytes = uploaded_file.getvalue()

        db.service_client.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_bytes,
            file_options={
                "content-type": mime_type,
                "upsert": "true",
            },
        )

        public_url = db.service_client.storage.from_(BUCKET_NAME).get_public_url(file_path)
        return public_url

    except Exception as e:
        st.error(f"Image upload failed: {str(e)}")
        return None


def extract_storage_path_from_url(public_url):
    try:
        parsed = urlparse(public_url)
        marker = f"/storage/v1/object/public/{BUCKET_NAME}/"
        full_path = parsed.path
        idx = full_path.find(marker)
        if idx == -1:
            return None
        return full_path[idx + len(marker):]
    except Exception:
        return None


def delete_profile_image_from_storage(public_url):
    try:
        if not public_url:
            return True

        file_path = extract_storage_path_from_url(public_url)
        if not file_path:
            return False

        db.service_client.storage.from_(BUCKET_NAME).remove([file_path])
        return True

    except Exception as e:
        st.error(f"Image delete failed: {str(e)}")
        return False


def update_officer_profile(user_id, officer_name, phone, profile_img_link=None, clear_image=False):
    try:
        officer_update = {
            "officer_name": officer_name,
            "phone": phone,
            "updated_at": "now()",
        }

        user_update = {
            "full_name": officer_name,
            "phone": phone,
            "updated_at": "now()",
        }

        if clear_image:
            officer_update["profile_img_link"] = None
            user_update["profile_image_url"] = None
        elif profile_img_link is not None:
            officer_update["profile_img_link"] = profile_img_link
            user_update["profile_image_url"] = profile_img_link

        officer_response = (
            db.service_client.table("officers")
            .update(officer_update)
            .eq("id", user_id)
            .execute()
        )

        user_response = (
            db.service_client.table("users")
            .update(user_update)
            .eq("id", user_id)
            .execute()
        )

        return bool(officer_response.data) and bool(user_response.data)

    except Exception as e:
        st.error(f"Profile update failed: {str(e)}")
        return False


# =====================================================
# UI STYLES
# =====================================================
def inject_profile_styles():
    st.markdown(
        """
        <style>
        :root {
            --gov-bg: #f5f8f6;
            --gov-surface-strong: rgba(255, 255, 255, 0.96);
            --gov-border: rgba(15, 65, 36, 0.14);
            --gov-text: #123524;
            --gov-text-soft: #5c6d62;
            --gov-green: #14532d;
            --gov-green-2: #1f7a45;
            --gov-chip: #e8f5e9;
            --gov-shadow: 0 20px 48px rgba(15, 23, 42, 0.12);
            --gov-radius-xl: 30px;
            --gov-radius-lg: 24px;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(67,160,71,0.06), transparent 28%),
                linear-gradient(180deg, #f7faf8 0%, #f1f6f3 100%);
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1.55rem !important;
            padding-bottom: 2.2rem !important;
        }

        .profile-hero {
            background:
                linear-gradient(135deg, rgba(10,56,32,0.98) 0%, rgba(20,83,45,0.96) 42%, rgba(39,119,63,0.94) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: var(--gov-radius-xl);
            padding: 28px 32px;
            color: white;
            box-shadow: 0 24px 56px rgba(15, 81, 50, 0.20);
            margin-bottom: 18px;
            position: relative;
            overflow: hidden;
        }

        .profile-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(120deg, rgba(255,255,255,0.06), transparent 40%),
                radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 34%);
            pointer-events: none;
        }

        .profile-hero::after {
            content: "";
            position: absolute;
            top: -72px;
            right: -58px;
            width: 230px;
            height: 230px;
            background: rgba(255,255,255,0.07);
            border-radius: 50%;
        }

        .profile-hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.14);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 14px;
            position: relative;
            z-index: 2;
            backdrop-filter: blur(8px);
        }

        .profile-hero-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.06;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
            letter-spacing: -0.02em;
        }

        .profile-hero-subtitle {
            font-size: 15px;
            line-height: 1.7;
            color: rgba(255,255,255,0.92);
            position: relative;
            z-index: 2;
            max-width: 860px;
        }

        .profile-layout-gap [data-testid="stColumn"] {
            padding-top: 0.05rem;
        }

        .profile-single-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(244,249,246,0.97) 100%);
            border: 1px solid rgba(20, 83, 45, 0.16);
            border-radius: var(--gov-radius-lg);
            box-shadow: 0 22px 50px rgba(15, 23, 42, 0.12);
            padding: 22px 18px 20px 18px;
            text-align: center;
            min-height: 100%;
            position: relative;
            overflow: hidden;
            max-width: 560px;
            margin: 0 auto;
        }

        .profile-single-card::after {
            content: "";
            position: absolute;
            left: 22px;
            right: 22px;
            bottom: 0;
            height: 4px;
            border-radius: 999px;
            background: linear-gradient(90deg, #dcedd8 0%, #8acb97 100%);
        }

        .profile-avatar-wrapper {
            width: 148px;
            height: 148px;
            margin: 0 auto 12px auto;
            border-radius: 50%;
            padding: 6px;
            background: linear-gradient(135deg, #d8efde, #79c28b);
            box-shadow: 0 18px 36px rgba(34, 139, 34, 0.16);
        }

        .profile-avatar {
            width: 136px;
            height: 136px;
            object-fit: cover;
            border-radius: 50%;
            background: white;
            display: block;
        }

        .profile-name {
            font-size: 22px;
            font-weight: 800;
            color: var(--gov-text);
            margin-top: 4px;
            line-height: 1.18;
            letter-spacing: -0.01em;
        }

        .profile-id {
            font-size: 14px;
            color: #58705f;
            margin-top: 8px;
            font-weight: 700;
        }

        .profile-role-badge {
            display: inline-block;
            margin-top: 14px;
            padding: 8px 14px;
            border-radius: 999px;
            background: var(--gov-chip);
            color: #166534;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            border: 1px solid rgba(22, 101, 52, 0.08);
        }

        .profile-card {
            background: rgba(255,255,255,0.96);
            border: 1px solid var(--gov-border);
            border-radius: var(--gov-radius-lg);
            box-shadow: var(--gov-shadow);
            padding: 24px 24px 22px 24px;
            min-height: 100%;
        }

        .section-title {
            font-size: 24px;
            font-weight: 800;
            color: var(--gov-text);
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .section-subtitle {
            font-size: 14px;
            color: #4e6256;
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-top: 4px;
            margin-bottom: 20px;
        }

        .info-tile {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 18px;
            padding: 15px 16px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .info-tile:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 26px rgba(15, 23, 42, 0.06);
        }

        .info-label {
            font-size: 11.5px;
            font-weight: 800;
            color: #728378;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 9px;
        }

        .info-value {
            font-size: 16px;
            font-weight: 700;
            color: var(--gov-text);
            word-break: break-word;
            line-height: 1.5;
        }

        .locked-note {
            background: linear-gradient(180deg, #edf6ef 0%, #e5f1e8 100%);
            border: 1px solid rgba(20, 83, 45, 0.15);
            border-radius: 16px;
            padding: 13px 15px;
            color: #244634;
            font-size: 13px;
            margin-top: 2px;
            margin-bottom: 14px;
            line-height: 1.65;
            font-weight: 700;
        }

        .picture-title-box {
            background: linear-gradient(180deg, #f4faf5 0%, #edf7ef 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 18px;
            padding: 14px 16px;
            margin-top: 8px;
            margin-bottom: 10px;
        }

        .picture-title-text {
            font-size: 15px;
            font-weight: 800;
            color: var(--gov-text);
        }

        div[data-testid="stTextInput"] label p,
        div[data-testid="stFileUploader"] label p,
        div[data-testid="stCheckbox"] label p {
            font-weight: 800 !important;
            color: #123524 !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stFileUploader"] section,
        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border: 1px solid rgba(20, 83, 45, 0.14) !important;
            background: rgba(255,255,255,0.98) !important;
            box-shadow: none !important;
            color: #123524 !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: rgba(27, 122, 68, 0.55) !important;
            box-shadow: 0 0 0 3px rgba(67, 160, 71, 0.10) !important;
        }

        .stFileUploader {
            margin-top: 0.1rem !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            height: 46px;
            border-radius: 14px !important;
            font-weight: 700 !important;
            border: 1px solid rgba(20, 83, 45, 0.10) !important;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05) !important;
        }

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            background: linear-gradient(135deg, #14532d 0%, #1f7a45 100%) !important;
            color: white !important;
            border: none !important;
        }

        /* REAL green card: target the actual Streamlit form */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 26px !important;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34) !important;
            padding: 24px 24px 20px 24px !important;
            backdrop-filter: blur(2px) !important;
        }

        div[data-testid="stForm"] .section-title {
            color: #f4fff7 !important;
        }

        div[data-testid="stForm"] .section-subtitle {
            color: rgba(240,255,244,0.88) !important;
        }

        div[data-testid="stForm"] .locked-note {
            background: linear-gradient(180deg, rgba(236,247,239,0.98) 0%, rgba(226,241,230,0.98) 100%) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #204231 !important;
        }

        div[data-testid="stForm"] .picture-title-box {
            background: linear-gradient(180deg, rgba(236,247,239,0.98) 0%, rgba(226,241,230,0.98) 100%) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
        }

        div[data-testid="stForm"] .picture-title-text {
            color: #163625 !important;
        }

        div[data-testid="stForm"] div[data-testid="stTextInput"] label p,
        div[data-testid="stForm"] div[data-testid="stFileUploader"] label p,
        div[data-testid="stForm"] div[data-testid="stCheckbox"] label p {
            color: #f4fff7 !important;
            font-weight: 800 !important;
        }

        .mini-kpi-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 14px;
        }

        .mini-kpi {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 12px 14px;
            position: relative;
            z-index: 2;
        }

        .mini-kpi-label {
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.80);
            font-weight: 800;
            margin-bottom: 6px;
        }

        .mini-kpi-value {
            font-size: 15px;
            font-weight: 700;
            color: white;
            line-height: 1.4;
        }

        @media (max-width: 1100px) {
            .mini-kpi-row {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 900px) {
            .info-grid {
                grid-template-columns: 1fr;
            }

            .profile-hero-title {
                font-size: 30px;
            }

            .profile-avatar-wrapper {
                width: 136px;
                height: 136px;
            }

            .profile-avatar {
                width: 124px;
                height: 124px;
            }

            .profile-single-card {
                max-width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# VIEW MODE
# =====================================================
def render_real_profile(officer_data):
    image_url = officer_data.get("profile_img_link") or DEFAULT_AVATAR

    st.markdown(
        f"""
        <div class="profile-hero">
            <div class="profile-hero-kicker">Officer Identity Center</div>
            <div class="profile-hero-title">Officer Profile</div>
            <div class="profile-hero-subtitle">
                Enterprise-grade officer identity panel for reviewing official account details,
                regional assignment, and profile credentials in one secure workspace.
            </div>
            <div class="mini-kpi-row">
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Officer ID</div>
                    <div class="mini-kpi-value">{officer_data.get("officer_id", "N/A")}</div>
                </div>
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Region</div>
                    <div class="mini-kpi-value">{officer_data.get("region", "N/A")}</div>
                </div>
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Department</div>
                    <div class="mini-kpi-value">{DISPLAY_DEPARTMENT}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="profile-layout-gap">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.02, 1.78], gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="profile-single-card">
                <div class="profile-avatar-wrapper">
                    <img src="{image_url}" class="profile-avatar" alt="Officer Profile Picture">
                </div>
                <div class="profile-name">{officer_data.get("officer_name", "Officer")}</div>
                <div class="profile-id">{officer_data.get("officer_id", "N/A")}</div>
                <div class="profile-role-badge">{officer_data.get("role", "officer")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="profile-card">
                <div class="section-title">Official Profile Details</div>
                <div class="section-subtitle">
                    Verified officer information synchronized with the live officer profile record.
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="info-grid">
                <div class="info-tile">
                    <div class="info-label">Officer ID</div>
                    <div class="info-value">{officer_data.get("officer_id", "N/A")}</div>
                </div>
                <div class="info-tile">
                    <div class="info-label">Full Name</div>
                    <div class="info-value">{officer_data.get("officer_name", "N/A")}</div>
                </div>
                <div class="info-tile">
                    <div class="info-label">Region</div>
                    <div class="info-value">{officer_data.get("region", "N/A")}</div>
                </div>
                <div class="info-tile">
                    <div class="info-label">Phone Number</div>
                    <div class="info-value">{officer_data.get("phone", "N/A") or "N/A"}</div>
                </div>
                <div class="info-tile">
                    <div class="info-label">Email</div>
                    <div class="info-value">{officer_data.get("email", "N/A")}</div>
                </div>
                <div class="info-tile">
                    <div class="info-label">Department</div>
                    <div class="info-value">{DISPLAY_DEPARTMENT}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("✏️ Edit Profile", use_container_width=True, type="primary"):
                st.session_state.editing_profile = True
                st.rerun()

        with col_b:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# =====================================================
# EDIT MODE
# =====================================================
def render_edit_profile(officer_data):
    image_url = officer_data.get("profile_img_link") or DEFAULT_AVATAR

    st.markdown(
        f"""
        <div class="profile-hero">
            <div class="profile-hero-kicker">Officer Identity Center</div>
            <div class="profile-hero-title">Edit Officer Profile</div>
            <div class="profile-hero-subtitle">
                Securely update your officer display name, phone number, and profile image while
                preserving locked administrative fields and official region assignment.
            </div>
            <div class="mini-kpi-row">
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Officer ID</div>
                    <div class="mini-kpi-value">{officer_data.get("officer_id", "N/A")}</div>
                </div>
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Region</div>
                    <div class="mini-kpi-value">{officer_data.get("region", "N/A")}</div>
                </div>
                <div class="mini-kpi">
                    <div class="mini-kpi-label">Status</div>
                    <div class="mini-kpi-value">Editable Session</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="profile-layout-gap">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.02, 1.78], gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="profile-single-card">
                <div class="profile-avatar-wrapper">
                    <img src="{image_url}" class="profile-avatar" alt="Current Officer Profile Picture">
                </div>
                <div class="profile-name">{officer_data.get("officer_name", "Officer")}</div>
                <div class="profile-id">{officer_data.get("officer_id", "N/A")}</div>
                <div class="profile-role-badge">Editable Profile</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        with st.form("edit_profile_form", clear_on_submit=False):
            st.markdown(
                """
                <div class="section-title">Update Officer Information</div>
                <div class="section-subtitle">
                    Only editable profile fields are available below. Locked operational fields remain protected.
                </div>
                <div class="locked-note">Region is locked and cannot be changed from this page.</div>
                """,
                unsafe_allow_html=True,
            )

            officer_name = st.text_input(
                "Officer Name",
                value=officer_data.get("officer_name", ""),
                placeholder="Enter officer name",
            )

            st.text_input(
                "Region",
                value=officer_data.get("region", ""),
                disabled=True,
            )

            phone = st.text_input(
                "Phone Number",
                value=officer_data.get("phone", ""),
                placeholder="Enter phone number",
            )

            st.text_input(
                "Email",
                value=officer_data.get("email", ""),
                disabled=True,
            )

            st.markdown(
                """
                <div class="picture-title-box">
                    <div class="picture-title-text">Profile Picture Management</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                "Upload a new profile image",
                type=["jpg", "jpeg", "png", "webp"],
            )

            current_image = officer_data.get("profile_img_link")
            remove_current_image = st.checkbox("Delete current profile picture")

            col_save, col_cancel = st.columns(2)

            with col_save:
                submit_button = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True,
                    type="primary",
                )

            with col_cancel:
                cancel_button = st.form_submit_button(
                    "↩️ Cancel",
                    use_container_width=True,
                )

        if cancel_button:
            st.session_state.editing_profile = False
            st.rerun()

        if submit_button:
            if not officer_name.strip():
                st.error("Officer name is required.")
                return

            original_name = str(officer_data.get("officer_name", "") or "")
            original_phone = str(officer_data.get("phone", "") or "")
            current_image = officer_data.get("profile_img_link")

            profile_img_link = None
            clear_image = False
            uploaded_new_image = False
            removed_existing_image = False

            if remove_current_image and current_image:
                with st.spinner("Removing current profile image..."):
                    deleted = delete_profile_image_from_storage(current_image)
                    if not deleted:
                        st.error("Failed to remove current profile image from storage.")
                        return
                    clear_image = True
                    removed_existing_image = True

            if uploaded_file is not None:
                with st.spinner("Uploading profile image..."):
                    profile_img_link = upload_profile_image(officer_data["id"], uploaded_file)
                    if not profile_img_link:
                        return
                    clear_image = False
                    uploaded_new_image = True

            with st.spinner("Updating profile..."):
                success = update_officer_profile(
                    user_id=officer_data["id"],
                    officer_name=officer_name.strip(),
                    phone=phone.strip(),
                    profile_img_link=profile_img_link,
                    clear_image=clear_image,
                )

            if success:
                st.session_state.full_name = officer_name.strip()
                st.session_state.officer_name = officer_name.strip()
                st.session_state.editing_profile = False

                if uploaded_new_image:
                    log_officer_activity(
                        action="UPLOAD_PROFILE_IMAGE",
                        description="Uploaded a new officer profile image",
                    )

                if removed_existing_image:
                    log_officer_activity(
                        action="REMOVE_PROFILE_IMAGE",
                        description="Removed officer profile image",
                    )

                if officer_name.strip() != original_name or phone.strip() != original_phone:
                    changes = []
                    if officer_name.strip() != original_name:
                        changes.append(f"name from '{original_name}' to '{officer_name.strip()}'")
                    if phone.strip() != original_phone:
                        changes.append(f"phone from '{original_phone}' to '{phone.strip()}'")

                    log_officer_activity(
                        action="UPDATE_PROFILE",
                        description=f"Updated officer profile: {', '.join(changes)}",
                    )

                if (
                    officer_name.strip() == original_name
                    and phone.strip() == original_phone
                    and not uploaded_new_image
                    and not removed_existing_image
                ):
                    log_officer_activity(
                        action="UPDATE_PROFILE",
                        description="Saved profile with no changes",
                    )

                st.success("✅ Profile updated successfully.")
                st.rerun()
            else:
                st.error("Failed to update profile.")


# =====================================================
# MAIN PAGE
# =====================================================
def render_profile_page():
    inject_profile_styles()
    set_profile_background()

    if "email" not in st.session_state or "user_id" not in st.session_state:
        st.error("Please log in first.")
        return

    user_id = st.session_state.get("user_id")
    user_email = st.session_state.get("email")
    user_name = st.session_state.get("full_name", "Officer")

    if "editing_profile" not in st.session_state:
        st.session_state.editing_profile = False

    log_profile_view_once(user_id)

    with st.spinner("Loading profile..."):
        officer_data = get_officer_profile(user_id, user_email, user_name)

    if not officer_data:
        st.error("Could not load officer profile.")
        return

    if st.session_state.get("editing_profile"):
        render_edit_profile(officer_data)
    else:
        render_real_profile(officer_data)