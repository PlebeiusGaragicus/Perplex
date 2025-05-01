# Perplexica Python Implementation Guide

## Introduction

This document provides detailed implementation guidance for Perplexica as a Python Streamlit application. It focuses on creating a fully local, self-hosted solution using LangGraph and Ollama, with SearXNG integration for web searches.

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
perplexica/
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
    └── perplexica.db       # SQLite database
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

1. **FastAPI Application**: Replaces Next.js API routes
2. **MetaSearchAgent**: Core component for search and answer generation
3. **SearXNG Integration**: For web search functionality
4. **LLM Integration**: Using LangChain's abstractions
5. **Database Models**: Using SQLAlchemy ORM
