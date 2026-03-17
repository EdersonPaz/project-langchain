"""SQL Message Repository - SQLite implementation of MessageRepository"""

import sqlite3
from datetime import datetime
from typing import List
from ...domain.entities import Message
from ...domain.repositories import MessageRepository
from ...domain.value_objects import SessionId, MessageContent


class SQLMessageRepository(MessageRepository):
    """
    SQLite implementation of MessageRepository.
    - Persists messages to SQLite database
    - Implements CRUD operations
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Create database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                message_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def add(self, message: Message) -> int:
        """Persist a message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO message_store (session_id, message_type, message_content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            message.session_id.value,
            message.message_type,
            message.content.value,
            message.created_at
        ))
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return message_id
    
    def get_by_session(self, session_id: SessionId, limit: int = 50) -> List[Message]:
        """Retrieve messages from a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_id, message_type, message_content, created_at
            FROM message_store
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (session_id.value, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row_id, session, msg_type, content, created_at in rows:
            message = Message(
                session_id=SessionId(session),
                content=MessageContent(content),
                message_type=msg_type,
                message_id=row_id,
                created_at=datetime.fromisoformat(created_at)
            )
            messages.append(message)
        
        return list(reversed(messages))  # Return in chronological order
    
    def get_recent(self, session_id: SessionId, count: int = 5) -> List[Message]:
        """Retrieve recent messages"""
        return self.get_by_session(session_id, limit=count)
    
    def delete_old(self, session_id: SessionId, keep_count: int = 20) -> int:
        """Delete old messages, keeping only recent ones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get IDs to delete
        cursor.execute("""
            SELECT id FROM message_store
            WHERE session_id = ?
            ORDER BY created_at DESC
            OFFSET ?
        """, (session_id.value, keep_count))
        
        ids_to_delete = [row[0] for row in cursor.fetchall()]
        
        if ids_to_delete:
            placeholders = ",".join(["?"] * len(ids_to_delete))
            cursor.execute(f"DELETE FROM message_store WHERE id IN ({placeholders})", ids_to_delete)
            conn.commit()
        
        deleted_count = len(ids_to_delete)
        conn.close()
        
        return deleted_count
    
    def clear_session(self, session_id: SessionId) -> int:
        """Clear all messages from a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM message_store WHERE session_id = ?", (session_id.value,))
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM message_store WHERE session_id = ?", (session_id.value,))
        conn.commit()
        conn.close()
        
        return count
