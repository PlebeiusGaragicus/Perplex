import streamlit as st
from src.utils.config import save_config, load_config
from src.ui.common import center_text
from src.data.ollama import get_available_models

def render_settings():
    """
    Renders the settings page for Perplexed
    """
    center_text(type="h1", text="Settings")
    
    # Load current configuration
    config = load_config()
    
    # Create tabs for different settings categories
    tab1, tab2, tab3 = st.tabs(["LLM Settings", "Search Settings", "Application Settings"])
    
    with tab1:
        render_llm_settings(config)
    
    with tab2:
        render_search_settings(config)
    
    with tab3:
        render_app_settings(config)
    
    # Save settings button
    if st.button("Save Settings", type="primary", use_container_width=True):
        save_config(config)
        st.success("Settings saved successfully!")
        st.balloons()

def render_llm_settings(config):
    """
    Renders LLM-related settings
    
    Args:
        config (dict): Current configuration
    """
    st.header("LLM Settings")
    
    # Ollama settings
    st.subheader("Ollama")
    
    # Ollama base URL
    ollama_base_url = st.text_input(
        "Ollama Base URL",
        value=config.get("ollama", {}).get("base_url", "http://host.docker.internal:11434"),
        help="The base URL for your Ollama instance (use host.docker.internal to access host from Docker)"
    )
    
    # Query available models from Ollama
    ollama_models, error_message = get_available_models()
    
    # Stop the app if we couldn't get the list of models
    if not ollama_models:
        st.error(f"Could not fetch models from Ollama: {error_message}")
        st.error("Please ensure Ollama is running and accessible, then refresh this page.")
        st.stop()
    
    # Get current default model
    current_default = config.get("ollama", {}).get("default_model", "")
    
    # Find index of current default model, or use 0 if not found
    try:
        default_index = ollama_models.index(current_default)
    except ValueError:
        default_index = 0
        
    selected_model = st.selectbox(
        "Default Ollama Model",
        options=ollama_models,
        index=default_index,
        help="The default Ollama model to use for queries"
    )
    
    # Update config
    if "ollama" not in config:
        config["ollama"] = {}
    
    config["ollama"]["base_url"] = ollama_base_url
    config["ollama"]["default_model"] = selected_model
    
    # Test connection button
    if st.button("Test Ollama Connection"):
        try:
            import httpx
            response = httpx.get(f"{ollama_base_url}/api/tags")
            if response.status_code == 200:
                st.success("Successfully connected to Ollama!")
            else:
                st.error(f"Failed to connect to Ollama: {response.text}")
        except Exception as e:
            st.error(f"Error connecting to Ollama: {str(e)}")

def render_search_settings(config):
    """
    Renders search-related settings
    
    Args:
        config (dict): Current configuration
    """
    st.header("Search Settings")
    
    # SearXNG settings
    st.subheader("SearXNG")
    
    # SearXNG URL
    searxng_url = st.text_input(
        "SearXNG URL",
        value=config.get("searxng", {}).get("url", "http://searxng:8080"),
        help="The URL for your SearXNG instance (use searxng:8080 for the Docker container)"
    )
    
    # Update config
    if "searxng" not in config:
        config["searxng"] = {}
    
    config["searxng"]["url"] = searxng_url
    
    # Test connection button
    if st.button("Test SearXNG Connection"):
        try:
            import httpx
            response = httpx.get(searxng_url)
            if response.status_code == 200:
                st.success("Successfully connected to SearXNG!")
            else:
                st.error(f"Failed to connect to SearXNG: {response.text}")
        except Exception as e:
            st.error(f"Error connecting to SearXNG: {str(e)}")
    
    # Search settings
    st.subheader("Search Behavior")
    
    # Number of results
    num_results = st.slider(
        "Number of Search Results",
        min_value=3,
        max_value=20,
        value=config.get("search", {}).get("num_results", 10),
        help="The number of search results to fetch for each query"
    )
    
    # Enable copilot by default
    copilot_default = st.checkbox(
        "Enable Copilot Mode by Default",
        value=config.get("search", {}).get("copilot_default", False),
        help="Whether to enable Copilot mode by default"
    )
    
    # Default focus mode
    focus_modes = ["all", "writing", "academic", "youtube", "wolfram", "reddit"]
    focus_mode_labels = ["All Web Search", "Writing Assistant", "Academic Search", "YouTube Search", "Wolfram Alpha", "Reddit Search"]
    
    default_focus_mode = st.selectbox(
        "Default Focus Mode",
        options=focus_modes,
        format_func=lambda x: focus_mode_labels[focus_modes.index(x)],
        index=focus_modes.index(config.get("search", {}).get("default_focus_mode", "all")) if config.get("search", {}).get("default_focus_mode") in focus_modes else 0,
        help="The default focus mode to use for searches"
    )
    
    # Update config
    if "search" not in config:
        config["search"] = {}
    
    config["search"]["num_results"] = num_results
    config["search"]["copilot_default"] = copilot_default
    config["search"]["default_focus_mode"] = default_focus_mode

def render_app_settings(config):
    """
    Renders application-related settings
    
    Args:
        config (dict): Current configuration
    """
    st.header("Application Settings")
    
    # Database settings
    st.subheader("Database")
    
    # Database path
    db_path = st.text_input(
        "SQLite Database Path",
        value=config.get("database", {}).get("path", "data/perplexed.db"),
        help="The path to the SQLite database file"
    )
    
    # Update config
    if "database" not in config:
        config["database"] = {}
    
    config["database"]["path"] = db_path
    
    # History settings
    st.subheader("History")
    
    # Enable history
    enable_history = st.checkbox(
        "Save Search History",
        value=config.get("history", {}).get("enabled", True),
        help="Whether to save search history to the database"
    )
    
    # Max history items
    max_history = st.number_input(
        "Maximum History Items",
        min_value=10,
        max_value=1000,
        value=config.get("history", {}).get("max_items", 100),
        help="The maximum number of history items to keep"
    )
    
    # Update config
    if "history" not in config:
        config["history"] = {}
    
    config["history"]["enabled"] = enable_history
    config["history"]["max_items"] = max_history
    
    # Clear history button
    if st.button("Clear Search History"):
        try:
            from src.data.database import clear_history
            clear_history()
            st.success("Search history cleared successfully!")
        except Exception as e:
            st.error(f"Error clearing history: {str(e)}")
