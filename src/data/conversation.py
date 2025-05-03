"""
Conversation history management for Perplex
"""

import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.utils.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation history for the application"""
    
    def __init__(self):
        """Initialize the conversation manager"""
        self.config = load_config()
        self.db_path = self._get_db_path()
        self._init_db()
    
    def _get_db_path(self) -> str:
        """Get the database path from config"""
        db_path = self.config.get("database", {}).get("path", "data/perplex.db")
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return db_path
    
    def _init_db(self):
        """Initialize the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
            ''')
            
            # Create sources table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                title TEXT,
                url TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def create_conversation(self, title: Optional[str] = None) -> int:
        """
        Create a new conversation
        
        Args:
            title (str, optional): The conversation title
            
        Returns:
            int: The conversation ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate title if not provided
            if not title:
                title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            cursor.execute(
                "INSERT INTO conversations (title) VALUES (?)",
                (title,)
            )
            
            conversation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created conversation {conversation_id}: {title}")
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return -1
    
    def add_message(self, conversation_id: int, role: str, content: str, sources: List[Dict[str, Any]] = None) -> int:
        """
        Add a message to a conversation
        
        Args:
            conversation_id (int): The conversation ID
            role (str): The message role (user, assistant)
            content (str): The message content
            sources (List[Dict[str, Any]], optional): List of sources used for this message
            
        Returns:
            int: The message ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content)
            )
            
            # Update conversation updated_at
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            
            message_id = cursor.lastrowid
            
            # Add sources if provided
            if sources and message_id > 0:
                for source in sources:
                    cursor.execute(
                        "INSERT INTO sources (message_id, title, url, content) VALUES (?, ?, ?, ?)",
                        (message_id, source.get('title', ''), source.get('url', ''), source.get('content', ''))
                    )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added message {message_id} to conversation {conversation_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return -1
    
    def get_message_sources(self, message_id: int) -> List[Dict[str, Any]]:
        """
        Get sources for a message
        
        Args:
            message_id (int): The message ID
            
        Returns:
            List[Dict[str, Any]]: The sources
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM sources WHERE message_id = ? ORDER BY id",
                (message_id,)
            )
            
            sources = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(sources)} sources for message {message_id}")
            return sources
        except Exception as e:
            logger.error(f"Error getting message sources: {str(e)}")
            return []
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation
        
        Args:
            conversation_id (int): The conversation ID
            
        Returns:
            List[Dict[str, Any]]: The messages
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,)
            )
            
            messages = [dict(row) for row in cursor.fetchall()]
            
            # Get sources for each message
            for message in messages:
                if message["role"] == "assistant":
                    message["sources"] = self.get_message_sources(message["id"])
                else:
                    message["sources"] = []
            
            conn.close()
            
            logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            return messages
        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            return []
    
    def get_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history in a format suitable for LLM context
        
        Args:
            conversation_id (int): The conversation ID
            
        Returns:
            List[Dict[str, str]]: The conversation history in LLM format
        """
        messages = self.get_conversation_messages(conversation_id)
        
        # Convert to LLM format
        llm_messages = []
        for message in messages:
            llm_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        return llm_messages
    
    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        Get all conversations
        
        Returns:
            List[Dict[str, Any]]: The conversations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM conversations ORDER BY updated_at DESC"
            )
            
            conversations = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(conversations)} conversations")
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations: {str(e)}")
            return []
    
    def update_message_content(self, message_id: int, content: str) -> bool:
        """
        Update the content of an existing message
        
        Args:
            message_id (int): The message ID
            content (str): The new content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE messages SET content = ? WHERE id = ?",
                (content, message_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated content for message {message_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating message content: {str(e)}")
            return False
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """
        Delete a conversation and all its messages
        
        Args:
            conversation_id (int): The conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete messages first
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )
            
            # Delete conversation
            cursor.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False
