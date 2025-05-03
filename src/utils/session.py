import streamlit as st
import urllib.parse
from src.utils.config import load_config

def initialize_session_state():
    """
    Initializes the session state variables for the Perplexed application
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
        
    # Initialize active conversation ID
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = None
    
    # Initialize discover results cache
    if "discover_results" not in st.session_state:
        st.session_state.discover_results = None
        
    # Handle URL query parameters for search engine functionality
    if "url_params_processed" not in st.session_state:
        st.session_state.url_params_processed = False
        
    # Check for query parameters only once per session
    if not st.session_state.url_params_processed:
        # Get query parameters from URL
        query_params = st.query_params
        
        # Check if there's a search query in the URL
        if "q" in query_params:
            # Get the search query from URL
            search_query = query_params.get("q")
            
            # Store the query in session state for processing
            st.session_state.url_search_query = search_query
            
            # Ensure we're on the search tab
            st.session_state.current_tab = "search"
            
            # Mark as processed to avoid reprocessing on subsequent reruns
            st.session_state.url_params_processed = True
        else:
            # No query parameters, mark as processed
            st.session_state.url_params_processed = True
            st.session_state.url_search_query = None
