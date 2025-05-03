import sqlite3
import json
import os
from pathlib import Path
from src.utils.config import load_config

def get_db_connection():
    """
    Gets a connection to the SQLite database
    
    Returns:
        sqlite3.Connection: Database connection
    """
    config = load_config()
    db_path = config.get("database", {}).get("path", "data/perplexed.db")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Initialize database if needed
    initialize_database(conn)
    
    return conn

def initialize_database(conn):
    """
    Initializes the database schema if it doesn't exist
    
    Args:
        conn (sqlite3.Connection): Database connection
    """
    cursor = conn.cursor()
    
    # Create search history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        sources TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()

def add_search_history(query, response, sources):
    """
    Adds a search query and response to the history database
    
    Args:
        query (str): The user's search query
        response (str): The assistant's response
        sources (list): List of sources used for the response
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert sources to JSON string
    sources_json = json.dumps(sources)
    
    # Insert into database
    cursor.execute(
        "INSERT INTO search_history (query, response, sources) VALUES (?, ?, ?)",
        (query, response, sources_json)
    )
    
    conn.commit()
    conn.close()

def get_search_history(limit=100):
    """
    Gets search history from the database
    
    Args:
        limit (int): Maximum number of history items to retrieve
        
    Returns:
        list: List of history items as dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query database
    cursor.execute(
        "SELECT query, response, sources FROM search_history ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    
    # Convert to list of dictionaries
    results = []
    for row in cursor.fetchall():
        item = dict(row)
        
        # Parse sources JSON
        if item["sources"]:
            try:
                item["sources"] = json.loads(item["sources"])
            except:
                item["sources"] = []
        else:
            item["sources"] = []
        
        results.append(item)
    
    conn.close()
    return results

def clear_history():
    """
    Clears all search history from the database
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete all history
    cursor.execute("DELETE FROM search_history")
    
    conn.commit()
    conn.close()
