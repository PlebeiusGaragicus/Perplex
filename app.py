import streamlit as st
from dotenv import load_dotenv
import os
from src.ui.sidebar import render_sidebar
from src.ui.search import render_search_interface
from src.ui.discover import render_discover_tab
from src.ui.settings import render_settings
from src.utils.session import initialize_session_state

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Perplexica",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state variables
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content based on selected tab
    if st.session_state.current_tab == "search":
        render_search_interface()
    elif st.session_state.current_tab == "discover":
        render_discover_tab()
    elif st.session_state.current_tab == "settings":
        render_settings()

if __name__ == "__main__":
    main()
