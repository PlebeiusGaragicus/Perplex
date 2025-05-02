"""
Fallback response generator for when Ollama is not available
"""

def generate_fallback_response(query, results):
    """
    Generates a simple response based on search results without using an LLM
    
    Args:
        query (str): The search query
        results (list): List of search results
        
    Returns:
        str: A formatted response with search results
    """
    if not results:
        return "I couldn't find any results for your query. Please try a different search term."
    
    # Create a simple response
    response = f"Here are the search results for: {query}\n\n"
    
    # Add a brief introduction
    response += "I found several relevant sources that might help answer your question. "
    response += "Below are summaries from each source:\n\n"
    
    # Add formatted results
    for i, result in enumerate(results):
        response += f"[{i+1}] {result.get('title', 'Untitled')}\n"
        
        # Add content snippet if available
        if 'content' in result and result['content']:
            # Truncate content if too long
            content = result['content']
            if len(content) > 200:
                content = content[:197] + "..."
            response += f"{content}\n"
            
        # Add source URL
        response += f"Source: {result.get('url', 'No URL available')}\n\n"
    
    # Add a closing note
    response += "You can click on the 'Sources' dropdown below to see more details about each source."
    
    return response
