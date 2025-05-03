"""
Search agent module for Perplex
"""

# Import the LangGraph-based agent
from src.agents.langgraph_agent import perform_search as langgraph_search

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def perform_search(query, conversation_manager, focus_mode="all", copilot_mode=False, conversation_id=None):
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
        
        # Handle streaming response
        if result.get("answer_generator"):
            # Add the user query to the conversation history
            conversation_manager.add_message(conversation_id, "user", query)
            
            # Create a placeholder for the assistant message that will be updated
            message_id = conversation_manager.add_message(conversation_id, "assistant", "", sources=result.get("search_results"))
            
            # Return the streaming generator, search results, conversation ID, and message ID for updating
            return result.get("answer_generator"), result.get("search_results"), conversation_id, message_id
        
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
        
        # No fallback - just report the error
        error_message = f"Search error: {str(e)}"
        
        # Store the user query in the conversation history
        conversation_manager.add_message(conversation_id, "user", query)
        
        # Raise the exception to be handled by the UI layer
        # This will allow the UI to show the error and stop execution
        import streamlit as st
        st.error(error_message)
        st.stop()
