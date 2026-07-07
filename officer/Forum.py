# officer/Forum.py

import base64
import html
import os
from datetime import datetime

import streamlit as st
from utils.supabase_db import db

FORUM_BACKGROUND = "assets/Background3.jpg"


# =====================================================
# BACKGROUND
# =====================================================
def set_forum_background(image_path=FORUM_BACKGROUND):
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
        print(f"set_forum_background error: {e}")


# =====================================================
# UTILS
# =====================================================
def safe_text(value):
    return html.escape(str(value)) if value is not None else ""


def format_time(value):
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %I:%M %p")
    except Exception:
        return str(value)


def log_officer_activity(action, description):
    try:
        current_officer_uuid = str(st.session_state.get("user_id", ""))
        current_officer_name = st.session_state.get("full_name", "Officer")

        officer_code = current_officer_uuid

        try:
            officer_response = (
                db.service_client.table("officers")
                .select("officer_id, officer_name")
                .eq("id", current_officer_uuid)
                .maybe_single()
                .execute()
            )

            if officer_response.data:
                officer_code = (
                    officer_response.data.get("officer_id")
                    or current_officer_uuid
                )
                current_officer_name = (
                    officer_response.data.get("officer_name")
                    or current_officer_name
                )
        except Exception:
            pass

        db.service_client.table("activity_logs_officer").insert({
            "officer_id": officer_code,
            "officer_name": current_officer_name,
            "action": action,
            "description": description,
        }).execute()

    except Exception as e:
        st.warning(f"Activity log failed: {e}")


# =====================================================
# STYLES
# =====================================================
def inject_forum_css():
    st.markdown(
        """
        <style>
        :root {
            --gov-text: #123524;
            --gov-green: #14532d;
            --gov-green-2: #1f7a45;
            --gov-radius-xl: 30px;
            --gov-radius-lg: 24px;
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1.55rem !important;
            padding-bottom: 2.2rem !important;
        }

        .forum-hero {
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

        .forum-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(120deg, rgba(255,255,255,0.06), transparent 40%),
                radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 34%);
            pointer-events: none;
        }

        .forum-hero::after {
            content: "";
            position: absolute;
            top: -72px;
            right: -58px;
            width: 230px;
            height: 230px;
            background: rgba(255,255,255,0.07);
            border-radius: 50%;
        }

        .forum-hero-kicker {
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

        .forum-hero-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.06;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
            letter-spacing: -0.02em;
            color: white;
        }

        .forum-hero-subtitle {
            font-size: 15px;
            line-height: 1.7;
            color: rgba(255,255,255,0.92);
            position: relative;
            z-index: 2;
            max-width: 860px;
            margin-bottom: 14px;
        }

        .forum-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            position: relative;
            z-index: 2;
        }

        .forum-badge {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 800;
            background: rgba(255,255,255,0.16);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.20);
            backdrop-filter: blur(6px);
        }

        /* FORUM MODE CARD - SOLID WHITE */
        .forum-mode-card {
            background: #ffffff;
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            padding: 16px;
            margin-bottom: 10px;
        }

        .forum-mode-title {
            font-size: 20px;
            font-weight: 800;
            color: #123524;
            margin-bottom: 4px;
        }

        .forum-mode-subtitle {
            font-size: 13px;
            color: #64748b;
            margin-bottom: 10px;
        
        }

        /* GREEN SHELLS FOR COMMUNITY AND POST SECTIONS */
        .forum-green-shell {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 26px;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34);
            padding: 24px 24px 20px 24px;
            backdrop-filter: blur(2px);
            margin-bottom: 16px;
        }

        .forum-green-title {
            font-size: 24px;
            font-weight: 800;
            color: #f4fff7;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .forum-green-subtitle {
            font-size: 14px;
            color: rgba(240,255,244,0.88);
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        .forum-panel-title-light {
            color: #f4fff7 !important;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .forum-panel-subtitle-light {
            color: rgba(240,255,244,0.88) !important;
            font-size: 13px;
            margin-bottom: 14px;
            line-height: 1.6;
        }

        /* GREEN SHELLS FOR FARMER SUPPORT SECTIONS */
        .forum-green-side-shell {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 26px;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34);
            padding: 24px 24px 20px 24px;
            backdrop-filter: blur(2px);
            margin-bottom: 16px;
        }

        /* WHITE CHAT SHELL */
        .ips-chat-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(244,249,246,0.97) 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            padding: 16px;
            min-height: 520px;
            max-height: 520px;
            overflow-y: auto;
            scroll-behavior: smooth;
        }

        .forum-delete-wrap {
            margin-top: -2px;
            margin-bottom: 10px;
        }

        .forum-delete-wrap button {
            height: 34px !important;
            min-height: 34px !important;
            padding: 0 12px !important;
            font-size: 12px !important;
        }

        .ips-empty-note {
            background: linear-gradient(180deg, #edf6ef 0%, #e5f1e8 100%);
            border: 1px solid rgba(20, 83, 45, 0.15);
            border-radius: 16px;
            padding: 13px 15px;
            color: #244634;
            font-size: 13px;
            line-height: 1.65;
            font-weight: 700;
            text-align: center;
        }

        /* Message card styling - UPDATED */
        .forum-msg {
            background: #eff6ff;
            border: 1px solid rgba(15, 23, 42, 0.06);
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }

        .forum-msg-user {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 8px;
        }

        .forum-msg-role {
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }

        .forum-msg-meta {
            font-size: 12px;
            color: #64748b;
            margin-bottom: 10px;
        }

        .forum-msg-content {
            color: #1e293b;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 14px;
        }

        .report-pill {
            margin-top: 10px;
            display: inline-block;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid rgba(15,23,42,0.08);
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }

        .forum-action-note {
            font-size: 12px;
            color: rgba(240,255,244,0.82);
            margin-top: 8px;
            line-height: 1.6;
            font-weight: 600;
        }

        .active-chat-box {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 18px;
            padding: 14px;
            margin-top: 12px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }

        .active-chat-label {
            font-size: 12px;
            color: #64748b;
        }

        .active-chat-name {
            font-size: 18px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 4px;
        }

        .active-chat-id {
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }

        .active-chat-region {
            font-size: 12px;
            color: #64748b;
            margin-top: 2px;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 16px !important;
            border: 1px solid rgba(20, 83, 45, 0.14) !important;
            background: #ffffff !important;
            min-height: 120px !important;
            color: #123524 !important;
        }

        div[data-testid="stTextInput"] input {
            border-radius: 14px !important;
            border: 1px solid rgba(20, 83, 45, 0.14) !important;
            background: #ffffff !important;
            color: #123524 !important;
        }

        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 14px !important;
            border: 1px solid rgba(20, 83, 45, 0.14) !important;
            background: #ffffff !important;
        }

        div.stButton > button {
            border-radius: 14px !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 10px 22px rgba(15,23,42,0.05) !important;
            padding-top: 0.70rem !important;
            padding-bottom: 0.70rem !important;
            height: 46px !important;
        }

        .community-post-wrap {
            margin-top: -6px;
        }

        @media (max-width: 900px) {
            .forum-hero-title {
                font-size: 30px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# COMMUNITY HELPERS
# =====================================================
def fetch_community_messages():
    try:
        response = (
            db.service_client.table("community_messages")
            .select("*")
            .order("created_at", desc=False)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading community messages: {e}")
        return []


def insert_community_message(sender_id, sender_name, sender_role, message):
    try:
        payload = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "sender_role": sender_role,
            "message": message,
        }
        response = (
            db.service_client.table("community_messages")
            .insert(payload)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error sending community message: {e}")
        return False


def delete_community_message(message_id, current_officer_id):
    try:
        response = (
            db.service_client.table("community_messages")
            .delete()
            .eq("id", message_id)
            .eq("sender_id", current_officer_id)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error deleting community message: {e}")
        return False


# =====================================================
# FARMER SUPPORT HELPERS
# =====================================================
def get_current_officer_profile(current_officer_uuid):
    try:
        response = (
            db.service_client.table("officers")
            .select("id, officer_id, officer_name")
            .eq("id", current_officer_uuid)
            .maybe_single()
            .execute()
        )
        data = response.data if response.data else None
        if data:
            return {
                "officer_uuid": str(data.get("id", "")),
                "officer_code": data.get("officer_id") or current_officer_uuid,
                "officer_name": data.get("officer_name") or "Officer",
            }
    except Exception as e:
        st.warning(f"Could not load officer profile: {e}")

    return {
        "officer_uuid": current_officer_uuid,
        "officer_code": current_officer_uuid,
        "officer_name": "Officer",
    }


def fetch_farmer_messages(
    selected_farmer_id=None,
    current_officer_id=None,
    current_officer_code=None,
):
    try:
        base_query = (
            db.service_client.table("farmer_support_messages")
            .select("*")
            .order("created_at", desc=False)
        )

        if selected_farmer_id:
            base_query = base_query.eq("farmer_id", selected_farmer_id)

        data = []

        if current_officer_code:
            try:
                code_query = base_query.eq("officer_id", current_officer_code)
                response = code_query.execute()
                data = response.data if response.data else []
            except Exception:
                data = []

        if not data and current_officer_id:
            try:
                uuid_query = (
                    db.service_client.table("farmer_support_messages")
                    .select("*")
                    .order("created_at", desc=False)
                )
                if selected_farmer_id:
                    uuid_query = uuid_query.eq("farmer_id", selected_farmer_id)
                uuid_query = uuid_query.eq("officer_id", current_officer_id)
                response = uuid_query.execute()
                data = response.data if response.data else []
            except Exception:
                data = []

        if not data and selected_farmer_id:
            fallback_query = (
                db.service_client.table("farmer_support_messages")
                .select("*")
                .eq("farmer_id", selected_farmer_id)
                .order("created_at", desc=False)
            )
            fallback_response = fallback_query.execute()
            data = fallback_response.data if fallback_response.data else []

        return data

    except Exception as e:
        st.error(f"Error loading farmer support messages: {e}")
        return []


def insert_farmer_message(
    sender_id,
    sender_role,
    farmer_id,
    farmer_name,
    message,
    report_id=None,
    officer_id=None,
    officer_name=None,
):
    try:
        payload = {
            "sender_id": sender_id,
            "sender_role": sender_role,
            "farmer_id": farmer_id,
            "farmer_name": farmer_name,
            "message": message,
            "report_id": report_id,
            "officer_id": officer_id,
        }

        if officer_name is not None:
            payload["officer_name"] = officer_name

        response = (
            db.service_client.table("farmer_support_messages")
            .insert(payload)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error sending farmer support message: {e}")
        return False


def delete_farmer_message(message_id):
    try:
        (
            db.service_client.table("farmer_support_messages")
            .delete()
            .eq("id", message_id)
            .execute()
        )
        return True
    except Exception as e:
        st.error(f"Error deleting farmer support message: {e}")
        return False


def get_farmer_list(current_officer_id, current_officer_code):
    try:
        farmers_response = (
            db.service_client.table("farmers")
            .select("farmer_id, full_name, region, area, email, created_at")
            .order("full_name", desc=False)
            .execute()
        )
        farmers_data = farmers_response.data if farmers_response.data else []

        chats_data = []

        if current_officer_code:
            try:
                response = (
                    db.service_client.table("farmer_support_messages")
                    .select("farmer_id, farmer_name, officer_id, created_at")
                    .eq("officer_id", current_officer_code)
                    .order("created_at", desc=True)
                    .execute()
                )
                chats_data = response.data if response.data else []
            except Exception:
                chats_data = []

        if not chats_data and current_officer_id:
            try:
                response = (
                    db.service_client.table("farmer_support_messages")
                    .select("farmer_id, farmer_name, officer_id, created_at")
                    .eq("officer_id", current_officer_id)
                    .order("created_at", desc=True)
                    .execute()
                )
                chats_data = response.data if response.data else []
            except Exception:
                chats_data = []

        chat_lookup = {}
        for row in chats_data:
            farmer_code = row.get("farmer_id")
            if not farmer_code or farmer_code in chat_lookup:
                continue
            chat_lookup[farmer_code] = {
                "last_chat_at": row.get("created_at"),
                "has_chat": True,
            }

        merged_farmers = []
        seen_codes = set()

        for row in farmers_data:
            farmer_code = row.get("farmer_id")
            if not farmer_code or farmer_code in seen_codes:
                continue

            seen_codes.add(farmer_code)
            merged_farmers.append({
                "farmer_code": farmer_code,
                "farmer_name": row.get("full_name") or "Unknown Farmer",
                "region": row.get("region") or "",
                "area": row.get("area") or "",
                "email": row.get("email") or "",
                "has_chat": chat_lookup.get(farmer_code, {}).get("has_chat", False),
                "last_chat_at": chat_lookup.get(farmer_code, {}).get("last_chat_at"),
            })

        for row in chats_data:
            farmer_code = row.get("farmer_id")
            if not farmer_code or farmer_code in seen_codes:
                continue

            seen_codes.add(farmer_code)
            merged_farmers.append({
                "farmer_code": farmer_code,
                "farmer_name": row.get("farmer_name") or "Unknown Farmer",
                "region": "",
                "area": "",
                "email": "",
                "has_chat": True,
                "last_chat_at": row.get("created_at"),
            })

        def sort_key(item):
            has_chat_rank = 0 if item.get("has_chat") else 1
            name_rank = str(item.get("farmer_name", "")).lower()
            return (has_chat_rank, name_rank)

        merged_farmers = sorted(merged_farmers, key=sort_key)
        return merged_farmers

    except Exception as e:
        st.error(f"Error loading farmer list: {e}")
        return []


# =====================================================
# UI HELPERS
# =====================================================
def render_community_message_html(msg):
    sender_name = safe_text(msg.get("sender_name", "Unknown"))
    sender_role = safe_text(msg.get("sender_role", "unknown"))
    message = safe_text(msg.get("message", ""))
    created_at = format_time(msg.get("created_at"))

    role_color = "#14532d" if sender_role.lower() == "officer" else "#1565c0"
    role_badge = "Officer" if sender_role.lower() == "officer" else "Farmer"

    return f"""
    <div class="forum-msg">
        <div class="forum-msg-user">
            {sender_name}
            <span class="forum-msg-role" style="background:{role_color}20; color:{role_color};">{role_badge}</span>
        </div>
        <div class="forum-msg-meta">{created_at}</div>
        <div class="forum-msg-content">{message}</div>
    </div>
    """


def render_farmer_message_html(msg):
    sender_role = safe_text(msg.get("sender_role", "unknown"))
    sender_name = safe_text(
        msg.get("farmer_name")
        if sender_role.lower() == "farmer"
        else msg.get("officer_name", "Officer")
    )
    message = safe_text(msg.get("message", ""))
    created_at = format_time(msg.get("created_at"))
    report_id = safe_text(msg.get("report_id", ""))

    role_color = "#14532d" if sender_role.lower() == "officer" else "#1565c0"
    role_badge = "Officer" if sender_role.lower() == "officer" else "Farmer"

    report_html = f'<div class="report-pill">📋 Report: {report_id}</div>' if report_id else ""

    return f"""
    <div class="forum-msg">
        <div class="forum-msg-user">
            {sender_name}
            <span class="forum-msg-role" style="background:{role_color}20; color:{role_color};">{role_badge}</span>
        </div>
        <div class="forum-msg-meta">{created_at}</div>
        <div class="forum-msg-content">{message}</div>
        {report_html}
    </div>
    """


# =====================================================
# MAIN PAGE
# =====================================================
def render_forum_page():
    # Check if user is logged in
    if "user_id" not in st.session_state:
        st.error("Please log in first.")
        return

    inject_forum_css()
    set_forum_background()

    officer_name = st.session_state.get("full_name", "Officer")
    current_officer_uuid = str(st.session_state.get("user_id", "unknown"))
    officer_profile = get_current_officer_profile(current_officer_uuid)
    current_officer_code = officer_profile["officer_code"]

    st.markdown(
        f"""
        <div class="forum-hero">
            <div class="forum-hero-kicker">Officer Identity Center</div>
            <div class="forum-hero-title">Officer Communication Forum</div>
            <div class="forum-hero-subtitle">
                Community discussion and direct officer-to-farmer support workspace with cleaner communication flow,
                private advisory handling, and field-response coordination.
            </div>
            <div class="forum-badge-row">
                <span class="forum-badge">💬 Communication Hub</span>
                <span class="forum-badge">👤 {safe_text(officer_name)}</span>
                <span class="forum-badge">🆔 {safe_text(current_officer_code)}</span>
                <span class="forum-badge">🟢 Active Session</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Forum Mode Card
    st.markdown(
        """
        <div class="forum-mode-card">
            <div class="forum-mode-title">Forum Mode</div>
            <div class="forum-mode-subtitle">
                Choose between public community discussion and private farmer support chat.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        forum_mode = st.radio(
            "Forum Mode",
            ["🧑‍🤝‍🧑 Community", "👨‍🌾 Farmer Support"],
            horizontal=True,
            label_visibility="collapsed",
        )

    if forum_mode == "🧑‍🤝‍🧑 Community":
        # Community section
        messages = fetch_community_messages()

        st.markdown(
            """
            <div class="forum-green-shell">
                <div class="forum-green-title">Community Discussion</div>
                <div class="forum-green-subtitle">
                    Public feed for updates, recommendations, and field notices.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # FIXED: Build ONE HTML string and render ONCE
        with st.container():
            chat_html = """
            <div style="
                background:#f5efe6;
                border-radius:22px;
                padding:16px;
                height:520px;
                overflow-y:auto;
            ">
            """

            if messages:
                for msg in messages:
                    chat_html += render_community_message_html(msg)
            else:
                chat_html += '<div class="ips-empty-note">No messages yet.</div>'

            chat_html += "</div>"

            st.markdown(chat_html, unsafe_allow_html=True)

        # DELETE buttons remain OUTSIDE the HTML (kept functional)
        if messages:
            for msg in messages:
                is_officer_msg = str(msg.get("sender_role", "")).lower() == "officer"
                is_mine = str(msg.get("sender_id", "")) == current_officer_uuid
                message_id = msg.get("id")

                if is_officer_msg and is_mine and message_id is not None:
                    st.markdown('<div class="forum-delete-wrap">', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"community_delete_{message_id}"):
                        ok = delete_community_message(message_id, current_officer_uuid)
                        if ok:
                            log_officer_activity(
                                "DELETE_COMMUNITY_MESSAGE",
                                f"Deleted community message ID: {message_id}",
                            )
                            st.success("Message deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete message.")
                    st.markdown('</div>', unsafe_allow_html=True)

        # Post new message section
        post_panel_html = """
        <div class="forum-green-shell">
            <div class="forum-panel-title-light">Post New Community Message</div>
            <div class="forum-panel-subtitle-light">
                Write a public message for the community feed.
            </div>
        </div>
        """.strip()

        st.markdown(post_panel_html, unsafe_allow_html=True)

        community_input = st.text_area(
            "Write your message",
            placeholder="Share an update, recommendation, or warning for the community...",
            key="community_message_input",
            label_visibility="collapsed",
        )

        # Wrap button with CSS class
        st.markdown('<div class="community-post-wrap">', unsafe_allow_html=True)
        if st.button("📢 Post to Community", width="stretch"):
            if not community_input.strip():
                st.warning("Please write a message first.")
            else:
                ok = insert_community_message(
                    sender_id=current_officer_uuid,
                    sender_name=officer_name,
                    sender_role="officer",
                    message=community_input.strip(),
                )
                if ok:
                    log_officer_activity(
                        "SEND_COMMUNITY_MESSAGE",
                        f"Posted community message: {community_input.strip()[:80]}",
                    )
                    st.success("Community message posted successfully.")
                    st.rerun()
                else:
                    st.error("Failed to post community message.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Farmer Support Mode
    farmer_list = get_farmer_list(current_officer_uuid, current_officer_code)

    if not farmer_list:
        st.markdown(
            """
            <div class="empty-box">
                No farmers found.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    left_col, right_col = st.columns([1.05, 2.15], gap="large")

    with left_col:
        left_panel_html = """
        <div class="forum-green-side-shell">
            <div class="forum-green-title">Farmer Conversations</div>
            <div class="forum-green-subtitle">
                Select any farmer to open or continue direct message support.
            </div>
        </div>
        """.strip()

        st.markdown(left_panel_html, unsafe_allow_html=True)

        farmer_options = {}
        option_labels = []

        for f in farmer_list:
            label = f"{f['farmer_name']} ({f['farmer_code']})"
            option_labels.append(label)
            farmer_options[label] = f

        selected_farmer_key = st.selectbox(
            "Select Farmer",
            option_labels,
            label_visibility="collapsed",
        )
        selected_farmer = farmer_options[selected_farmer_key]

        st.markdown(
            f"""
            <div class="active-chat-box">
                <div class="active-chat-label">Active conversation</div>
                <div class="active-chat-name">{safe_text(selected_farmer['farmer_name'])}</div>
                <div class="active-chat-id">Farmer ID: {safe_text(selected_farmer['farmer_code'])}</div>
                <div class="active-chat-region">Region: {safe_text(selected_farmer.get('region', '-') or '-')} | Area: {safe_text(selected_farmer.get('area', '-') or '-')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        # Farmer support section
        farmer_messages = fetch_farmer_messages(
            selected_farmer_id=selected_farmer["farmer_code"],
            current_officer_id=current_officer_uuid,
            current_officer_code=current_officer_code,
        )

        st.markdown(
            f"""
            <div class="forum-green-side-shell">
                <div class="forum-green-title">{safe_text(selected_farmer['farmer_name'])}</div>
                <div class="forum-green-subtitle">
                    Private support chat • Farmer ID: {safe_text(selected_farmer['farmer_code'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # FIXED: Build ONE HTML string and render ONCE
        with st.container():
            chat_html = """
            <div style="
                background:#f5efe6;
                border-radius:22px;
                padding:16px;
                height:520px;
                overflow-y:auto;
            ">
            """

            if farmer_messages:
                for msg in farmer_messages:
                    chat_html += render_farmer_message_html(msg)
            else:
                chat_html += '<div class="ips-empty-note">💬 No messages yet. Start the conversation!</div>'

            chat_html += "</div>"

            st.markdown(chat_html, unsafe_allow_html=True)

        # DELETE buttons remain OUTSIDE the HTML (kept functional)
        if farmer_messages:
            for msg in farmer_messages:
                is_officer_msg = str(msg.get("sender_role", "")).lower() == "officer"
                is_mine = str(msg.get("sender_id", "")) == current_officer_uuid
                message_id = msg.get("id")

                if is_officer_msg and is_mine and message_id is not None:
                    st.markdown('<div class="forum-delete-wrap">', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"farmer_delete_{message_id}"):
                        ok = delete_farmer_message(message_id)
                        if ok:
                            log_officer_activity(
                                "DELETE_SUPPORT_MESSAGE",
                                f"Deleted support message ID: {message_id} for farmer {selected_farmer['farmer_code']}",
                            )
                            st.success("Message deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete message.")
                    st.markdown('</div>', unsafe_allow_html=True)

        # Reply section
        reply_panel_html = f"""
        <div class="forum-green-side-shell">
            <div class="forum-panel-title-light">Reply to {safe_text(selected_farmer['farmer_name'])}</div>
            <div class="forum-panel-subtitle-light">
                Send advice, follow-up, or report-related response.
            </div>
        </div>
        """.strip()

        st.markdown(reply_panel_html, unsafe_allow_html=True)

        report_id_input = st.text_input(
            "Related Report ID (optional)",
            placeholder="Example: RPT-001",
            key="farmer_report_id_input",
            label_visibility="collapsed",
        )

        private_input = st.text_area(
            "Write your reply",
            placeholder="Type your advice or response here...",
            key="private_message_input",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="forum-action-note">💬 Private replies are sent directly to the selected farmer conversation.</div>',
            unsafe_allow_html=True,
        )

        if st.button("📨 Send Reply", width="stretch"):
            if not private_input.strip():
                st.warning("Please write a reply first.")
            else:
                clean_report_id = (
                    report_id_input.strip()
                    if report_id_input.strip()
                    else None
                )

                ok = insert_farmer_message(
                    sender_id=current_officer_uuid,
                    sender_role="officer",
                    farmer_id=selected_farmer["farmer_code"],
                    farmer_name=selected_farmer["farmer_name"],
                    message=private_input.strip(),
                    report_id=clean_report_id,
                    officer_id=current_officer_code,
                    officer_name=officer_name,
                )
                if ok:
                    log_officer_activity(
                        "SEND_SUPPORT_MESSAGE",
                        f"Sent support reply to {selected_farmer['farmer_name']} ({selected_farmer['farmer_code']})"
                        + (f" for report {clean_report_id}" if clean_report_id else ""),
                    )
                    st.success("Reply sent successfully.")
                    st.rerun()
                else:
                    st.error("Failed to send reply.")