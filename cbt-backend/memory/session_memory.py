"""
Session Memory - Short-term conversation memory
Stored in RAM per session
"""

from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SessionMemory:
    """In-memory storage for conversation sessions"""
    
    def __init__(self):
        """Initialize session memory storage"""
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> None:
        """
        Create new session
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
        """
        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'summary': None
        }
        logger.info(f"Created session: {session_id}")
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add message to session
        
        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (emotions, distortions, etc.)
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.sessions[session_id]['messages'].append(message)
        self.sessions[session_id]['last_updated'] = datetime.now().isoformat()
        
        # Keep only last 10 messages
        if len(self.sessions[session_id]['messages']) > 10:
            self.sessions[session_id]['messages'] = self.sessions[session_id]['messages'][-10:]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def get_conversation_history(
        self,
        session_id: str,
        last_n: int = 5
    ) -> List[Dict]:
        """
        Get recent conversation history
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages
        
        Returns:
            List of recent messages
        """
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = session['messages'][-last_n:]
        return messages
    
    def format_for_llm(self, session_id: str, last_n: int = 5) -> str:
        """
        Format conversation history for LLM context
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages
        
        Returns:
            Formatted conversation history
        """
        messages = self.get_conversation_history(session_id, last_n)
        
        if not messages:
            return ""
        
        formatted = ["<SESSION_HISTORY>"]
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Therapist"
            formatted.append(f"{role}: {msg['content']}")
        formatted.append("</SESSION_HISTORY>")
        
        return "\n".join(formatted)
    
    def update_summary(self, session_id: str, summary: str) -> None:
        """Update session summary"""
        if session_id in self.sessions:
            self.sessions[session_id]['summary'] = summary
            self.sessions[session_id]['last_updated'] = datetime.now().isoformat()
    
    def delete_session(self, session_id: str) -> None:
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
    
    def clear_old_sessions(self, hours: int = 24) -> int:
        """
        Clear sessions older than specified hours
        
        Args:
            hours: Age threshold in hours
        
        Returns:
            Number of sessions deleted
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        to_delete = []
        
        for session_id, session in self.sessions.items():
            last_updated = datetime.fromisoformat(session['last_updated'])
            if last_updated < cutoff:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        logger.info(f"Cleared {len(to_delete)} old sessions")
        return len(to_delete)


# Global instance
_session_memory = None


def get_session_memory() -> SessionMemory:
    """Get or create global session memory instance"""
    global _session_memory
    if _session_memory is None:
        _session_memory = SessionMemory()
    return _session_memory
