import httpx
import platform
import subprocess
import sys
import os

def check_ollama_running(url="http://localhost:11434"):
    """
    Check if Ollama is running and accessible
    
    Args:
        url (str): The URL to check
        
    Returns:
        bool: True if Ollama is running, False otherwise
    """
    try:
        response = httpx.get(f"{url}/api/tags", timeout=5.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout, Exception):
        return False

def get_install_instructions():
    """
    Get platform-specific instructions for installing Ollama
    
    Returns:
        str: Installation instructions
    """
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return """
To install Ollama on macOS:
1. Download the installer from https://ollama.com/download/mac
2. Open the downloaded file and follow the installation instructions
3. Once installed, Ollama will run in the background

To start Ollama:
1. Open Terminal
2. Run: ollama serve
"""
    elif system == "linux":
        return """
To install Ollama on Linux:
1. Run the following command:
   curl -fsSL https://ollama.com/install.sh | sh
   
To start Ollama:
1. Open Terminal
2. Run: ollama serve
"""
    elif system == "windows":
        return """
To install Ollama on Windows:
1. Download the installer from https://ollama.com/download/windows
2. Run the downloaded .exe file and follow the installation instructions
3. Once installed, Ollama will run in the background

To start Ollama:
1. Open Command Prompt or PowerShell
2. Run: ollama serve
"""
    else:
        return "Please visit https://ollama.com/download for installation instructions for your platform."

def check_and_print_status():
    """
    Check if Ollama is running and print status
    
    Returns:
        bool: True if Ollama is running, False otherwise
    """
    print("Checking if Ollama is running...")
    
    # Check if Ollama is running locally
    local_running = check_ollama_running("http://localhost:11434")
    
    # Check if Ollama is running on host.docker.internal (for Docker)
    docker_running = check_ollama_running("http://host.docker.internal:11434")
    
    if local_running:
        print("✅ Ollama is running locally at http://localhost:11434")
    else:
        print("❌ Ollama is not running locally")
    
    if docker_running:
        print("✅ Ollama is accessible from Docker at http://host.docker.internal:11434")
    else:
        print("❌ Ollama is not accessible from Docker")
    
    if not local_running and not docker_running:
        print("\nOllama needs to be installed and running for AI-powered answers.")
        print(get_install_instructions())
        return False
    
    return local_running or docker_running

if __name__ == "__main__":
    # If this script is run directly, check Ollama status
    success = check_and_print_status()
    sys.exit(0 if success else 1)
