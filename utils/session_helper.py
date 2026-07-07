import streamlit as st
from utils.supabase_db import db

class SessionHelper:
    """Helper for managing user sessions and permissions"""
    
    @staticmethod
    def get_role_name():
        """Get user's role name"""
        role_name = st.session_state.get("role")
        if not role_name and "role_id" in st.session_state:
            # Fetch role name from database
            try:
                response = db.client.table("user_roles") \
                    .select("role_name") \
                    .eq("id", st.session_state.role_id) \
                    .single() \
                    .execute()
                
                if response.data:
                    role_name = response.data["role_name"]
                    st.session_state.role = role_name
                    return role_name
            except:
                pass
        return role_name or ""
    
    @staticmethod
    def require_role(required_role):
        """Require specific role to access page"""
        if not st.session_state.get("logged_in"):
            st.error("Please log in first")
            st.switch_page("pages/3_Login.py")
        
        user_role = SessionHelper.get_role_name()
        if user_role != required_role:
            st.error(f"Access denied. {required_role.title()} role required.")
            st.switch_page("main.py")
    
    @staticmethod
    def get_full_name():
        """Get user's full name"""
        return st.session_state.get("full_name", "")
    
    @staticmethod
    def get_user_id():
        """Get user's ID"""
        return st.session_state.get("user_id", "")
    
    @staticmethod
    def get_email():
        """Get user's email"""
        return st.session_state.get("email", "")