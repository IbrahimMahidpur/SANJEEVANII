"""
Memory Manager - Unified interface for session and user memory
"""

from typing import Dict, Optional
from .session_memory import get_session_memory
from .user_memory import get_user_memory
import logging

logger = logging.getLogger(__name__)


class MemoryManager:
    """Unified memory management interface"""
    
    def __init__(self):
        """Initialize memory manager"""
        self.session_memory = get_session_memory()
        self.user_memory = get_user_memory()
    
    def start_session(self, session_id: str, user_id: Optional[str] = None) -> None:
        """Start new session"""
        self.session_memory.create_session(session_id, user_id)
        logger.info(f"Started session: {session_id} for user: {user_id}")
    
    def add_exchange(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        user_id: Optional[str] = None,
        analysis: Optional[Dict] = None
    ) -> None:
        """
        Add user-assistant exchange to memory
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_message: Assistant's response
            user_id: Optional user identifier
            analysis: Optional analysis metadata
        """
        # Add to session memory
        self.session_memory.add_message(session_id, 'user', user_message, analysis)
        self.session_memory.add_message(session_id, 'assistant', assistant_message)
        
        # Update user memory if user_id provided
        if user_id and analysis:
            self._update_user_from_analysis(user_id, analysis)
    
    def _update_user_from_analysis(self, user_id: str, analysis: Dict) -> None:
        """Update user memory from analysis"""
        # Track emotions
        if 'emotions' in analysis and 'intensity' in analysis:
            for emotion in analysis['emotions']:
                self.user_memory.add_emotional_trend(
                    user_id,
                    emotion,
                    analysis['intensity']
                )
        
        # Track distortions
        if 'distortions' in analysis:
            for distortion in analysis['distortions']:
                self.user_memory.add_distortion(user_id, distortion)
    
    def get_context_for_llm(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Get formatted memory context for LLM
        
        Args:
            session_id: Session identifier
            user_id: Optional user identifier
        
        Returns:
            Formatted memory context
        """
        context_parts = []
        
        # Session history
        session_context = self.session_memory.format_for_llm(session_id, last_n=5)
        if session_context:
            context_parts.append(session_context)
        
        # User memory
        if user_id:
            user_context = self.user_memory.format_for_llm(user_id)
            if user_context:
                context_parts.append(user_context)
        
        return "\n\n".join(context_parts)
    
    def cleanup(self, hours: int = 24) -> None:
        """Clean up old sessions"""
        deleted = self.session_memory.clear_old_sessions(hours)
        logger.info(f"Cleaned up {deleted} old sessions")


# Global instance
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
