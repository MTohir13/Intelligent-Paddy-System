# pages/4_OfficerDashboard.py

import streamlit as st
from officer.Dashboard import render_dashboard
from officer.Profile import render_profile_page
from officer.Reports import render_reports
from officer.Forum import render_forum_page
from officer.AI_Assistant import render_ai_assistant

st.set_page_config(
    page_title="Officer Dashboard",
    page_icon="🌾",
    layout="wide"
)

is_logged_in = st.session_state.get("logged_in") or st.session_state.get("user_logged_in")
user_role = st.session_state.get("role") or st.session_state.get("user_role")

if not is_logged_in:
    st.warning("🔐 Please login first")
    st.switch_page("pages/3_Login.py")
    st.stop()

if str(user_role).lower() != "officer":
    st.error("⛔ Unauthorized access. Officer account required.")
    st.switch_page("main.py")
    st.stop()

st.sidebar.success(f"Welcome, {st.session_state.get('full_name', 'Officer')}!")
st.sidebar.markdown(f"**Role:** {user_role}")
st.sidebar.markdown(f"**Email:** {st.session_state.get('email', '')}")

selected_menu = render_dashboard()

if selected_menu is None:
    st.stop()

if st.session_state.get("dashboard_redirect"):
    selected_menu = st.session_state["dashboard_redirect"]
    del st.session_state["dashboard_redirect"]

if selected_menu == "👤 Profile":
    render_profile_page()

elif selected_menu == "📄 Report":
    render_reports()

elif selected_menu == "💬 Forum":
    render_forum_page()

elif selected_menu == "🤖 AI Assistant":
    render_ai_assistant()
