import streamlit as st
from src.data.database import add_search_history, get_search_history
from src.utils.config import load_config

def add_to_history(query, response, sources):
    """
    Adds a search query and response to the conversation history
    
    Args:
        query (str): The user's search query
        response (str): The assistant's response
        sources (list): List of sources used for the response
    """
    # Add to session state history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    st.session_state.conversation_history.append((query, response, sources))
    
    # Add to database if history is enabled
    config = load_config()
    if config.get("history", {}).get("enabled", True):
        try:
            add_search_history(query, response, sources)
        except Exception as e:
            print(f"Error saving to history: {str(e)}")

def get_conversation_history():
    """
    Gets the conversation history from session state
    
    Returns:
        list: List of (query, response, sources) tuples
    """
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    return st.session_state.conversation_history

def load_history_from_database():
    """
    Loads search history from the database into session state
    """
    config = load_config()
    if config.get("history", {}).get("enabled", True):
        try:
            history_items = get_search_history(limit=config.get("history", {}).get("max_items", 100))
            
            # Convert to the format used in session state
            st.session_state.conversation_history = [
                (item["query"], item["response"], item["sources"])
                for item in history_items
            ]
        except Exception as e:
            print(f"Error loading history from database: {str(e)}")
            st.session_state.conversation_history = []
