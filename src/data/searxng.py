import httpx
import json
import socket
import subprocess
import sys
import traceback
import platform
from urllib.parse import urlparse
from src.utils.config import load_config

def search_searxng(query, engines=None, page=1, num_results=10):
    """
    Performs a search using SearXNG
    
    Args:
        query (str): The search query
        engines (list): List of search engines to use
        page (int): Page number for pagination
        num_results (int): Number of results to return
        
    Returns:
        list: List of search results
    """
    config = load_config()
    searxng_url = config.get("searxng", {}).get("url", "http://10.10.10.10:4001")
    
    # Load debug flag from config
    DEBUG = config.get("debug", False)
    
    if DEBUG:
        print(f"\n[DEBUG] SearXNG URL: {searxng_url}")
        print(f"[DEBUG] Environment: {socket.gethostname()}")
    
    # Build search URL
    search_url = f"{searxng_url}/search"
    
    # Default engines if not specified
    if engines is None:
        engines = ["google", "bing", "duckduckgo"]
    
    # Build parameters
    params = {
        "q": query,
        "format": "json",
        "pageno": page,
        "engines": ",".join(engines),
        "results": num_results
    }
    
    if DEBUG:
        print(f"[DEBUG] Search parameters: {params}")
    
    try:
        # Make request with proper error handling
        if DEBUG:
            print(f"[DEBUG] Making search request to {search_url}")
            
        # Prepare for potential errors
        error_message = None
        try:
            response = httpx.get(search_url, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        except httpx.RequestError as e:
            error_message = f"Connection error when contacting SearXNG: {str(e)}"
            if DEBUG:
                print(f"[ERROR] {error_message}")
            return [], error_message
        except httpx.HTTPStatusError as e:
            error_message = f"SearXNG returned error status: {e.response.status_code} - {e.response.reason_phrase}"
            if DEBUG:
                print(f"[ERROR] {error_message}")
                print(f"[ERROR] Response content: {e.response.text[:200]}...")
            return [], error_message
        
        # Parse response
        if DEBUG:
            print(f"[DEBUG] Received response with status {response.status_code}")
            
        try:
            data = response.json()
        except Exception as e:
            error_message = f"Error parsing SearXNG response: {str(e)}"
            if DEBUG:
                print(f"[ERROR] {error_message}")
                print(f"[ERROR] Response content: {response.text[:200]}...")
            return [], error_message
        
        # Extract results
        results = []
        for result in data.get("results", []):
            # Create standardized result object
            result_obj = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            }
            
            # Add thumbnail if available
            if "img_src" in result:
                result_obj["thumbnail"] = result["img_src"]
            
            results.append(result_obj)
        
        # Check if we got any results
        if not results and not error_message:
            error_message = "No search results found"
            if DEBUG:
                print(f"[INFO] {error_message}")
        
        return results, error_message
    
    except Exception as e:
        error_message = f"Error searching SearXNG: {str(e)}"
        if DEBUG:
            print(f"[ERROR] {error_message}")
            print(f"[DEBUG] Exception details: {traceback.format_exc()}")
        return [], error_message

def search_news(query, num_results=10):
    """
    Performs a news search using SearXNG
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return
        
    Returns:
        tuple: (List of news results, Error message if any)
    """
    # Use news-specific engines
    engines = ["bing news", "google news"]
    
    return search_searxng(query, engines=engines, num_results=num_results)

def perform_web_search(query, searxng_url=None, focus_mode="all", num_results=10):
    """
    Performs a web search based on the query and focus mode
    
    Args:
        query (str): The search query
        searxng_url (str): The URL of the SearXNG instance
        focus_mode (str): The focus mode to use for the search
        num_results (int): Number of results to return
        
    Returns:
        tuple: (List of search results, Error message if any)
    """
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
    if focus_mode in engines:
        selected_engines = engines[focus_mode]
    else:
        # Default to all engines
        selected_engines = engines["all"]
    
    # Parse the URL
    if searxng_url:
        # Use the provided URL
        config = load_config()
        config["searxng"] = {"url": searxng_url}
    
    # Perform the search
    results, error_message = search_searxng(query, engines=selected_engines, num_results=num_results)
    
    # If no results found, try a more general search
    if not results and focus_mode != "all" and error_message is None:
        results, fallback_error = search_searxng(query, engines=engines["all"], num_results=num_results)
        if not error_message and fallback_error:
            error_message = fallback_error
    
    return results, error_message
