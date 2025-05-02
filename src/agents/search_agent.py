"""
Search agent module for Perplex
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

# Import the LangGraph-based agent
from src.agents.langgraph_agent import perform_search as langgraph_search
from src.data.searxng import perform_web_search
from src.utils.config import load_config
from src.data.conversation import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the conversation manager as a module-level singleton
conversation_manager = ConversationManager()

def perform_search(query, focus_mode="all", copilot_mode=False, conversation_id=None):
    """
    Perform a search and return results
    
    Args:
        query (str): The search query
        focus_mode (str): The focus mode for search
        copilot_mode (bool): Whether to use copilot mode
        conversation_id (int, optional): The conversation ID for follow-up questions
        
    Returns:
        tuple: (response, sources, conversation_id) where response is the AI-generated response,
               sources is a list of sources used, and conversation_id is the ID of the conversation
    """
    logger.info(f"Performing search for: {query} with focus_mode={focus_mode} and copilot_mode={copilot_mode}")
    
    # Get conversation history if this is a follow-up question
    conversation_history = None
    if conversation_id:
        logger.info(f"This is a follow-up question in conversation {conversation_id}")
        conversation_history = conversation_manager.get_conversation_history(conversation_id)
    else:
        # Create a new conversation
        conversation_id = conversation_manager.create_conversation(f"Search: {query[:50]}")
        logger.info(f"Created new conversation with ID {conversation_id}")
    
    try:
        # Use the LangGraph-based agent for search with conversation history
        result = langgraph_search(query, focus_mode, conversation_id, conversation_history)
        
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
                
                # Store the user query and fallback response in the conversation history
                conversation_manager.add_message(conversation_id, "user", query)
                conversation_manager.add_message(conversation_id, "assistant", fallback_response, sources=result.get("search_results"))
                
                return fallback_response, result.get("search_results"), conversation_id
        
        # Store the user query and AI response in the conversation history
        conversation_manager.add_message(conversation_id, "user", query)
        conversation_manager.add_message(conversation_id, "assistant", result.get("answer", ""), sources=result.get("search_results"))
        
        # Return the answer, search results, and conversation ID
        return result.get("answer"), result.get("search_results"), conversation_id
        
    except Exception as e:
        logger.error(f"Error in search agent: {str(e)}")
        
        # Fallback to direct search if LangGraph agent fails
        try:
            # Get config
            config = load_config()
            searxng_url = config.get("searxng", {}).get("url", "http://searxng:8080")
            
            # Perform direct search - now returns (results, error_message)
            results, search_error = perform_web_search(query, searxng_url, focus_mode)
            
            # Handle search error if present
            if search_error:
                error_message = f"Search error: {search_error}"
                # Store the user query and error message in the conversation history
                conversation_manager.add_message(conversation_id, "user", query)
                conversation_manager.add_message(conversation_id, "assistant", error_message, sources=[])
                return error_message, [], conversation_id
            
            if not results:
                error_message = "I couldn't find any results for your query. Please try a different search term or focus mode."
                # Store the user query and error message in the conversation history
                conversation_manager.add_message(conversation_id, "user", query)
                conversation_manager.add_message(conversation_id, "assistant", error_message, sources=[])
                return error_message, [], conversation_id
            
            # Create a simple fallback response
            fallback_response = f"Here are the search results for: {query}\n\n"
            fallback_response += "I encountered an error when trying to generate an AI response. "
            fallback_response += f"Error: {str(e)}\n\n"
            
            for i, result in enumerate(results):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "No URL")
                fallback_response += f"[{i+1}] {title}\n{content}\nSource: {url}\n\n"
            
            # Store the user query and fallback response in the conversation history
            conversation_manager.add_message(conversation_id, "user", query)
            conversation_manager.add_message(conversation_id, "assistant", fallback_response, sources=results)
            
            return fallback_response, results, conversation_id
            
        except Exception as inner_e:
            logger.error(f"Fallback search also failed: {str(inner_e)}")
            error_message = f"Search failed: {str(e)}. Fallback also failed: {str(inner_e)}"
            
            # Store the user query and error message in the conversation history
            conversation_manager.add_message(conversation_id, "user", query)
            conversation_manager.add_message(conversation_id, "assistant", error_message, sources=[])
            
            return error_message, [], conversation_id
