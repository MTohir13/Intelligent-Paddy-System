# officer/AI_Assistant.py

import base64
import html
import os
import re
import textwrap

import streamlit as st
from utils.supabase_db import db
from components.ai_chat_logic import generate_ai_reply

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama-3.3-70b-versatile")
AI_BACKGROUND = "assets/Background3.jpg"


# =========================================================
# BACKGROUND
# =========================================================
def set_ai_background(image_path=AI_BACKGROUND):
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
        print(f"set_ai_background error: {e}")


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


def log_ai_view_once():
    session_key = "ai_assistant_view_logged"
    if st.session_state.get(session_key):
        return

    log_officer_activity(
        action="VIEW_AI_ASSISTANT",
        description="Viewed AI Assistant page"
    )
    st.session_state[session_key] = True


# =========================================================
# STATE
# =========================================================
def _init_ai_state():
    if "ai_chat" not in st.session_state:
        st.session_state.ai_chat = []

    if "ai_query_count" not in st.session_state:
        st.session_state.ai_query_count = 0

    if "ai_input_key" not in st.session_state:
        st.session_state.ai_input_key = 0

    _force_clean_corrupted_chat()


# =========================================================
# SANITIZE / CLEAN
# =========================================================
def _strip_html_tags(text: str) -> str:
    if text is None:
        return ""

    text = str(text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _looks_bad(text: str) -> bool:
    if not text:
        return False

    text = str(text)
    bad_patterns = [
        "<div",
        "</div>",
        "class=",
        "ips-message-row",
        "ips-avatar",
        "ips-bubble",
        "&lt;div",
    ]
    return any(p in text for p in bad_patterns)


def _clean_message(text: str) -> str:
    if text is None:
        return ""

    text = str(text).strip()

    if _looks_bad(text):
        text = _strip_html_tags(text)

    return text.strip()


def _force_clean_corrupted_chat():
    cleaned = []
    changed = False

    for item in st.session_state.get("ai_chat", []):
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            changed = True
            continue

        sender, msg = item
        clean_msg = _clean_message(msg)

        if clean_msg != str(msg):
            changed = True

        if clean_msg:
            cleaned.append((sender, clean_msg))
        else:
            changed = True

    if changed:
        st.session_state.ai_chat = cleaned


def _msg_html(text: str) -> str:
    return html.escape(_clean_message(text)).replace("\n", "<br>")


# =========================================================
# ACTIONS
# =========================================================
def _clear_chat():
    had_messages = len(st.session_state.ai_chat) > 0

    if had_messages:
        log_officer_activity(
            action="CLEAR_AI_CONVERSATION",
            description=f"Cleared AI conversation containing {len(st.session_state.ai_chat)} messages"
        )

    st.session_state.ai_chat = []
    st.session_state.ai_input_key += 1
    st.rerun()


def _send_message(user_text: str):
    user_text = _clean_message(user_text)

    if not user_text:
        st.warning("Please enter a question.")
        return

    st.session_state.ai_chat.append(("Officer", user_text))
    answer = generate_ai_reply(user_text)
    cleaned_answer = _clean_message(answer)
    st.session_state.ai_chat.append(("AI", cleaned_answer))

    st.session_state.ai_query_count += 1

    preview = user_text[:160]
    if len(user_text) > 160:
        preview += "..."

    log_officer_activity(
        action="SEND_AI_PROMPT",
        description=f"Sent AI prompt #{st.session_state.ai_query_count}: {preview}"
    )

    st.session_state.ai_input_key += 1
    st.rerun()


# =========================================================
# CSS
# =========================================================
def _inject_css():
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

        .ips-hero {
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

        .ips-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(120deg, rgba(255,255,255,0.06), transparent 40%),
                radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 34%);
            pointer-events: none;
        }

        .ips-hero::after {
            content: "";
            position: absolute;
            top: -72px;
            right: -58px;
            width: 230px;
            height: 230px;
            background: rgba(255,255,255,0.07);
            border-radius: 50%;
        }

        .ips-hero-kicker {
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

        .ips-hero-title {
            font-size: 34px;
            font-weight: 800;
            line-height: 1.06;
            margin-bottom: 8px;
            position: relative;
            z-index: 2;
            letter-spacing: -0.02em;
            color: white;
        }

        .ips-hero-subtitle {
            font-size: 15px;
            line-height: 1.7;
            color: rgba(255,255,255,0.92);
            position: relative;
            z-index: 2;
            max-width: 860px;
            margin-bottom: 14px;
        }

        .ips-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            position: relative;
            z-index: 2;
        }

        .ips-badge {
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

        /* GREEN OUTER PANEL */
        .ips-outer-panel {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 26px;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34);
            padding: 24px 24px 20px 24px;
            backdrop-filter: blur(2px);
        }

        /* Form styling (right panel) */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%) !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 26px !important;
            box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34) !important;
            padding: 24px 24px 20px 24px !important;
            backdrop-filter: blur(2px) !important;
        }

        .ips-outer-panel .ips-section-title,
        div[data-testid="stForm"] .ips-section-title {
            color: #f4fff7 !important;
        }

        .ips-outer-panel .ips-section-subtitle,
        div[data-testid="stForm"] .ips-section-subtitle {
            color: rgba(240,255,244,0.88) !important;
        }

        .ips-section-title {
            font-size: 24px;
            font-weight: 800;
            color: #f4fff7;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .ips-section-subtitle {
            font-size: 14px;
            color: rgba(240,255,244,0.88);
            margin-top: 0;
            margin-bottom: 18px;
            line-height: 1.65;
            font-weight: 600;
        }

        /* WHITE INNER CHAT BOX */
        .ips-chat-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(244,249,246,0.97) 100%);
            border: 1px solid rgba(20, 83, 45, 0.12);
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            padding: 16px;
            min-height: 620px;
            max-height: 620px;
            overflow-y: auto;
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
        }

        .ips-msg-user {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 12px;
        }

        .ips-msg-ai {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 12px;
        }

        .ips-bubble-user {
            background: linear-gradient(135deg, #14532d 0%, #1f7a45 100%);
            color: white;
            padding: 12px 14px;
            border-radius: 16px 16px 4px 16px;
            max-width: 72%;
            font-size: 14px;
            line-height: 1.65;
            box-shadow: 0 8px 18px rgba(20,83,45,0.20);
            word-break: break-word;
        }

        .ips-bubble-ai {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            color: #123524;
            padding: 12px 14px;
            border-radius: 16px 16px 16px 4px;
            max-width: 72%;
            font-size: 14px;
            line-height: 1.65;
            border: 1px solid rgba(20, 83, 45, 0.08);
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            word-break: break-word;
        }

        /* RIGHT WHITE INNER CARDS */
        .ips-mini-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }

        .ips-mini-grid-single {
            grid-template-columns: 1fr !important;
        }

        .ips-mini-card {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 18px;
            padding: 15px 16px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }

        .ips-mini-card-title {
            font-size: 11.5px;
            font-weight: 800;
            color: #728378;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 9px;
        }

        .ips-mini-card-value {
            font-size: 15px;
            font-weight: 700;
            color: #123524;
            line-height: 1.55;
        }

        .ips-side-box {
            background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
            border: 1px solid rgba(20, 83, 45, 0.08);
            border-radius: 18px;
            padding: 15px 16px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
            margin-bottom: 12px;
        }

        .ips-side-label {
            font-size: 11.5px;
            font-weight: 800;
            color: #728378;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 9px;
        }

        .ips-side-tip {
            font-size: 14px;
            color: #5c6d62;
            line-height: 1.65;
            font-weight: 600;
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 16px !important;
            border: 1px solid rgba(20, 83, 45, 0.14) !important;
            background: rgba(255,255,255,0.98) !important;
            min-height: 220px !important;
            color: #123524 !important;
        }

        div[data-testid="stTextArea"] textarea:focus {
            border-color: rgba(27,122,68,0.55) !important;
            box-shadow: 0 0 0 3px rgba(67,160,71,0.10) !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 14px !important;
            font-weight: 700 !important;
            border: 1px solid rgba(20, 83, 45, 0.10) !important;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05) !important;
            height: 46px !important;
        }

        .ips-footer-note {
            font-size: 12px;
            color: rgba(240,255,244,0.82);
            margin-top: 8px;
            line-height: 1.6;
            font-weight: 600;
        }

        @media (max-width: 900px) {
            .ips-mini-grid {
                grid-template-columns: 1fr;
            }

            .ips-hero-title {
                font-size: 30px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# RENDERERS
# =========================================================
def _render_topbar():
    officer_name = st.session_state.get("full_name", "Officer")
    officer_email = st.session_state.get("email", "officer@email.com")
    query_count = st.session_state.get("ai_query_count", 0)

    hero_html = f"""
    <div class="ips-hero">
        <div class="ips-hero-kicker">Officer Identity Center</div>
        <div class="ips-hero-title">Intelligent Paddy System AI</div>
        <div class="ips-hero-subtitle">
            Advanced officer support assistant for disease reasoning, farmer guidance, field explanation,
            and decision support. Built to feel beyond FYP level while still staying practical for your
            agricultural workflow.
        </div>
        <div class="ips-badge-row">
            <span class="ips-badge">🧠 {OLLAMA_MODEL}</span>
            <span class="ips-badge">👤 {officer_name}</span>
            <span class="ips-badge">📨 {officer_email}</span>
            <span class="ips-badge">💬 {query_count} prompts</span>
            <span class="ips-badge">🟢 Connected</span>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(hero_html).strip(), unsafe_allow_html=True)


def _render_chat_panel():
    if st.session_state.ai_chat:
        chat_parts = []

        for sender, msg in st.session_state.ai_chat:
            clean_msg = _msg_html(msg)

            if sender == "Officer":
                chat_parts.append(
                    f'<div class="ips-msg-user"><div class="ips-bubble-user">{clean_msg}</div></div>'
                )
            else:
                chat_parts.append(
                    f'<div class="ips-msg-ai"><div class="ips-bubble-ai">{clean_msg}</div></div>'
                )

        chat_body = "".join(chat_parts)
    else:
        chat_body = (
            '<div class="ips-empty-note">'
            '<b>No messages yet.</b><br><br>'
            'Start asking about paddy disease symptoms, field monitoring, farmer advisory, '
            'fertilizer issues, pest risk, or action plans.'
            '</div>'
        )

    panel_html = f"""
<div class="ips-outer-panel">
    <div class="ips-section-title">Conversation</div>
    <div class="ips-section-subtitle">
        Your chat stays inside this card. Review earlier officer and AI messages here.
    </div>
    <div class="ips-chat-shell">
        {chat_body}
    </div>
</div>
""".strip()

    st.markdown(panel_html, unsafe_allow_html=True)


def _render_input_panel():
    with st.form("ai_input_panel_form", clear_on_submit=False):
        st.markdown('<div class="ips-section-title">Ask AI Assistant</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ips-section-subtitle">Write your prompt here.</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="ips-mini-grid ips-mini-grid-single">
                <div class="ips-mini-card">
                    <div class="ips-mini-card-title">Assistant Role</div>
                    <div class="ips-mini-card-value">
                        Agricultural officer support AI for paddy monitoring and disease guidance.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="ips-side-box">
                <div class="ips-side-label">Prompt Tip</div>
                <div class="ips-side-tip">
                    Better prompts mention symptom, suspected disease, field condition, weather, region,
                    and the exact output you want such as diagnosis, officer note, or farmer advice.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        user_input = st.text_area(
            "Ask AI",
            placeholder=(
                "Example: A farmer reports yellowing leaf edges with brown lesions after several rainy days. "
                "Give likely disease, field signs to verify, officer response, and concise farmer advice."
            ),
            key=f"ai_input_{st.session_state.ai_input_key}",
            label_visibility="collapsed",
            height=220,
        )

        st.markdown(
            '<div class="ips-footer-note">Please provide context and specific details for better AI responses.</div>',
            unsafe_allow_html=True,
        )

        ask_btn = st.form_submit_button("🚀 Ask AI", use_container_width=True)

    # OUTSIDE THE FORM - Clear button
    clear_btn = st.button("🗑️ Clear Conversation", use_container_width=True)

    if ask_btn and user_input:
        _send_message(user_input)

    if clear_btn:
        _clear_chat()


# =========================================================
# PUBLIC PAGE
# =========================================================
def render_ai_assistant():
    _init_ai_state()
    _inject_css()
    set_ai_background()
    log_ai_view_once()

    _render_topbar()

    left_col, right_col = st.columns([1.7, 1], gap="large")

    with left_col:
        _render_chat_panel()

    with right_col:
        _render_input_panel()