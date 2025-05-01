import httpx
import json
from src.utils.config import load_config

def generate_response(prompt, model=None, system_prompt=None, temperature=0.7, max_tokens=1024):
    """
    Generates a response using Ollama
    
    Args:
        prompt (str): The prompt to send to the model
        model (str): The model to use (defaults to config default_model)
        system_prompt (str): Optional system prompt to control model behavior
        temperature (float): Sampling temperature (0.0 to 1.0)
        max_tokens (int): Maximum number of tokens to generate
        
    Returns:
        str: The generated response
    """
    config = load_config()
    ollama_url = config.get("ollama", {}).get("base_url", "http://localhost:11434")
    
    # Use default model if not specified
    if model is None:
        model = config.get("ollama", {}).get("default_model", "llama3")
    
    # Build API URL
    api_url = f"{ollama_url}/api/generate"
    
    # Build request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    # Add system prompt if provided
    if system_prompt:
        payload["system"] = system_prompt
    
    try:
        # Make request
        response = httpx.post(api_url, json=payload)
        
        # Check for errors
        if response.status_code != 200:
            print(f"Ollama error: {response.status_code} - {response.text}")
            return "Error generating response. Please try again."
        
        # Parse response
        data = response.json()
        
        # Return generated text
        return data.get("response", "")
    
    except Exception as e:
        print(f"Error calling Ollama: {str(e)}")
        return "Error generating response. Please try again."

def summarize_search_results(query, results, focus_mode="all"):
    """
    Summarizes search results using Ollama
    
    Args:
        query (str): The original search query
        results (list): List of search results
        focus_mode (str): The focus mode to use for summarization
        
    Returns:
        str: The summarized response
    """
    # Create system prompt based on focus mode
    system_prompts = {
        "all": "You are a helpful search assistant that summarizes web search results.",
        "writing": "You are a writing assistant that helps with writing, grammar, and style.",
        "academic": "You are an academic research assistant that helps with scholarly research.",
        "youtube": "You are a video content summarizer that helps find relevant videos.",
        "wolfram": "You are a computational knowledge engine that helps with factual queries.",
        "reddit": "You are a social media summarizer that helps find relevant discussions."
    }
    
    system_prompt = system_prompts.get(focus_mode, system_prompts["all"])
    
    # Format results for the prompt
    formatted_results = ""
    for i, result in enumerate(results):
        formatted_results += f"[{i+1}] {result['title']}\n"
        formatted_results += f"URL: {result['url']}\n"
        formatted_results += f"Content: {result['content']}\n\n"
    
    # Create the prompt
    prompt = f"""
User Query: {query}

Search Results:
{formatted_results}

Based on the search results above, provide a comprehensive answer to the user's query.
Include relevant information from the search results and cite your sources using [1], [2], etc.
If the search results don't contain enough information to answer the query, acknowledge this
and provide the best response you can based on the available information.
"""
    
    # Generate response
    return generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.5,
        max_tokens=2048
    )
