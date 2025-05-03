import streamlit as st
from dotenv import load_dotenv
import os
from src.ui.sidebar import render_sidebar
from src.ui.search import render_search_interface
from src.ui.discover import render_discover_tab
from src.ui.settings import render_settings
from src.utils.session import initialize_session_state
from src.data.conversation import ConversationManager

from src.ui.common import cprint, Colors
# cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)
cprint(f"RUNNING...", Colors.YELLOW)

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Perplexed",
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
    
    # Create a single ConversationManager instance to be shared
    conversation_manager = ConversationManager()
    cprint("Created shared ConversationManager instance", Colors.GREEN)
    
    # Render sidebar with the shared conversation manager
    render_sidebar(conversation_manager=conversation_manager)
    
    # Render main content based on selected tab
    if st.session_state.current_tab == "search":
        render_search_interface(conversation_manager=conversation_manager)
    elif st.session_state.current_tab == "discover":
        render_discover_tab()
    elif st.session_state.current_tab == "settings":
        render_settings()

if __name__ == "__main__":
    # import logging
    # logging.getLogger("fsevents").setLevel(logging.WARNING)
    # logging.getLogger("PIL").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    # logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.connection").setLevel(logging.WARNING)

    main()
