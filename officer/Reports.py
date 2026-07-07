import base64
import json
import os
import textwrap

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import Point, shape

from utils.supabase_db import db


# =========================================================
# BACKGROUND IMAGE
# =========================================================
REPORTS_BACKGROUND = "assets/Background3.jpg"


def set_reports_background(image_path=REPORTS_BACKGROUND):
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
        print(f"set_reports_background error: {e}")


# =========================================================
# STYLING
# =========================================================
def inject_reports_css():
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

        .reports-hero {
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

        .reports-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(120deg, rgba(255,255,255,0.06), transparent 40%),
                radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 34%);
            pointer-events: none;
        }

        .reports-hero::after {
            content: "";
            position: absolute;
            top: -72px;
            right: -58px;
            width: 230px;
            height: 230px;
            background: rgba(255,255,255,0.07);
            border-radius: 50%;
        }

        .reports-hero-kicker {
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

        .reports-hero-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.06;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
            letter-spacing: -0.02em;
        }

        .reports-hero-subtitle {
            font-size: 15px;
            line-height: 1.7;
            color: rgba(255,255,255,0.92);
            position: relative;
            z-index: 2;
            max-width: 860px;
        }

        .refresh-button-wrap {
            margin-top: 74px;
        }

        .master-title {
            font-size: 24px;
            font-weight: 800;
            color: #f4fff7;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .master-subtitle {
            font-size: 14px;
            color: rgba(240,255,244,0.88);
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        .region-banner {
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

        .metric-card {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 18px;
            padding: 18px 18px 16px 18px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            min-height: 122px;
        }

        .metric-title {
            font-size: 11.5px;
            font-weight: 800;
            color: #728378;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 9px;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: var(--gov-text);
            line-height: 1;
            margin-bottom: 10px;
        }

        .metric-caption {
            font-size: 14px;
            color: #5c6d62;
            line-height: 1.55;
            font-weight: 600;
        }

        .white-card-title {
            font-size: 24px;
            font-weight: 800;
            color: #f4fff7;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .white-card-subtitle {
            font-size: 14px;
            color: rgba(240,255,244,0.88);
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        .cream-card-title {
            font-size: 24px;
            font-weight: 800;
            color: #123524;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .cream-card-subtitle {
            font-size: 14px;
            color: #4e6256;
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        .section-header-box {
            background: linear-gradient(180deg, #f4faf5 0%, #edf7ef 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 18px;
            padding: 14px 16px;
            margin-top: 8px;
            margin-bottom: 10px;
        }

        .section-header-title {
            font-size: 15px;
            font-weight: 800;
            color: var(--gov-text);
            margin-bottom: 4px;
        }

        .section-header-subtitle {
            font-size: 13px;
            color: #4e6256;
            line-height: 1.6;
            font-weight: 600;
        }

        .table-shell {
            background: linear-gradient(180deg, #ffffff 0%, #f8fcfa 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(16,59,45,0.07);
            padding: 14px 18px 10px 18px;
            margin-bottom: 6px;
        }

        .table-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 20px;
            margin-bottom: 8px;
        }

        .table-title {
            font-size: 22px;
            font-weight: 800;
            color: var(--gov-text);
            margin-bottom: 6px;
            letter-spacing: -0.02em;
        }

        .table-subtitle {
            font-size: 14px;
            color: #4e6256;
            line-height: 1.6;
            font-weight: 600;
        }

        .table-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 8px 12px;
            border-radius: 999px;
            background: var(--gov-chip);
            border: 1px solid rgba(22, 101, 52, 0.08);
            color: #166534;
            font-size: 12px;
            font-weight: 800;
            white-space: nowrap;
        }

        .detail-label {
            font-size: 11.5px;
            font-weight: 800;
            color: rgba(230,245,236,0.78);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 9px;
        }

        .detail-value {
            font-size: 16px;
            font-weight: 700;
            color: white;
            word-break: break-word;
            line-height: 1.5;
            margin-bottom: 1rem;
        }

        .summary-box {
            background: linear-gradient(180deg, #f7fbf8 0%, #f1f8f3 100%);
            border: 1px solid rgba(16,59,45,0.08);
            border-radius: 16px;
            padding: 14px 15px;
            color: #23483a;
            line-height: 1.75;
            margin-top: 8px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.32);
        }

        .status-pill {
            display: inline-block;
            padding: 0.40rem 0.88rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.2px;
        }

        .status-review {
            background: rgba(37, 99, 235, 0.14);
            color: #dbe8ff;
            border: 1px solid rgba(255,255,255,0.14);
        }

        .status-high {
            background: rgba(220, 38, 38, 0.18);
            color: #ffe0e0;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .status-validated {
            background: rgba(22, 163, 74, 0.18);
            color: #ddffe7;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .status-flagged {
            background: rgba(234, 88, 12, 0.18);
            color: #ffe8da;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .status-resolved {
            background: rgba(8, 145, 178, 0.18);
            color: #def9ff;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .status-default {
            background: rgba(255,255,255,0.10);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.12);
        }

        .risk-note {
            color: #ffe2e2;
            font-weight: 800;
            font-size: 0.92rem;
            margin-top: 12px;
        }

        .image-frame,
        .location-map-frame {
            background: linear-gradient(180deg, #f4faf5 0%, #edf7ef 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 18px;
            padding: 14px 16px 16px 16px;
            margin-top: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .report-selector-note {
            color: #204231;
            font-size: 13px;
            margin-top: -2px;
            margin-bottom: 12px;
            line-height: 1.6;
            background: linear-gradient(180deg, #edf6ef 0%, #e5f1e8 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 14px;
            padding: 12px 14px;
            font-weight: 600;
        }

        .workspace-grid {
            margin-top: 8px;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stDataEditor"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(16,59,45,0.08);
            box-shadow: 0 10px 28px rgba(16,59,45,0.06);
            background: rgba(255,255,255,0.99) !important;
        }

        div[data-testid="stDataEditor"] [data-testid="stWidgetLabel"] {
            display: none;
        }

        div[data-testid="stDataEditor"] thead th {
            background: #f4f8f5 !important;
            color: #204231 !important;
            font-weight: 800 !important;
            border-bottom: 1px solid rgba(20,83,45,0.08) !important;
        }

        div[data-testid="stDataEditor"] tbody tr:nth-child(even) {
            background: rgba(248,251,249,0.70) !important;
        }

        div[data-testid="stDataEditor"] tbody tr:hover {
            background: rgba(233,245,236,0.78) !important;
        }

        div[data-testid="stSelectbox"] label p,
        div[data-testid="stTextInput"] label p,
        div[data-testid="stTextArea"] label p {
            font-weight: 800 !important;
            color: #ffffff !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border: 1px solid rgba(20,83,45,0.14) !important;
            background: rgba(255,255,255,0.98) !important;
            box-shadow: none !important;
            color: #123524 !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: rgba(27,122,68,0.55) !important;
            box-shadow: 0 0 0 3px rgba(67,160,71,0.10) !important;
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

        /* TARGETED OUTER REPORT CONTAINERS */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.reports-green-marker),
        div[data-testid="stVerticalBlock"]:has(.reports-green-marker) {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 26px !important;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34) !important;
            padding: 20px 20px 18px 20px !important;
            backdrop-filter: blur(2px) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.reports-cream-marker),
        div[data-testid="stVerticalBlock"]:has(.reports-cream-marker) {
            background: #f5efe6 !important;
            border: 1px solid rgba(20, 83, 45, 0.12) !important;
            border-radius: 26px !important;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08) !important;
            padding: 20px 20px 18px 20px !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.reports-green-marker) > div,
        div[data-testid="stVerticalBlock"]:has(.reports-green-marker) > div,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.reports-cream-marker) > div,
        div[data-testid="stVerticalBlock"]:has(.reports-cream-marker) > div {
            background: transparent !important;
        }

        /* green action form */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, rgba(10,56,32,0.98) 0%, rgba(20,83,45,0.96) 42%, rgba(39,119,63,0.94) 100%) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 22px !important;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.26) !important;
            padding: 18px 18px 14px 18px !important;
        }

        div[data-testid="stForm"] .white-card-title,
        div[data-testid="stForm"] .white-card-subtitle,
        div[data-testid="stForm"] label p {
            color: white !important;
        }

        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.96) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(15,65,36,0.08) !important;
        }

        @media (max-width: 1100px) {
            .reports-hero-title {
                font-size: 30px;
            }

            .refresh-button-wrap {
                margin-top: 0;
            }

            .table-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# ACTIVITY LOG HELPERS
# =========================================================
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


def get_current_officer_region():
    region = st.session_state.get("region")
    if region:
        return str(region).strip()

    user_id = st.session_state.get("user_id")
    if not user_id:
        return None

    try:
        response = (
            db.service_client.table("officers")
            .select("region")
            .eq("id", user_id)
            .single()
            .execute()
        )

        if response.data:
            region = response.data.get("region")
            if region:
                st.session_state["region"] = region
                return str(region).strip()
    except Exception as e:
        print(f"get_current_officer_region error: {e}")

    return None


def log_officer_activity(action, description):
    officer_id, officer_name = get_current_officer_info()

    if not officer_id or not officer_name:
        return False

    try:
        (
            db.service_client.table("activity_logs_officer")
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


def log_report_view_once(row):
    detection_id = str(row.get("id", ""))
    if not detection_id:
        return

    session_key = f"viewed_report_{detection_id}"
    if st.session_state.get(session_key):
        return

    farmer_name = row.get("farmer_name", "Unknown Farmer")
    farmer_id = row.get("farmer_id_display", "N/A")
    disease = row.get("disease", "Unknown")
    status = normalize_status(row.get("status", "UNDER_REVIEW"))

    log_officer_activity(
        action="VIEW_REPORT",
        description=(
            f"Viewed detection report {detection_id} for farmer {farmer_name} "
            f"({farmer_id}) - disease: {disease}, status: {status}"
        ),
    )

    st.session_state[session_key] = True


# =========================================================
# DB HELPERS
# =========================================================
def fetch_all_rows(table_name, columns="*", page_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + page_size - 1
        response = (
            db.service_client.table(table_name)
            .select(columns)
            .range(start, end)
            .execute()
        )

        data = response.data or []
        if not data:
            break

        all_rows.extend(data)

        if len(data) < page_size:
            break

        start += page_size

    return all_rows


def normalize_status(status):
    raw = str(status or "").strip().upper()

    if raw in {"VALIDATED"}:
        return "VALIDATED"
    if raw in {"FLAGGED"}:
        return "FLAGGED"
    if raw in {"HIGH_RISK", "HIGH RISK", "HIGH-RISK"}:
        return "HIGH_RISK"
    if raw in {"RESOLVED"}:
        return "RESOLVED"
    if raw in {"UNDER_REVIEW", "UNDER REVIEW", "REVIEWING"}:
        return "UNDER_REVIEW"

    if raw in {"PENDING", "CLOSED", ""}:
        return "UNDER_REVIEW"

    return "UNDER_REVIEW"


def normalize_region(value):
    return str(value).strip().lower() if value is not None else ""


def build_report_option_label(row):
    report_id = str(row.get("report_id") or row.get("detection_id_display") or "N/A")
    disease = str(row.get("disease") or "Unknown")
    created_at = str(row.get("created_at_display") or "N/A")
    status = normalize_status(row.get("status"))
    return f"{report_id} | {disease} | {status} | {created_at}"


def find_farmer_assigned_field(lat, lon):
    """Find paddy field polygon that contains the given coordinates"""
    try:
        # Load paddy fields data
        paddy_fields_path = "assets/paddy_fields.geojson"
        if not os.path.exists(paddy_fields_path):
            return None
        
        with open(paddy_fields_path, "r", encoding="utf-8") as f:
            paddy_data = json.load(f)
        
        clicked_point = Point(lon, lat)
        
        for feature in paddy_data.get("features", []):
            try:
                polygon = shape(feature.get("geometry"))
                if polygon.contains(clicked_point):
                    return feature
            except Exception:
                continue
                
        return None
    except Exception as e:
        print(f"find_farmer_assigned_field error: {e}")
        return None


def update_detection_location(detection_id, lat, lon):
    """Update detection location in database"""
    try:
        response = (
            db.service_client.table("detection_history")
            .update({
                "detection_latitude": lat,
                "detection_longitude": lon,
            })
            .eq("id", detection_id)
            .execute()
        )
        return True if response else False
    except Exception as e:
        print(f"update_detection_location error: {e}")
        return False


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(ttl=30, show_spinner=False)
def load_report_data():
    detection_rows = fetch_all_rows(
        "detection_history",
        """
        id,
        user_id,
        disease,
        confidence,
        advice,
        image_url,
        created_at,
        status,
        summary,
        likely_issue,
        immediate_actions,
        prevention_tips,
        monitoring_advice,
        retake_photo_tip,
        officer_followup_note,
        report_id,
        farmer_name,
        farmer_id,
        region,
        area,
        detection_latitude,
        detection_longitude
        """
    )

    farmer_rows = fetch_all_rows(
        "farmers",
        """
        id,
        email,
        full_name,
        farmer_id,
        role,
        region,
        area,
        created_at,
        updated_at,
        latitude,
        longitude
        """
    )

    user_rows = fetch_all_rows(
        "users",
        """
        id,
        email,
        full_name,
        phone,
        region,
        role_id,
        created_at,
        updated_at,
        profile_image_url
        """
    )

    df_detection = pd.DataFrame(detection_rows)
    df_farmers = pd.DataFrame(farmer_rows)
    df_users = pd.DataFrame(user_rows)

    if df_detection.empty:
        return pd.DataFrame()

    if df_farmers.empty:
        df_farmers = pd.DataFrame(columns=["id", "full_name", "farmer_id", "region", "area", "email", "latitude", "longitude"])

    if df_users.empty:
        df_users = pd.DataFrame(columns=["id", "full_name", "region", "email"])

    df_farmers = df_farmers.rename(
        columns={
            "id": "farmer_user_id",
            "full_name": "farmer_full_name",
            "email": "farmer_email",
            "region": "farmer_region",
            "area": "farmer_area",
            "farmer_id": "farmer_id_profile",
            "latitude": "farmer_latitude",
            "longitude": "farmer_longitude",
        }
    )

    df_users = df_users.rename(
        columns={
            "id": "user_ref_id",
            "full_name": "user_full_name",
            "email": "user_email",
            "region": "user_region",
        }
    )

    df = df_detection.merge(
        df_farmers,
        how="left",
        left_on="user_id",
        right_on="farmer_user_id",
    )

    df = df.merge(
        df_users,
        how="left",
        left_on="user_id",
        right_on="user_ref_id",
    )

    df["farmer_name"] = (
        df["farmer_name"]
        .fillna(df["farmer_full_name"])
        .fillna(df["user_full_name"])
        .fillna("Unknown Farmer")
    )

    df["farmer_id_display"] = (
        df["farmer_id"]
        .fillna(df["farmer_id_profile"])
        .fillna("N/A")
    )

    df["region_display"] = (
        df["region"]
        .fillna(df["farmer_region"])
        .fillna(df["user_region"])
        .fillna("N/A")
    )

    df["area_display"] = (
        df["area"]
        .fillna(df["farmer_area"])
        .fillna("N/A")
    )

    df["disease"] = df["disease"].fillna("Unknown")
    df["status"] = df["status"].apply(normalize_status)
    df["summary"] = df["summary"].fillna(df["advice"]).fillna("No summary available.")
    df["officer_followup_note"] = df["officer_followup_note"].fillna("")

    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0)
    df["confidence_pct"] = (df["confidence"] * 100).round(2)

    df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["created_at_display"] = df["created_at_dt"].dt.strftime("%d %b %Y, %I:%M %p")
    df["created_at_display"] = df["created_at_display"].fillna("N/A")

    df["detection_id_display"] = df["id"].astype(str)
    df["report_option_label"] = df.apply(build_report_option_label, axis=1)

    df = df.sort_values(by="created_at_dt", ascending=False, na_position="last").reset_index(drop=True)

    return df


# =========================================================
# REGION FILTER
# =========================================================
def filter_reports_by_officer_region(df):
    officer_region = get_current_officer_region()

    if df.empty:
        return df, officer_region

    if not officer_region:
        return df.iloc[0:0].copy(), officer_region

    officer_region_norm = normalize_region(officer_region)
    filtered_df = df[df["region_display"].apply(normalize_region) == officer_region_norm].copy()
    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df, officer_region


# =========================================================
# UPDATE ACTION
# =========================================================
def update_report_action(detection_id, new_status, followup_note):
    try:
        response = (
            db.service_client.table("detection_history")
            .update(
                {
                    "status": normalize_status(new_status),
                    "officer_followup_note": followup_note.strip()
                }
            )
            .eq("id", detection_id)
            .execute()
        )

        load_report_data.clear()
        return True if response else False

    except Exception as e:
        st.error(f"Failed to update report: {e}")
        return False


# =========================================================
# UI HELPERS
# =========================================================
def render_status_badge(status):
    status_upper = normalize_status(status)

    if status_upper == "HIGH_RISK":
        css = "status-pill status-high"
    elif status_upper == "VALIDATED":
        css = "status-pill status-validated"
    elif status_upper == "FLAGGED":
        css = "status-pill status-flagged"
    elif status_upper == "RESOLVED":
        css = "status-pill status-resolved"
    elif status_upper == "UNDER_REVIEW":
        css = "status-pill status-review"
    else:
        css = "status-pill status-default"

    st.markdown(
        f'<span class="{css}">{status_upper}</span>',
        unsafe_allow_html=True
    )


def render_metrics(df):
    total_reports = len(df)
    high_risk_count = len(df[df["status"] == "HIGH_RISK"])
    validated_count = len(df[df["status"] == "VALIDATED"])
    flagged_count = len(df[df["status"] == "FLAGGED"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Detection Reports</div>
                <div class="metric-value">{total_reports}</div>
                <div class="metric-caption">Live records from your assigned region</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">High Risk Cases</div>
                <div class="metric-value">{high_risk_count}</div>
                <div class="metric-caption">Urgent intervention required</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Validated Reports</div>
                <div class="metric-value">{validated_count}</div>
                <div class="metric-caption">Reviewed and confirmed by officer</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Flagged Reports</div>
                <div class="metric-value">{flagged_count}</div>
                <div class="metric-caption">Needs further checking</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def apply_filters(df):
    st.markdown(
        """
        <div class="master-title">Report Intelligence Filters</div>
        <div class="master-subtitle">Filter live reports by area, disease, status, or farmer name within your assigned region.</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.1, 1.5])

    area_options = ["All"] + sorted([x for x in df["area_display"].dropna().unique().tolist() if str(x).strip()])
    disease_options = ["All"] + sorted([x for x in df["disease"].dropna().unique().tolist() if str(x).strip()])
    status_options = ["All"] + sorted([str(x).upper() for x in df["status"].dropna().unique().tolist() if str(x).strip()])

    with col1:
        selected_area = st.selectbox("Area (MADA)", area_options)

    with col2:
        selected_disease = st.selectbox("Disease", disease_options)

    with col3:
        selected_status = st.selectbox("Status", status_options)

    with col4:
        search_name = st.text_input("Search Farmer Name", placeholder="Type farmer name...")

    filtered = df.copy()

    if selected_area != "All":
        filtered = filtered[filtered["area_display"] == selected_area]

    if selected_disease != "All":
        filtered = filtered[filtered["disease"] == selected_disease]

    if selected_status != "All":
        filtered = filtered[filtered["status"].astype(str).str.upper() == selected_status]

    if search_name.strip():
        filtered = filtered[
            filtered["farmer_name"].astype(str).str.contains(search_name.strip(), case=False, na=False)
        ]

    return filtered.reset_index(drop=True)


def render_report_table(df):
    st.markdown(
        f"""
        <div class="table-shell">
            <div class="table-header">
                <div>
                    <div class="table-title">Live Detection Report Table</div>
                    <div class="table-subtitle">
                        Cleaner structured report presentation for officer review and monitoring.
                    </div>
                </div>
                <div class="table-chip">{len(df)} record(s)</div>
            </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("No report found based on selected filters.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    display_df = df[
        [
            "image_url",
            "farmer_name",
            "farmer_id_display",
            "region_display",
            "area_display",
            "disease",
            "confidence_pct",
            "status",
            "summary",
            "created_at_display",
            "detection_id_display"
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "image_url": "Image",
            "farmer_name": "Farmer Name",
            "farmer_id_display": "Farmer ID",
            "region_display": "Region",
            "area_display": "Area",
            "disease": "Disease",
            "confidence_pct": "Confidence (%)",
            "status": "Status",
            "summary": "Summary",
            "created_at_display": "Created At",
            "detection_id_display": "Detection ID"
        }
    )

    st.data_editor(
        display_df,
        width="stretch",
        hide_index=True,
        disabled=True,
        column_config={
            "Image": st.column_config.ImageColumn("Image", width="medium"),
            "Confidence (%)": st.column_config.NumberColumn("Confidence (%)", format="%.2f"),
            "Summary": st.column_config.TextColumn("Summary", width="large"),
            "Detection ID": st.column_config.TextColumn("Detection ID", width="large"),
        },
        key="reports_table_live"
    )

    st.markdown("</div>", unsafe_allow_html=True)


def render_detail_row(label, value):
    """Render a labeled detail row with styling"""
    st.markdown(f'<div class="detail-label">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="detail-value">{value}</div>', unsafe_allow_html=True)


def render_detection_location_map(row, farmer_reports):
    """Render map for detection location with farmer assigned field and detection point"""
    
    # Clean coordinate values - handle None, NaN, and invalid values
    def clean_coord(value):
        if value is None or pd.isna(value):
            return None
        try:
            return float(value)
        except Exception:
            return None
    
    # Get farmer's assigned location (from farmers table)
    farmer_lat = clean_coord(row.get("farmer_latitude"))
    farmer_lon = clean_coord(row.get("farmer_longitude"))
    
    # Get detection location for current report
    detection_lat = clean_coord(row.get("detection_latitude"))
    detection_lon = clean_coord(row.get("detection_longitude"))
    
    # Determine center point for map
    if detection_lat and detection_lon:
        center = [detection_lat, detection_lon]
    elif farmer_lat and farmer_lon:
        center = [farmer_lat, farmer_lon]
    else:
        # Region-based fallback centers
        region_centers = {
            "Kota Setar": [6.1248, 100.3678],
            "Kubang Pasu": [6.3230, 100.4200],
            "Pendang": [5.9847, 100.4770],
            "Yan": [5.8080, 100.3760],
            "Padang Terap": [6.2550, 100.6100],
            "Alor Setar": [6.1248, 100.3678],
        }
        
        region_name = row.get("region_display", "")
        center = region_centers.get(region_name, [6.1, 100.5])  # Default Kedah center
    
    # Determine zoom level: closer if farmer has location, wider if using region default
    zoom_level = 13 if not (farmer_lat and farmer_lon) else 16
    
    # Create map
    m = folium.Map(location=center, zoom_start=zoom_level)
    
    # Add farmer's assigned field polygon (blue)
    if farmer_lat and farmer_lon:
        assigned_field = find_farmer_assigned_field(farmer_lat, farmer_lon)
        if assigned_field:
            folium.GeoJson(
                assigned_field,
                name="Farmer Assigned Field",
                style_function=lambda _: {
                    "color": "#2563eb",
                    "weight": 3,
                    "fillColor": "#60a5fa",
                    "fillOpacity": 0.22,
                },
                tooltip=f"Farmer's assigned paddy field"
            ).add_to(m)
        
        # Add farmer marker (blue)
        folium.Marker(
            location=[farmer_lat, farmer_lon],
            popup=f"""
            <b>Farmer's Registered Location</b><br>
            Farmer: {row.get('farmer_name', 'Unknown')}<br>
            ID: {row.get('farmer_id_display', 'N/A')}
            """,
            icon=folium.Icon(color="blue", icon="home", prefix="fa")
        ).add_to(m)
    
    # Show all saved detection points for this selected farmer
    for _, report_row in farmer_reports.iterrows():
        saved_lat = clean_coord(report_row.get("detection_latitude"))
        saved_lon = clean_coord(report_row.get("detection_longitude"))

        if saved_lat and saved_lon:
            popup_html = f"""
            <b>Report ID:</b> {report_row.get('report_id') or report_row.get('detection_id_display', 'N/A')}<br>
            <b>Disease:</b> {report_row.get('disease', 'Unknown')}
            """

            folium.Marker(
                location=[saved_lat, saved_lon],
                popup=popup_html,
                icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa")
            ).add_to(m)
    
    # Add click handler for selecting detection location
    map_data = st_folium(
        m,
        height=400,
        width="100%",
        returned_objects=["last_clicked"],
        key=f"detection_location_map_{row['detection_id_display']}"
    )
    
    if map_data and map_data.get("last_clicked"):
        detection_lat = map_data["last_clicked"]["lat"]
        detection_lon = map_data["last_clicked"]["lng"]

        st.session_state[f"temp_detection_lat_{row['detection_id_display']}"] = detection_lat
        st.session_state[f"temp_detection_lon_{row['detection_id_display']}"] = detection_lon

    detection_lat = st.session_state.get(
        f"temp_detection_lat_{row['detection_id_display']}",
        detection_lat
    )
    detection_lon = st.session_state.get(
        f"temp_detection_lon_{row['detection_id_display']}",
        detection_lon
    )

    if detection_lat and detection_lon:
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 12px;
                padding: 12px 16px;
                color: white;
                font-weight: 800;
                margin-top: 12px;
            ">
                📍 Selected detection location: {detection_lat:.6f}, {detection_lon:.6f}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    return detection_lat, detection_lon


def render_detail_panel(df):
    if df.empty:
        st.info("No report available to review.")
        return

    # Mark as green container
    with st.container(border=True):
        st.markdown('<div class="reports-green-marker"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="white-card-title">Officer Review Workspace</div>
            <div class="white-card-subtitle">Review farmer report details, image evidence, and AI intelligence in one controlled workspace.</div>
            """,
            unsafe_allow_html=True
        )

        farmer_source = (
            df[["farmer_name", "farmer_id_display"]]
            .drop_duplicates()
            .sort_values(by=["farmer_name", "farmer_id_display"])
        )

        farmer_options = [
            f"{row['farmer_name']} ({row['farmer_id_display']})"
            for _, row in farmer_source.iterrows()
        ]

        selected_farmer_option = st.selectbox("Select farmer", farmer_options)

        selected_farmer_name = selected_farmer_option.rsplit(" (", 1)[0]
        selected_farmer_id = selected_farmer_option.rsplit("(", 1)[-1].rstrip(")")

        farmer_reports = df[
            (df["farmer_name"].astype(str) == selected_farmer_name) &
            (df["farmer_id_display"].astype(str) == selected_farmer_id)
        ].copy()

        farmer_reports = farmer_reports.sort_values(by="created_at_dt", ascending=False, na_position="last").reset_index(drop=True)

        report_option_labels = farmer_reports["report_option_label"].tolist()
        selected_report_label = st.selectbox("Select report", report_option_labels)
        row = farmer_reports[farmer_reports["report_option_label"] == selected_report_label].iloc[0]

        log_report_view_once(row)

        if len(farmer_reports) > 1:
            st.markdown(
                f'<div class="report-selector-note">This farmer has <b>{len(farmer_reports)}</b> reports in your assigned region. Choose the exact detection record you want to review or validate.</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="workspace-grid">', unsafe_allow_html=True)
        left, right = st.columns([1.0, 1.28], gap="large")

        with left:
            st.markdown(
                """
                <div class="image-frame">
                    <div class="section-header-title">Detection Image</div>
                    <div class="section-header-subtitle">
                        Captured image submitted by farmer for AI analysis.
                    </div>
                """,
                unsafe_allow_html=True
            )

            if str(row.get("image_url", "")).strip():
                st.image(row["image_url"], use_container_width=True)
            else:
                st.warning("No image available.")

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Detection Location Map Section
            st.markdown(
                """
                <div class="location-map-frame">
                    <div class="section-header-title">Detection Location Map</div>
                    <div class="section-header-subtitle">
                        Click on map to set detection point. Blue polygon = farmer assigned field.
                    </div>
                """,
                unsafe_allow_html=True
            )

            detection_lat, detection_lon = render_detection_location_map(row, farmer_reports)

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Save detection location button
            if detection_lat and detection_lon:
                if st.button("💾 Save Detection Location", key=f"save_location_{row['detection_id_display']}"):
                    if update_detection_location(row["id"], detection_lat, detection_lon):
                        st.success("✅ Detection location saved successfully!")
                        load_report_data.clear()
                        st.session_state.pop(f"temp_detection_lat_{row['detection_id_display']}", None)
                        st.session_state.pop(f"temp_detection_lon_{row['detection_id_display']}", None)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save detection location.")

        with right:
            st.markdown(
                """
                <div class="section-header-box">
                    <div class="section-header-title">Detection Intelligence</div>
                    <div class="section-header-subtitle">Structured AI result with farmer and detection details.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            info_left, info_right = st.columns(2, gap="large")

            with info_left:
                render_detail_row("Farmer Name", row["farmer_name"])
                render_detail_row("Farmer ID", row["farmer_id_display"])
                render_detail_row("Region", row["region_display"])
                render_detail_row("Area", row["area_display"])

            with info_right:
                render_detail_row("Disease", row["disease"])
                render_detail_row("Confidence", f"{row['confidence_pct']:.2f}%")
                st.markdown('<div class="detail-label">Current Status</div>', unsafe_allow_html=True)
                render_status_badge(row["status"])
                st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
                render_detail_row("Created At", row["created_at_display"])

            render_detail_row("Detection ID", row["detection_id_display"])

            st.markdown('<div class="detail-label" style="margin-top:12px;">AI Summary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="summary-box">{row["summary"]}</div>', unsafe_allow_html=True)

            if row["status"] == "HIGH_RISK":
                st.markdown(
                    '<div class="risk-note">⚠ High-risk report detected. Immediate officer monitoring recommended.</div>',
                    unsafe_allow_html=True
                )

            with st.expander("See full AI advisory details"):
                st.write("**Likely Issue:**", row.get("likely_issue", "N/A"))
                st.write("**Immediate Actions:**", row.get("immediate_actions", "N/A"))
                st.write("**Prevention Tips:**", row.get("prevention_tips", "N/A"))
                st.write("**Monitoring Advice:**", row.get("monitoring_advice", "N/A"))
                st.write("**Retake Photo Tip:**", row.get("retake_photo_tip", "N/A"))
                st.write("**Officer Follow-up Note:**", row.get("officer_followup_note", ""))

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mark as cream container
    with st.container(border=True):
        st.markdown('<div class="reports-cream-marker"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="cream-card-title">Officer Action Console</div>
            <div class="cream-card-subtitle">Update the official review status and officer follow-up note for this detection record.</div>
            """,
            unsafe_allow_html=True
        )

        status_choices = [
            "UNDER_REVIEW",
            "VALIDATED",
            "HIGH_RISK",
            "FLAGGED",
            "RESOLVED",
        ]

        current_status = normalize_status(row["status"])
        default_status_index = status_choices.index(current_status) if current_status in status_choices else 0
        original_note = str(row.get("officer_followup_note", "") or "")

        with st.form(f"officer_action_form_{row['detection_id_display']}"):
            c1, c2 = st.columns([1, 2])

            with c1:
                selected_status = st.selectbox("Update Status", status_choices, index=default_status_index)

            with c2:
                note = st.text_area(
                    "Officer Follow-up Note",
                    value=original_note,
                    height=140,
                    placeholder="Write officer action, field verification result, farmer instruction, or monitoring note..."
                )

            submit = st.form_submit_button("Save Officer Action", width="stretch")

            if submit:
                ok = update_report_action(
                    detection_id=row["id"],
                    new_status=selected_status,
                    followup_note=note
                )
                if ok:
                    normalized_old_note = original_note.strip()
                    normalized_new_note = note.strip()

                    if selected_status != current_status:
                        log_officer_activity(
                            action="UPDATE_REPORT_STATUS",
                            description=(
                                f"Updated detection report {row['detection_id_display']} for farmer "
                                f"{row['farmer_name']} ({row['farmer_id_display']}) "
                                f"status from {current_status} to {selected_status}"
                            ),
                        )

                    if normalized_new_note != normalized_old_note:
                        log_officer_activity(
                            action="ADD_FOLLOWUP_NOTE",
                            description=(
                                f"Updated follow-up note for detection report {row['detection_id_display']} "
                                f"for farmer {row['farmer_name']} ({row['farmer_id_display']})"
                            ),
                        )

                    if selected_status == current_status and normalized_new_note == normalized_old_note:
                        log_officer_activity(
                            action="UPDATE_REPORT_STATUS",
                            description=(
                                f"Saved officer action for detection report {row['detection_id_display']} "
                                f"for farmer {row['farmer_name']} ({row['farmer_id_display']}) "
                                f"with no change to status or follow-up note"
                            ),
                        )

                    st.success("Report updated successfully.")
                    st.rerun()


# =========================================================
# PUBLIC RENDER
# =========================================================
def render_reports():
    inject_reports_css()
    set_reports_background()

    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        hero_html = """
        <div class="reports-hero">
            <div class="reports-hero-kicker">Detection Intelligence Center</div>
            <div class="reports-hero-title">Agricultural Detection Report Intelligence Panel</div>
            <div class="reports-hero-subtitle">
                Real-time officer review system powered by detection_history, farmers, and users tables.
                Review submitted detections, inspect farmer images, and manage official officer decisions
                from one professional workspace.
            </div>
        </div>
        """
        st.markdown(textwrap.dedent(hero_html).strip(), unsafe_allow_html=True)

    with header_col2:
        st.markdown('<div class="refresh-button-wrap">', unsafe_allow_html=True)
        if st.button("Refresh Data", width="stretch"):
            load_report_data.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    try:
        df = load_report_data()
        df, officer_region = filter_reports_by_officer_region(df)
    except Exception as e:
        st.error(f"Unable to load report data: {e}")
        return

    if not officer_region:
        st.warning("Officer region not found. Please make sure this officer has a region assigned in the officers table.")
        return

    if df.empty:
        st.warning(f"No detection records found for your assigned region: {officer_region}.")
        return

    # Mark as green container
    with st.container(border=True):
        st.markdown('<div class="reports-green-marker"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="master-title">Regional Detection Overview</div>
            <div class="master-subtitle">Officer dashboard overview for assigned region reports, quick metrics, filters, and live detection history.</div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="region-banner">
                Showing reports for your assigned region: <b>{officer_region}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        render_metrics(df)
        st.markdown("<br>", unsafe_allow_html=True)

        filtered_df = apply_filters(df)
        st.markdown("<br>", unsafe_allow_html=True)

        render_report_table(filtered_df)

    st.markdown("<br>", unsafe_allow_html=True)

    render_detail_panel(filtered_df)