# Perplexed Python Implementation Guide

## Introduction

This document provides detailed implementation guidance for `Perplexed` as a Python Streamlit application. It focuses on creating a fully local, self-hosted solution using Streamlit and Ollama, with SearXNG integration for web searches. Both Streamlit and SearXNG are containerized within Docker for easy deployment.

## System Requirements

- Python 3.9+
- Streamlit 1.32.0+ (for the web interface)
- LangGraph 0.0.20+ (for agent workflows and multi-hop searches)
- LangChain 0.1.0+ (for LLM integrations)
- Ollama (for local LLM inference)
- SearXNG (for web search capabilities)
- SQLite (for database storage)
- httpx (for HTTP requests to SearXNG)
- Docker (for containerization)

## Core Architecture

### Project Structure

```
perplexed/
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Python dependencies
├── config.json             # Application configuration
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── src/
│   ├── ui/
│   │   ├── sidebar.py      # Sidebar navigation component
│   │   ├── search.py       # Search interface component
│   │   ├── discover.py     # Discover tab component
│   │   └── settings.py     # Settings page component
│   ├── agents/
│   │   ├── search_agent.py # Main search agent
│   │   ├── copilot.py      # Multi-hop search implementation
│   │   └── focus_modes.py  # Focus mode implementations
│   ├── data/
│   │   ├── database.py     # SQLite database operations
│   │   └── searxng.py      # SearXNG integration
│   ├── models/
│   │   ├── ollama.py       # Ollama LLM integration
│   │   └── prompts.py      # System prompts for different modes
│   └── utils/
│       ├── config.py       # Configuration utilities
│       ├── history.py      # Search history utilities
│       └── session.py      # Streamlit session state management
└── data/
    └── perplexed.db       # SQLite database
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models
│   │   └── session.py            # Database session
│   ├── searxng.py                # SearXNG integration
│   ├── config.py                 # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── documents.py          # Document processing
│       ├── similarity.py         # Similarity computation
│       └── formatting.py         # History formatting
├── main.py                       # FastAPI application entry point
└── config.toml                   # Configuration file
```

### Key Components

1. **Streamlit Application**: Replaces Next.js frontend
2. **Search Agent**: Core component for search and answer generation
3. **SearXNG Integration**: For web search functionality
4. **Ollama Integration**: For local LLM inference
5. **SQLite Database**: For storing search history and user preferences

## Development Plan

### Core Features to Implement

1. **Web Search Functionality**
   - SearXNG integration for web searches ✅
   - Result ranking and relevance sorting
   - Source citation and attribution
   - Error handling and fallback mechanisms

2. **AI-Powered Answer Generation**
   - Ollama integration for local LLM inference ✅
   - Context-aware response generation
   - Source summarization and synthesis
   - Citation linking to original sources

3. **Focus Modes**
   - All Web Search (default) ✅
   - Writing Assistant - SKIP FOR NOW
   - Academic Search - SKIP FOR NOW
   - YouTube Search - SKIP FOR NOW
   - Wolfram Alpha - SKIP FOR NOW
   - Reddit Search - SKIP FOR NOW

4. **User Interface**
   - Search interface with query input ✅
   - Results display with expandable sources ✅
   - Focus mode selection - SKIP FOR NOW
   - Settings configuration
   - Conversation history display ✅

5. **History and Session Management**
   - Search history storage in SQLite ✅
   - Session state management ✅
   - History export and clearing

6. **Advanced Features**
   - Copilot mode for multi-hop searches
   - Image and video search capabilities
   - Discover tab for exploring trending topics
   - API endpoints for external integration

### Implementation Progress

- ✅ Basic Streamlit app structure
- ✅ SearXNG integration for web search
- ✅ Ollama integration for LLM inference
- ✅ Search interface with query input
- ✅ Basic conversation history display
- ✅ SQLite database for history storage
- ✅ Settings page
- ✅ Discover tab
- ⬜ API endpoints
- ⬜ Copilot mode implementation

### Technical Debt and Considerations

- Docker networking for accessing Ollama on the host machine
- Error handling and graceful degradation
- Performance optimization for search and inference
- Security considerations for user data
- Accessibility and responsive design
- SearXNG configuration and customization
