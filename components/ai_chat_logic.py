# components/ai_chat_logic.py
 
import os
import re
import streamlit as st
from groq import Groq
from utils.supabase_db import db
from dotenv import load_dotenv

# =========================================================
# CONFIG
# =========================================================
# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Check for missing API key
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Please add it to .env file or .streamlit/secrets.toml"
    )

groq_client = Groq(api_key=GROQ_API_KEY)
 
 
# =========================================================
# 🔥 ACTIVITY LOGGING
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
    except Exception:
        pass
 
    return None, None
 
 
def log_officer_activity(action, description):
    officer_id, officer_name = get_current_officer_info()
 
    if not officer_id or not officer_name:
        return False
 
    try:
        db.client.table("activity_logs_officer").insert({
            "officer_id": officer_id,
            "officer_name": officer_name,
            "action": action,
            "description": description
        }).execute()
        return True
    except Exception:
        return False
 
 
# =========================================================
# SANITIZE HELPERS
# =========================================================
def sanitize_text_for_prompt(text: str) -> str:
    if text is None:
        return ""
 
    text = str(text)
 
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
 
    return text.strip()
 
 
# =========================================================
# SYSTEM PROMPT
# =========================================================
def build_system_prompt() -> str:
    officer_name = st.session_state.get("full_name", "Officer")
    officer_region = st.session_state.get("region", "Unknown Region")
 
    return f"""
You are Intelligence Paddy System AI, a professional agricultural decision-support assistant for Malaysian paddy management.
 
You support agricultural officers and monitoring staff.
You must answer professionally, clearly, and practically.
 
Current officer context:
- Officer name: {officer_name}
- Officer region: {officer_region}
 
Main scope:
- Paddy diseases
- Pest risk
- Crop health
- Fertilizer and nutrient management
- Water management
- Monitoring actions
- Field recommendations
- Farmer advisory drafting
 
Rules:
- Focus on paddy and agriculture support
- Prefer Malaysia / Kedah / MADA context when relevant
- Be practical, structured, and field-usable
- Do not invent lab-confirmed facts
- If uncertain, say what should be checked in the field
- Avoid childish chatbot style
- Always identify yourself as Intelligence Paddy System AI
- Never output HTML tags
""".strip()
 
 
def build_prompt(user_question: str) -> str:
    history = st.session_state.get("ai_chat", [])
    recent_history = history[-8:] if len(history) > 8 else history
 
    conversation_text = ""
    for sender, msg in recent_history:
        clean_msg = sanitize_text_for_prompt(msg)
 
        if sender == "Officer":
            conversation_text += f"Officer: {clean_msg}\n"
        elif sender == "AI":
            conversation_text += f"Assistant: {clean_msg}\n"
 
    clean_question = sanitize_text_for_prompt(user_question)
 
    return f"""
Conversation history:
{conversation_text}
 
New officer question:
Officer: {clean_question}
""".strip()
 
 
# =========================================================
# GROQ CALL
# =========================================================
def call_groq_generate(user_question: str) -> str:
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": build_system_prompt()
            },
            {
                "role": "user",
                "content": build_prompt(user_question)
            }
        ],
        temperature=0.3,
        top_p=0.9,
        max_tokens=500,
        stream=False
    )
 
    answer = completion.choices[0].message.content.strip()
 
    if not answer:
        log_officer_activity(
            action="AI_RESPONSE_EMPTY",
            description="Groq returned empty response"
        )
        raise ValueError("Empty response")
 
    return sanitize_text_for_prompt(answer)
 
 
# =========================================================
# PUBLIC FUNCTION
# =========================================================
def generate_ai_reply(user_question: str) -> str:
    user_question = sanitize_text_for_prompt(user_question)
 
    if not user_question:
        return "Please enter a question."
 
    preview = user_question[:150]
 
    log_officer_activity(
        action="AI_REQUEST_START",
        description=f"Started AI request: {preview}"
    )
 
    try:
        with st.spinner(f"🤖 Asking {GROQ_MODEL}..."):
            answer = call_groq_generate(user_question)
 
        log_officer_activity(
            action="AI_REQUEST_SUCCESS",
            description=f"AI request successful: {preview}"
        )
 
        st.session_state.ai_query_count = st.session_state.get("ai_query_count", 0) + 1
        return answer
 
    except Exception as e:
        log_officer_activity(
            action="AI_REQUEST_ERROR",
            description=f"AI request failed: {str(e)}"
        )
        return f"AI Assistant error: {str(e)}"