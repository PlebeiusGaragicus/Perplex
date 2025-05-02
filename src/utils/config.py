import os
import json
from pathlib import Path

CONFIG_FILE = "config.json"

# Environment variable names
ENV_SEARXNG_URL = "SEARXNG_URL"
ENV_OLLAMA_URL = "OLLAMA_URL"

def load_config():
    """
    Loads the configuration from the config file
    
    Returns:
        dict: The configuration dictionary
    """
    config_path = Path(CONFIG_FILE)
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        default_config = {
            "ollama": {
                # "base_url": "http://10.10.10.10:11434",
                "base_url": "http://host.docker.internal:11434",
                "default_model": "llama3.1:8b"
            },
            "searxng": {
                "url": "http://10.10.10.10:4001"
            },
            "search": {
                "num_results": 10,
                "copilot_default": False,
                "default_focus_mode": "all"
            },
            "database": {
                "path": "data/perplexica.db"
            },
            "history": {
                "enabled": True,
                "max_items": 100
            }
        }
        
        save_config(default_config)
        return override_with_env_vars(default_config)
    
    # Load existing config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return override_with_env_vars(config)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return override_with_env_vars({})

def override_with_env_vars(config):
    # Initialize empty sections if they don't exist
    if "searxng" not in config:
        config["searxng"] = {}
    if "ollama" not in config:
        config["ollama"] = {}
        
    # Override with environment variables if they exist
    if os.getenv(ENV_SEARXNG_URL):
        searxng_url = os.getenv(ENV_SEARXNG_URL)
        print(f"Using SearXNG URL from environment: {searxng_url}")
        config["searxng"]["url"] = searxng_url
    else:
        # Default SearXNG URL if not in environment
        if "url" not in config["searxng"]:
            config["searxng"]["url"] = "http://searxng:8080"
            
    if os.getenv(ENV_OLLAMA_URL):
        ollama_url = os.getenv(ENV_OLLAMA_URL)
        print(f"Using Ollama URL from environment: {ollama_url}")
        config["ollama"]["base_url"] = ollama_url
    else:
        # Default Ollama URL if not in environment
        if "base_url" not in config["ollama"]:
            config["ollama"]["base_url"] = "http://127.0.0.1:11434"
        if "default_model" not in config["ollama"]:
            config["ollama"]["default_model"] = "llama3"
            
    return config

def save_config(config):
    """
    Saves the configuration to the config file
    
    Args:
        config (dict): The configuration dictionary
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {str(e)}")
