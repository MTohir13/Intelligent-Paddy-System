
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Import components
from components.navbar import navbar

# =====================================================
# PAGE CONFIGURATION
# =====================================================
def page_config():
    """Configure page settings"""
    st.set_page_config(
        page_title="Paddy Guard - Officer Dashboard",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        /* Hide Streamlit default elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom styles */
        .dashboard-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #2e7d32;
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .alert-badge {
            background: #ffebee;
            color: #c62828;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }
        
        .quick-action-btn {
            width: 100%;
            padding: 10px;
            border: 2px solid #2e7d32;
            border-radius: 8px;
            background: white;
            color: #2e7d32;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .quick-action-btn:hover {
            background: #2e7d32;
            color: white;
        }
        
        .message-bubble {
            background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
            padding: 12px 16px;
            border-radius: 18px 18px 0 18px;
            margin: 8px 0;
            border: 1px solid #a5d6a7;
            max-width: 85%;
            margin-left: auto;
        }
        
        .ai-bubble {
            background: linear-gradient(135deg, #f1f8e9, #dcedc8);
            border-radius: 18px 18px 18px 0;
            border: 1px solid #9ccc65;
            margin-left: 0;
            margin-right: auto;
        }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# SAMPLE DATA GENERATION
# =====================================================
def generate_dashboard_data():
    """Generate sample data for dashboard"""
    
    # Recent Activities
    activities = [
        {"time": "10:30 AM", "action": "Field Inspection", "location": "Block A", "status": "Completed"},
        {"time": "9:15 AM", "action": "Disease Report", "location": "Block C", "status": "Pending Review"},
        {"time": "Yesterday", "action": "Soil Testing", "location": "Block B", "status": "Completed"},
        {"time": "2 days ago", "action": "Farmer Training", "location": "Community Hall", "status": "Completed"},
        {"time": "3 days ago", "action": "Pest Control", "location": "Block D", "status": "In Progress"},
    ]
    
    # Field Health Data
    fields = ["Block A", "Block B", "Block C", "Block D", "Block E"]
    health_scores = [85, 92, 78, 65, 88]
    disease_risk = [15, 8, 25, 40, 12]
    farmers_count = [12, 8, 15, 10, 9]
    
    # Disease Reports
    diseases = [
        {"disease": "Blast Disease", "severity": "High", "fields": 3, "treated": 1},
        {"disease": "Brown Spot", "severity": "Medium", "fields": 5, "treated": 3},
        {"disease": "Sheath Blight", "severity": "Low", "fields": 2, "treated": 2},
        {"disease": "Bacterial Blight", "severity": "Medium", "fields": 4, "treated": 2},
    ]
    
    # Weather Data
    weather = {
        "temperature": "28°C",
        "humidity": "75%",
        "rainfall": "15mm",
        "forecast": "Partly Cloudy"
    }
    
    return {
        "activities": activities,
        "fields": fields,
        "health_scores": health_scores,
        "disease_risk": disease_risk,
        "farmers_count": farmers_count,
        "diseases": diseases,
        "weather": weather
    }

# =====================================================
# DASHBOARD COMPONENTS
# =====================================================
def render_header():
    """Render dashboard header"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="color: #1b5e20; margin-bottom: 5px;">🌾 Officer Dashboard</h1>
            <p style="color: #666; font-size: 16px;">
                Welcome back, <strong>Officer Raj</strong> | Last login: Today 9:00 AM
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Active Fields", "8", "2 this week")
    
    with col3:
        st.metric("Farmers Assisted", "54", "+5 this week")
    
    st.markdown("---")

def render_quick_stats(data):
    """Render quick statistics cards"""
    st.markdown("### 📊 Overview")
    
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 24px; color: #2e7d32;">85%</div>
            <div style="font-size: 14px; color: #555;">Avg. Field Health</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 24px; color: #d32f2f;">3</div>
            <div style="font-size: 14px; color: #555;">Disease Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 24px; color: #1976d2;">12</div>
            <div style="font-size: 14px; color: #555;">Pending Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 24px; color: #7b1fa2;">24</div>
            <div style="font-size: 14px; color: #555;">AI Queries Today</div>
        </div>
        """, unsafe_allow_html=True)

def render_field_health_chart(fields, health_scores, disease_risk):
    """Render field health chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Health Score',
        x=fields,
        y=health_scores,
        marker_color='#66bb6a',
        text=health_scores,
        textposition='auto',
    ))
    
    fig.add_trace(go.Scatter(
        name='Disease Risk',
        x=fields,
        y=disease_risk,
        mode='lines+markers',
        line=dict(color='#ef5350', width=3),
        marker=dict(size=10),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title="Field Health & Disease Risk",
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(title="Health Score (%)", range=[0, 100]),
        yaxis2=dict(title="Disease Risk (%)", overlaying='y', side='right', range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    
    return fig

def render_recent_activities(activities):
    """Render recent activities table"""
    st.markdown("### 📝 Recent Activities")
    
    html = """
    <div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 2px solid #e0e0e0;">
                    <th style="padding: 10px; text-align: left;">Time</th>
                    <th style="padding: 10px; text-align: left;">Action</th>
                    <th style="padding: 10px; text-align: left;">Location</th>
                    <th style="padding: 10px; text-align: left;">Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for activity in activities:
        status_color = {
            "Completed": "#4caf50",
            "Pending Review": "#ff9800",
            "In Progress": "#2196f3"
        }.get(activity["status"], "#666")
        
        html += f"""
            <tr style="border-bottom: 1px solid #f0f0f0;">
                <td style="padding: 10px;">{activity['time']}</td>
                <td style="padding: 10px; font-weight: 500;">{activity['action']}</td>
                <td style="padding: 10px;">{activity['location']}</td>
                <td style="padding: 10px;">
                    <span style="color: {status_color}; font-weight: 500;">{activity['status']}</span>
                </td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def render_disease_alerts(diseases):
    """Render disease alerts"""
    st.markdown("### ⚠️ Disease Alerts")
    
    for disease in diseases:
        severity_color = {
            "High": "#d32f2f",
            "Medium": "#ff9800",
            "Low": "#4caf50"
        }.get(disease["severity"], "#666")
        
        st.markdown(f"""
        <div style="
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid {severity_color};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #333;">{disease['disease']}</h4>
                    <p style="margin: 5px 0; color: #666; font-size: 14px;">
                        {disease['fields']} fields affected | {disease['treated']} treated
                    </p>
                </div>
                <div style="
                    background: {severity_color}15;
                    color: {severity_color};
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                ">
                    {disease['severity']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_quick_actions():
    """Render quick action buttons"""
    st.markdown("### 🚀 Quick Actions")
    
    cols = st.columns(4)
    
    actions = [
        {"icon": "📝", "label": "New Report", "page": "Reports"},
        {"icon": "📷", "label": "Upload Image", "page": "AI Assistant"},
        {"icon": "👨‍🌾", "label": "Add Farmer", "page": "Profile"},
        {"icon": "💬", "label": "AI Chat", "page": "AI Assistant"},
    ]
    
    for col, action in zip(cols, actions):
        with col:
            if st.button(
                f"{action['icon']} {action['label']}",
                use_container_width=True,
                type="primary" if action['label'] == "AI Chat" else "secondary"
            ):
                st.session_state.redirect_page = action['page']
                st.rerun()

def render_ai_stats():
    """Render AI usage statistics"""
    ai_queries = st.session_state.get("ai_query_count", 0)
    
    st.metric(
        label="AI Queries Today",
        value=f"{ai_queries}",
        delta=None
    )

def render_message_bubble(sender: str, message: str):
    """Render a single chat message bubble"""
    if sender == "You":
        st.markdown(f"""
        <div class="message-bubble">
            <div style="font-weight: bold; color: #2e7d32; margin-bottom: 4px;">
                🧑‍🌾 You
            </div>
            <div style="color: #333;">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message-bubble ai-bubble">
            <div style="font-weight: bold; color: #689f38; margin-bottom: 4px;">
                🤖 AI Assistant
            </div>
            <div style="color: #333;">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_ai_assistant_sidebar():
    """Render mini AI Assistant in sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1b5e20, #2e7d32);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        ">
            <h3 style="margin: 0; color: white;">🤖 Quick AI Assistant</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">
                Get instant farming advice
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize AI session if not exists
        if "ai_chat_history" not in st.session_state:
            st.session_state.ai_chat_history = []
        
        if "ai_query_count" not in st.session_state:
            st.session_state.ai_query_count = 0
        
        # Quick questions
        quick_questions = [
            "Best fertilizer for paddy?",
            "How to prevent blast disease?",
            "Water management tips",
            "Common pests this season"
        ]
        
        for question in quick_questions:
            if st.button(f"💡 {question}", use_container_width=True, key=f"quick_{question}"):
                # Store question for AI Assistant page
                st.session_state.quick_question = question
                st.session_state.redirect_page = "AI Assistant"
                st.rerun()
        
        st.divider()
        
        # AI Stats
        st.markdown("#### 📈 AI Usage")
        render_ai_stats()
        
        st.divider()
        
        # Weather Widget
        st.markdown("#### 🌤️ Weather")
        st.markdown("""
        <div style="
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        ">
            <div style="font-size: 32px;">🌤️</div>
            <div style="font-size: 24px; font-weight: bold;">28°C</div>
            <div style="color: #666;">Partly Cloudy</div>
            <div style="font-size: 14px; color: #666; margin-top: 5px;">
                Humidity: 75% | Rainfall: 15mm
            </div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# MAIN DASHBOARD FUNCTION
# =====================================================
def render_dashboard():
    """Main dashboard rendering function"""
    
    # Page configuration
    page_config()
    
    # Check for redirect
    if "redirect_page" in st.session_state:
        redirect = st.session_state.redirect_page
        del st.session_state.redirect_page
        return redirect
    
    # Generate sample data
    data = generate_dashboard_data()
    
    # Create layout with sidebar
    main_col, sidebar_col = st.columns([3, 1])
    
    with main_col:
        # Header
        render_header()
        
        # Quick Stats
        render_quick_stats(data)
        
        # Charts Section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Field Health Chart
            fig = render_field_health_chart(
                data["fields"], 
                data["health_scores"], 
                data["disease_risk"]
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Recent Activities
            render_recent_activities(data["activities"])
        
        with col2:
            # Disease Alerts
            render_disease_alerts(data["diseases"])
            
            # Quick Actions
            render_quick_actions()
    
    with sidebar_col:
        # AI Assistant Sidebar
        render_ai_assistant_sidebar()
        
        # Upcoming Events
        st.markdown("#### 📅 Upcoming Events")
        events = [
            {"date": "Tomorrow", "event": "Field Inspection - Block A"},
            {"date": "Mar 15", "event": "Farmer Training Workshop"},
            {"date": "Mar 18", "event": "Soil Testing Day"},
            {"date": "Mar 22", "event": "Monthly Review Meeting"},
        ]
        
        for event in events:
            st.markdown(f"""
            <div style="
                background: #f5f5f5;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 8px;
            ">
                <div style="font-weight: bold; color: #2e7d32;">{event['date']}</div>
                <div style="font-size: 14px; color: #333;">{event['event']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Notifications
        st.divider()
        st.markdown("#### 🔔 Notifications")
        
        notifications = [
            "New disease report from Block C",
            "Soil test results ready",
            "Weather alert: Heavy rain expected",
            "2 pending reports need review"
        ]
        
        for notif in notifications:
            st.info(f"📌 {notif}")

# =====================================================
# EXPORT FUNCTION
# =====================================================
def render_officer_dashboard():
    """Main function to render officer dashboard"""
    try:
        # Render navbar
        selected = navbar()
        
        # Check if user is logged in (simplified)
        if "user_logged_in" not in st.session_state:
            st.session_state.user_logged_in = True  # For demo
        
        if st.session_state.user_logged_in:
            # Render dashboard
            return render_dashboard()
        else:
            st.warning("Please login to access the dashboard")
            return "Login"
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        return None

# For direct execution
if __name__ == "__main__":
    render_dashboard()