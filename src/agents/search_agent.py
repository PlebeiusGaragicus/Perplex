import streamlit as st
from src.data.searxng import search_searxng, search_news
from src.data.ollama import summarize_search_results
from src.utils.config import load_config

def perform_search(query, focus_mode="all", copilot_mode=False):
    """
    Performs a search based on the query and focus mode
    
    Args:
        query (str): The search query
        focus_mode (str): The focus mode to use for the search
        copilot_mode (bool): Whether to use copilot mode
        
    Returns:
        tuple: (response, sources) where response is the AI-generated response
               and sources is a list of sources used
    """
    config = load_config()
    num_results = config.get("search", {}).get("num_results", 10)
    
    # Define search engines based on focus mode
    engines = {
        "all": ["google", "bing", "duckduckgo"],
        "writing": ["google", "bing"],
        "academic": ["google scholar", "semantic scholar", "base"],
        "youtube": ["youtube"],
        "wolfram": ["wolfram alpha"],
        "reddit": ["reddit"]
    }
    
    # Get search results based on focus mode
    if focus_mode == "all":
        results = search_searxng(query, engines=engines["all"], num_results=num_results)
    elif focus_mode == "writing":
        # For writing, we'll use general search but the AI will focus on writing assistance
        results = search_searxng(query, engines=engines["writing"], num_results=num_results)
    elif focus_mode == "academic":
        results = search_searxng(query, engines=engines["academic"], num_results=num_results)
    elif focus_mode == "youtube":
        results = search_searxng(query, engines=engines["youtube"], num_results=num_results)
    elif focus_mode == "wolfram":
        results = search_searxng(query, engines=engines["wolfram"], num_results=num_results)
    elif focus_mode == "reddit":
        results = search_searxng(query, engines=engines["reddit"], num_results=num_results)
    else:
        # Default to all engines
        results = search_searxng(query, num_results=num_results)
    
    # If no results found, try a more general search
    if not results and focus_mode != "all":
        results = search_searxng(query, engines=engines["all"], num_results=num_results)
    
    # If still no results, return an error message
    if not results:
        return "I couldn't find any results for your query. Please try a different search term or focus mode.", []
    
    # If in copilot mode, generate a response using Ollama
    if copilot_mode:
        response = summarize_search_results(query, results, focus_mode)
    else:
        # In regular mode, just return a simple response with the search results
        response = f"Here are the search results for: {query}"
    
    return response, results
