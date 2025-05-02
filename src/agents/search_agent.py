"""
Search agent module for Perplex
"""

import logging
from typing import Dict, List, Any, Optional

# Import the LangGraph-based agent
from src.agents.langgraph_agent import perform_search as langgraph_search
from src.data.searxng import perform_web_search
from src.utils.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def perform_search(query, focus_mode="all", copilot_mode=False):
    """
    Perform a search and return results
    
    Args:
        query (str): The search query
        focus_mode (str): The focus mode for search
        copilot_mode (bool): Whether to use copilot mode
        
    Returns:
        tuple: (response, sources) where response is the AI-generated response
               and sources is a list of sources used
    """
    logger.info(f"Performing search for: {query} with focus_mode={focus_mode} and copilot_mode={copilot_mode}")
    
    try:
        # Use the LangGraph-based agent for search
        result = langgraph_search(query, focus_mode)
        
        # If there's an error in the LangGraph agent, log it
        if result.get("error"):
            logger.warning(f"LangGraph agent error: {result.get('error')}")
            
            # If we have search results but no answer, create a fallback response
            if result.get("search_results") and not result.get("answer"):
                fallback_response = f"Here are the search results for: {query}\n\n"
                fallback_response += "I couldn't generate an AI summary because of an error. "
                fallback_response += f"Error: {result.get('error')}\n\n"
                
                # Add search results to the fallback response
                for i, res in enumerate(result.get("search_results")):
                    title = res.get("title", "No title")
                    content = res.get("content", "No content")
                    url = res.get("url", "No URL")
                    fallback_response += f"[{i+1}] {title}\n{content}\nSource: {url}\n\n"
                
                return fallback_response, result.get("search_results")
        
        # Return the answer and search results
        return result.get("answer"), result.get("search_results")
        
    except Exception as e:
        logger.error(f"Error in search agent: {str(e)}")
        
        # Fallback to direct search if LangGraph agent fails
        try:
            # Get config
            config = load_config()
            searxng_url = config.get("searxng", {}).get("url", "http://searxng:8080")
            
            # Perform direct search
            results = perform_web_search(query, searxng_url, focus_mode)
            
            if not results:
                return "I couldn't find any results for your query. Please try a different search term or focus mode.", []
            
            # Create a simple fallback response
            fallback_response = f"Here are the search results for: {query}\n\n"
            fallback_response += "I encountered an error when trying to generate an AI response. "
            fallback_response += f"Error: {str(e)}\n\n"
            
            for i, result in enumerate(results):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "No URL")
                fallback_response += f"[{i+1}] {title}\n{content}\nSource: {url}\n\n"
            
            return fallback_response, results
            
        except Exception as inner_e:
            logger.error(f"Fallback search also failed: {str(inner_e)}")
            return f"Search failed: {str(e)}. Fallback also failed: {str(inner_e)}", []
