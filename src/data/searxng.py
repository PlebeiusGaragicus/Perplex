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
    
    print(f"[DEBUG] Search parameters: {params}")
    
    try:
        # Test connectivity first
        try:
            print(f"[DEBUG] Testing connectivity to {searxng_url}...")
            parsed_url = urlparse(searxng_url)
            hostname = parsed_url.netloc.split(':')[0]
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            print(f"[DEBUG] Resolving hostname: {hostname}")
            try:
                ip_address = socket.gethostbyname(hostname)
                print(f"[DEBUG] Resolved {hostname} to {ip_address}")
            except socket.gaierror as e:
                print(f"[DEBUG] DNS resolution failed: {str(e)}")
            
            print(f"[DEBUG] Testing socket connection to {hostname}:{port}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            result = s.connect_ex((hostname, port))
            s.close()
            if result == 0:
                print(f"[DEBUG] Socket connection successful")
            else:
                print(f"[DEBUG] Socket connection failed with error code {result}")
                
            # Try ping
            try:
                print(f"[DEBUG] Pinging {hostname}...")
                ping_param = "-n" if platform.system().lower() == "windows" else "-c"
                ping_cmd = ["ping", ping_param, "1", hostname]
                ping_output = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=5)
                print(f"[DEBUG] Ping result: {ping_output.returncode}")
                print(f"[DEBUG] Ping output: {ping_output.stdout[:200]}...")
            except Exception as e:
                print(f"[DEBUG] Ping failed: {str(e)}")
                
        except Exception as e:
            print(f"[DEBUG] Connectivity test error: {str(e)}")
        
        # Make request
        print(f"[DEBUG] Making HTTP request to {search_url}")
        response = httpx.get(search_url, params=params, timeout=10)
        
        # Check for errors
        if response.status_code != 200:
            print(f"[ERROR] SearXNG error: {response.status_code} - {response.text}")
            return []
        
        # Parse response
        print(f"[DEBUG] Received response with status {response.status_code}")
        data = response.json()
        
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
        
        print(f"[DEBUG] Found {len(results)} results")
        return results
    
    except Exception as e:
        print(f"[ERROR] Error searching SearXNG: {str(e)}")
        print(f"[DEBUG] Exception details: {traceback.format_exc()}")
        return []

def search_news(query, num_results=10):
    """
    Performs a news search using SearXNG
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return
        
    Returns:
        list: List of news results
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
        list: List of search results
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
    results = search_searxng(query, engines=selected_engines, num_results=num_results)
    
    # If no results found, try a more general search
    if not results and focus_mode != "all":
        results = search_searxng(query, engines=engines["all"], num_results=num_results)
    
    return results
