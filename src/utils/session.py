import streamlit as st
from src.utils.config import load_config

def initialize_session_state():
    """
    Initializes the session state variables for the Perplexica application
    """
    # Load configuration
    config = load_config()
    
    # Initialize tab navigation
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "search"
    
    # Initialize search settings
    if "focus_mode" not in st.session_state:
        default_focus_mode = config.get("search", {}).get("default_focus_mode", "all")
        st.session_state.focus_mode = default_focus_mode
    
    if "copilot_mode" not in st.session_state:
        default_copilot = config.get("search", {}).get("copilot_default", False)
        st.session_state.copilot_mode = default_copilot
    
    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Initialize discover results cache
    if "discover_results" not in st.session_state:
        st.session_state.discover_results = None
