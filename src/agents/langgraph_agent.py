"""
LangGraph-based search agent implementation
"""

import logging
from typing import Dict, List, Any, Optional

import ollama
from pydantic import BaseModel, Field

from src.data.searxng import perform_web_search
from src.utils.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simple state class for our search process
class AgentState(BaseModel):
    """State for the search agent"""
    query: str = Field(description="The user's search query")
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="Results from search engine")
    answer: Optional[str] = Field(default=None, description="The final answer to return to the user")
    error: Optional[str] = Field(default=None, description="Error message if any")
    focus_mode: str = Field(default="all", description="The focus mode for search")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Citations for the answer")
    steps_taken: List[str] = Field(default_factory=list, description="Steps taken by the agent")

# Create a simpler search function that doesn't use LangGraph
def perform_search(query: str, focus_mode: str = "all") -> Dict[str, Any]:
    """Perform a search using a sequential approach instead of LangGraph
    
    Args:
        query (str): The search query
        focus_mode (str): The focus mode for search
        
    Returns:
        Dict[str, Any]: The search results and answer
    """
    # Create initial state
    state = AgentState(
        query=query,
        focus_mode=focus_mode,
        steps_taken=[],
        search_results=[],
        citations=[]
    )
    
    # Step 1: Search the web
    logger.info(f"Step 1: Searching the web for: {query}")
    try:
        # Get search results from SearXNG
        config = load_config()
        searxng_url = config.get("searxng", {}).get("url", "http://searxng:8080")
        results = perform_web_search(query, searxng_url, focus_mode)
        
        if not results:
            return {
                "query": query,
                "answer": "I couldn't find any results for your query. Please try a different query.",
                "citations": [],
                "error": "No search results found",
                "search_results": [],
                "steps": ["Searched the web but found no results"]
            }
        
        state.search_results = results
        state.steps_taken.append(f"Found {len(results)} search results")
        
        # Step 2: Generate an answer
        logger.info("Step 2: Generating answer with Ollama")
        
        # Format search results for the prompt
        formatted_results = ""
        for i, result in enumerate(results):
            title = result.get("title", "No title")
            content = result.get("content", "No content")
            url = result.get("url", "No URL")
            
            formatted_results += f"[{i+1}] {title}\n{content}\nSource: {url}\n\n"
        
        # Create system prompt
        system_prompt = """You are a helpful assistant that answers questions based on search results.
        Your answer should be comprehensive, accurate, and based solely on the provided search results.
        Always include citations in your answer using the format [1], [2], etc. that refer to the numbered search results.
        If the search results don't contain enough information to answer the question, say so clearly."""
        
        # Create user prompt
        user_prompt = f"""Question: {query}
        
        Search Results:
        {formatted_results}
        
        Please provide a comprehensive answer to the question based on these search results.
        Include citations to the relevant sources using the format [1], [2], etc."""
        
        # Get Ollama config
        ollama_url = config.get("ollama", {}).get("base_url", "http://host.docker.internal:11434")
        model = config.get("ollama", {}).get("default_model", "llama3")
        
        # Generate response
        logger.info(f"Calling Ollama at {ollama_url} with model {model}")
        
        # Create a custom Ollama client with the correct host URL
        client = ollama.Client(host=ollama_url)
        
        # Use the client to make the chat request
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.7}
        )
        
        # Extract answer
        answer = response["message"]["content"]
        state.steps_taken.append("Generated answer with Ollama")
        
        # Process citations
        citations = []
        for i, result in enumerate(results):
            if f"[{i+1}]" in answer:
                citations.append({
                    "id": i+1,
                    "title": result.get("title", "No title"),
                    "url": result.get("url", "No URL")
                })
        
        state.answer = answer
        state.citations = citations
        
        # Return results
        return {
            "query": query,
            "answer": state.answer,
            "citations": state.citations,
            "error": None,
            "search_results": state.search_results,
            "steps": state.steps_taken
        }
        
    except Exception as e:
        logger.error(f"Error in search process: {str(e)}")
        return {
            "query": query,
            "answer": f"I encountered an error when trying to generate an AI response. Error: {str(e)}",
            "citations": [],
            "error": str(e),
            "search_results": state.search_results,
            "steps": state.steps_taken + [f"Error: {str(e)}"]
        }

# This is the only perform_search function we need now
# The LangGraph approach was replaced with a simpler sequential approach
