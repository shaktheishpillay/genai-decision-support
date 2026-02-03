"""
Main application entry point
"""

import streamlit as st
from ui.chat import render_chat_interface

# Page configuration
st.set_page_config(
    page_title="GenAI Decision Support System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Render the main interface
if __name__ == "__main__":
    render_chat_interface()