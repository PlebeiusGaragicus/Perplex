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
    initial_sidebar_state="auto"
)

def hide_markdown_header_links():
    """
    https://discuss.streamlit.io/t/hide-titles-link/19783/3
    """

        # <style>
        # .css-15zrgzn {display: none}
        # .css-eczf16 {display: none}
        # .css-jn99sy {display: none}
        # .st-emotion-cache-gi0tri {display: none}
        # .e121c1cl3 {display: none}
        # </style>
    st.markdown("""
        <style>
        .stApp a:first-child {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)


def main():
    # Initialize session state variables
    initialize_session_state()

    # hide_markdown_header_links()
    
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
