import base64
import os
import re

import bcrypt
import streamlit as st

from utils.supabase_db import db

# =====================================================
# IMAGE PATH
# =====================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "paddy_logo.png")

# =====================================================
# BACKGROUND IMAGE PATH
# EDIT THIS LINE IF YOU WANT TO CHANGE THE PAGE BACKGROUND
# =====================================================
BACKGROUND_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "Background.jpg")

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def is_valid_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_strong_password(password):
    """Check if password is strong enough"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"


def get_role_name(role_id):
    """Get role name for a given role_id"""
    try:
        role_data = (
            db.client.table("user_roles")
            .select("role_name")
            .eq("id", role_id)
            .single()
            .execute()
        )

        if role_data.data:
            return role_data.data["role_name"]
        return "unknown"
    except Exception:
        return "unknown"


def get_role_id(role_name):
    """Get role_id for a given role name"""
    try:
        role_data = (
            db.client.table("user_roles")
            .select("id")
            .eq("role_name", role_name)
            .single()
            .execute()
        )

        if role_data.data:
            return role_data.data["id"]
        return None
    except Exception:
        return None


def get_officer_profile_by_user_id(user_id):
    """Get officer profile using auth/public user UUID"""
    try:
        response = (
            db.client.table("officers")
            .select("officer_id, officer_name, email, region, role")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return response.data if response.data else None
    except Exception:
        return None


def get_officer_profile_by_email(email):
    """Fallback: get officer profile using email"""
    try:
        response = (
            db.client.table("officers")
            .select("officer_id, officer_name, email, region, role")
            .eq("email", email.strip().lower())
            .single()
            .execute()
        )
        return response.data if response.data else None
    except Exception:
        return None


def log_officer_activity(officer_id, officer_name, action, description):
    """
    Insert officer activity log into activity_logs_officer.
    Uses OFF-XXXX officer_id, not UUID.
    """
    try:
        if not officer_id or not officer_name:
            return False

        payload = {
            "officer_id": officer_id,
            "officer_name": officer_name,
            "action": action,
            "description": description
        }

        db.client.table("activity_logs_officer").insert(payload).execute()
        return True
    except Exception as e:
        print(f"Officer activity log insert failed: {e}")
        return False


def clear_login_session():
    """Clear only login-related session keys"""
    keys_to_clear = [
        "user",
        "user_id",
        "email",
        "role",
        "user_role",
        "role_id",
        "logged_in",
        "user_logged_in",
        "full_name",
        "officer_id",
        "officer_name",
        "officer_region"
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def logout_current_user():
    """
    Log logout activity first, then sign out from Supabase auth,
    then clear session state.
    """
    try:
        officer_id = st.session_state.get("officer_id")
        officer_name = st.session_state.get("officer_name") or st.session_state.get("full_name")
        email = st.session_state.get("email")

        if (not officer_id or not officer_name) and email:
            officer_profile = get_officer_profile_by_email(email)
            if officer_profile:
                officer_id = officer_profile.get("officer_id")
                officer_name = officer_profile.get("officer_name")

        current_role = st.session_state.get("role") or st.session_state.get("user_role")
        if current_role == "officer" and officer_id and officer_name:
            log_officer_activity(
                officer_id=officer_id,
                officer_name=officer_name,
                action="LOGOUT",
                description=f"Officer {officer_name} ({officer_id}) logged out of the system"
            )

        try:
            db.client.auth.sign_out()
        except Exception as auth_error:
            print(f"Supabase sign_out warning: {auth_error}")

        clear_login_session()
        st.success("Logged out successfully.")
        st.rerun()

    except Exception as e:
        st.error(f"Logout failed: {str(e)}")


def image_to_base64(image_path):
    """Convert image file to base64 for HTML rendering"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Image encode error: {e}")
        return None


def get_image_mime_type(image_path):
    """Return correct mime type based on extension"""
    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".png":
        return "image/png"
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".webp":
        return "image/webp"
    return "image/png"


def render_login_logo_only():
    """Render only the centered square logo card"""
    logo_html = '<div class="login-logo-fallback">🌾</div>'

    if os.path.exists(LOGIN_IMAGE_PATH):
        img_b64 = image_to_base64(LOGIN_IMAGE_PATH)
        if img_b64:
            mime_type = get_image_mime_type(LOGIN_IMAGE_PATH)
            logo_html = (
                f'<img src="data:{mime_type};base64,{img_b64}" '
                f'class="login-logo-img" alt="Login Logo">'
            )

    st.markdown(
        f"""
        <div class="login-logo-wrapper">
            <div class="login-logo-square">
                {logo_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_background():
    """Render page background image if available, otherwise fallback to gradient."""
    bg_b64 = None
    bg_mime = "image/jpeg"

    if os.path.exists(BACKGROUND_IMAGE_PATH):
        bg_b64 = image_to_base64(BACKGROUND_IMAGE_PATH)
        bg_mime = get_image_mime_type(BACKGROUND_IMAGE_PATH)

    if bg_b64:
        st.markdown(
            f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image:
        linear-gradient(rgba(255,255,255,0.18), rgba(255,255,255,0.18)),
        url("data:{bg_mime};base64,{bg_b64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
}
</style>
""",
            unsafe_allow_html=True,
        )


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Intelligence Paddy System | Secure Login",
    page_icon="🌾",
    layout="centered"
)


# =====================================================
# SESSION STATE
# =====================================================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# =====================================================
# STYLES
# =====================================================
st.markdown(
    """
<style>
.login-logo-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 18px;
}

.login-logo-square {
    width: 230px;
    height: 230px;
    background: linear-gradient(135deg, rgba(246,247,242,0.92) 0%, rgba(236,239,229,0.92) 100%);
    border-radius: 22px;
    border: 1px solid rgba(27, 94, 32, 0.10);
    box-shadow: 0 12px 28px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 0;
    backdrop-filter: blur(3px);
}

.login-logo-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center center;
    display: block;
}

.login-logo-fallback {
    font-size: 76px;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

.stButton > button {
    height: 46px;
    border-radius: 12px;
    font-weight: 600;
}

/* ONE BIG CARD */
div[data-testid="stTabs"] {
    max-width: 620px;
    margin: 0 auto;
    background: rgba(255,255,255,0.52);
    padding: 10px 18px 12px 18px;
    border-radius: 18px;
    backdrop-filter: blur(7px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.10);
}

/* SIMPLE TEXT TAB HEADER */
div[data-baseweb="tab-list"] {
    gap: 28px;
    justify-content: center;
    align-items: center;
    margin: 0 0 12px 0;
    max-width: 100%;
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 0 6px 0 !important;
    border-bottom: 1px solid rgba(27, 94, 32, 0.10);
}

/* REMOVE INDIVIDUAL CARD LOOK */
button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0 0 8px 0 !important;
    min-height: auto !important;
    color: #5e6b63 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    position: relative !important;
}

/* KILL DEFAULT STREAMLIT RED / EXTRA INDICATOR */
button[data-baseweb="tab"] > div:nth-child(2),
button[data-baseweb="tab"] [data-testid="stMarkdownContainer"] + div {
    display: none !important;
}

/* REMOVE ANY DEFAULT DECORATIVE LINE */
button[data-baseweb="tab"]::before,
button[data-baseweb="tab"]::after {
    display: none !important;
    content: none !important;
}

/* ACTIVE TAB = GREEN UNDERLINE ONLY */
button[data-baseweb="tab"][aria-selected="true"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #163c2c !important;
}

button[data-baseweb="tab"][aria-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] div,
button[data-baseweb="tab"][aria-selected="true"] span {
    color: #163c2c !important;
}

button[data-baseweb="tab"][aria-selected="true"]::after {
    display: block !important;
    content: "" !important;
    position: absolute !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    bottom: -1px !important;
    width: 64px !important;
    height: 4px !important;
    border-radius: 999px !important;
    background: #1b5e20 !important;
}

/* PANEL NO EXTRA CARD */
div[data-baseweb="tab-panel"] {
    max-width: 100%;
    margin: 0;
    background: transparent !important;
    padding: 0;
    border-radius: 0;
    backdrop-filter: none;
    box-shadow: none !important;
    border: none !important;
}

@media (max-width: 768px) {
    .login-logo-square {
        width: 210px;
        height: 210px;
    }

    div[data-testid="stTabs"] {
        padding: 8px 14px 10px 14px;
    }

    div[data-baseweb="tab-list"] {
        gap: 20px;
        margin: 0 0 10px 0;
        padding: 0 0 4px 0 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"]::after {
        width: 54px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# IF ALREADY LOGGED IN
# =====================================================
if st.session_state.get("logged_in", False):
    current_name = st.session_state.get("full_name", "User")
    current_role = st.session_state.get("role", "unknown")
    current_officer_id = st.session_state.get("officer_id", "-")

    render_login_logo_only()

    st.markdown("""
    <div style="font-size:15px;color:#666;text-align:center;margin-top:-4px;margin-bottom:20px;">
        You are already signed in
    </div>
    """, unsafe_allow_html=True)

    st.success(f"Logged in as {current_name} ({current_role})")
    if current_role == "officer":
        st.info(f"Officer ID: {current_officer_id}")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("📋 Go to Dashboard", use_container_width=True, type="primary"):
            if current_role == "admin":
                st.switch_page("pages/5_AdminDashboard.py")
            elif current_role == "officer":
                st.switch_page("pages/4_OfficerDashboard.py")
            else:
                st.switch_page("main.py")

    with col_b:
        if st.button("🚪 Logout", use_container_width=True):
            logout_current_user()

    st.markdown("""
        <div style="text-align:center;color:white;margin-top:30px;font-size:13px;">
            <hr style="margin:20px 0;">
            Protected system • Role-based access • Secure authentication<br>
            ©️ 2026 Intelligence Paddy System • All rights reserved
        </div>
    """, unsafe_allow_html=True)

else:
    render_login_logo_only()

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # =====================================================
    # LOGIN TAB
    # =====================================================
    with tab1:
        st.subheader("Officer Login")

        email = st.text_input("📧 Email", placeholder="officer@example.com", key="login_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("🚀 Login Securely", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please enter email and password.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                try:
                    normalized_email = email.strip().lower()

                    auth_response = db.client.auth.sign_in_with_password({
                        "email": normalized_email,
                        "password": password
                    })

                    if auth_response.user:
                        user_data = (
                            db.client.table("users")
                            .select("*")
                            .eq("email", normalized_email)
                            .single()
                            .execute()
                        )

                        if user_data.data:
                            user = user_data.data
                            role_name = get_role_name(user.get("role_id"))

                            st.session_state.user = user
                            st.session_state.user_id = user["id"]
                            st.session_state.email = user["email"]
                            st.session_state.role = role_name
                            st.session_state.user_role = role_name
                            st.session_state.role_id = user.get("role_id")
                            st.session_state.logged_in = True
                            st.session_state.user_logged_in = True
                            st.session_state.full_name = user["full_name"]

                            try:
                                (
                                    db.client.table("users")
                                    .update({"last_login": "now()"})
                                    .eq("id", user["id"])
                                    .execute()
                                )
                            except Exception as update_error:
                                print(f"last_login update warning: {update_error}")

                            if role_name == "officer":
                                officer_profile = get_officer_profile_by_user_id(user["id"])

                                if not officer_profile:
                                    officer_profile = get_officer_profile_by_email(normalized_email)

                                if officer_profile:
                                    st.session_state.officer_id = officer_profile.get("officer_id")
                                    st.session_state.officer_name = officer_profile.get("officer_name")
                                    st.session_state.officer_region = officer_profile.get("region")

                                    log_officer_activity(
                                        officer_id=officer_profile.get("officer_id"),
                                        officer_name=officer_profile.get("officer_name"),
                                        action="LOGIN",
                                        description=f"Officer {officer_profile.get('officer_name')} ({officer_profile.get('officer_id')}) logged into the system"
                                    )
                                else:
                                    st.warning("Officer profile not found in officers table. Login allowed, but officer activity log was not recorded.")

                            if role_name == "admin":
                                st.success(f"Welcome Admin {user['full_name']}!")
                                st.switch_page("pages/5_AdminDashboard.py")
                            elif role_name == "officer":
                                st.success(f"Welcome Officer {user['full_name']}!")
                                st.switch_page("pages/4_OfficerDashboard.py")
                            else:
                                st.success(f"Welcome {user['full_name']}!")
                                st.info("Redirecting to home page...")
                                st.switch_page("main.py")
                        else:
                            st.error("User not found in database.")
                    else:
                        st.error("Login failed: Invalid email or password")

                except Exception:
                    st.error("Login failed: Invalid email or password")

    # =====================================================
    # SIGNUP TAB
    # =====================================================
    with tab2:
        st.subheader("Create Officer Account")

        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("👤 Full Name", placeholder="John Smith", key="signup_full_name")
        with col2:
            phone = st.text_input("📞 Phone Number", placeholder="+6012-3456789", key="signup_phone")

        signup_email = st.text_input("📧 Email Address", placeholder="officer@example.com", key="signup_email")

        col3, col4 = st.columns(2)
        with col3:
            signup_password = st.text_input("🔒 Password", type="password", placeholder="Create strong password", key="signup_password")
        with col4:
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm_password")

        if signup_password:
            is_strong, msg = is_strong_password(signup_password)
            st.info(f"🔒 {msg}")

        region = st.selectbox(
            "🌾 Region of Responsibility",
            ["Kota Setar", "Pendang", "Kubang Pasu", "Padang Terap", "Yan"],
            key="signup_region"
        )

        agree_terms = st.checkbox("I agree to the Terms and Conditions and Privacy Policy", key="signup_terms")

        if st.button("✅ Create Officer Account", use_container_width=True, type="primary"):
            errors = []

            allowed_regions = ["Kota Setar", "Pendang", "Kubang Pasu", "Padang Terap", "Yan"]

            if not full_name:
                errors.append("Full name is required")
            if not signup_email:
                errors.append("Email is required")
            elif not is_valid_email(signup_email):
                errors.append("Invalid email format")
            if not signup_password:
                errors.append("Password is required")
            elif not is_strong_password(signup_password)[0]:
                errors.append("Password is not strong enough")
            if signup_password != confirm_password:
                errors.append("Passwords do not match")
            if not phone:
                errors.append("Phone number is required")
            if region not in allowed_regions:
                errors.append("Invalid region selected")
            if not agree_terms:
                errors.append("You must agree to the terms and conditions")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    normalized_email = signup_email.strip().lower()

                    existing_user = (
                        db.service_client.table("users")
                        .select("id, email")
                        .eq("email", normalized_email)
                        .execute()
                    )

                    if existing_user.data:
                        st.error("Email already registered. Please use a different email or login.")
                    else:
                        officer_role_id = get_role_id("officer")

                        if not officer_role_id:
                            st.error("Officer role not found in database. Please contact administrator.")
                        else:
                            auth_response = db.client.auth.sign_up({
                                "email": normalized_email,
                                "password": signup_password,
                                "options": {
                                    "data": {
                                        "full_name": full_name,
                                        "phone": phone,
                                        "region": region,
                                        "role": "officer"
                                    }
                                }
                            })

                            if not auth_response.user:
                                st.error("Failed to create authentication account.")
                            else:
                                user_id = auth_response.user.id
                                officer_id_value = f"OFF-{user_id[:8].upper()}"

                                existing_user_by_id = (
                                    db.service_client.table("users")
                                    .select("id")
                                    .eq("id", user_id)
                                    .execute()
                                )

                                if not existing_user_by_id.data:
                                    user_record = {
                                        "id": user_id,
                                        "email": normalized_email,
                                        "full_name": full_name,
                                        "phone": phone,
                                        "region": region,
                                        "role_id": officer_role_id
                                    }

                                    db.service_client.table("users").insert(user_record).execute()

                                officer_record = {
                                    "id": user_id,
                                    "officer_id": officer_id_value,
                                    "officer_name": full_name,
                                    "region": region,
                                    "role": "officer",
                                    "phone": phone,
                                    "email": normalized_email,
                                    "profile_img_link": None
                                }

                                existing_officer = (
                                    db.service_client.table("officers")
                                    .select("id")
                                    .eq("id", user_id)
                                    .execute()
                                )

                                if existing_officer.data:
                                    (
                                        db.service_client.table("officers")
                                        .update({
                                            "officer_id": officer_id_value,
                                            "officer_name": full_name,
                                            "region": region,
                                            "role": "officer",
                                            "phone": phone,
                                            "email": normalized_email,
                                            "updated_at": "now()",
                                            "profile_img_link": None
                                        })
                                        .eq("id", user_id)
                                        .execute()
                                    )
                                else:
                                    (
                                        db.service_client.table("officers")
                                        .insert(officer_record)
                                        .execute()
                                    )

                                st.success("✅ Officer account created successfully! Please login.")
                                st.balloons()
                                st.info("Switch to Login tab to sign in.")

                except Exception as e:
                    st.error(f"Signup failed: {str(e)}")
                    with st.expander("Technical Details"):
                        st.code(str(e))

    # =====================================================
    # FOOTER
    # =====================================================
    st.markdown("""
        <div style="text-align:center;color:white;margin-top:30px;font-size:13px;">
            <hr style="margin:20px 0;">
            Protected system • Role-based access • Secure authentication<br>
            ©️ 2026 Intelligent Paddy System • All rights reserved
        </div>
    """, unsafe_allow_html=True)


# =====================================================
# BACKGROUND
# =====================================================
render_background()