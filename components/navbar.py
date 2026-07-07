# components/navbar.py
import streamlit as st
from streamlit_option_menu import option_menu

def navbar():
    """Main navigation bar for the application"""
    selected = option_menu(
        menu_title=None,
        options=["Home", "About", "FAQ", "Login"],
        icons=["house", "info-circle", "question-circle", "box-arrow-in-right"],
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#ffffff",
                "justify-content": "flex-end",
                "border-bottom": "1px solid #e0e0e0"
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "center",
                "margin": "0px 10px",
                "padding": "8px 16px",
                "color": "#000000",
                "border-radius": "4px",
                "transition": "all 0.3s ease"
            },
            "nav-link:hover": {
                "background-color": "#e8f5e9",
                "color": "#2e7d32"
            },
            "nav-link-selected": {
                "background-color": "#2e7d32",
                "color": "white",
                "font-weight": "bold"
            }
        }
    )

    return selected
