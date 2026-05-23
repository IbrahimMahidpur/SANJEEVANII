"""
User Memory - Long-term user memory with ChromaDB
Stores user patterns, preferences, and history
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class UserMemory:
    """Long-term user memory storage"""
    
    def __init__(self, collection_name: str = "user_memory"):
        """Initialize user memory"""
        self.collection_name = collection_name
        self.vector_store = get_vector_store()
    
    def create_user(self, user_id: str, initial_data: Optional[Dict] = None) -> None:
        """
        Create new user memory
        
        Args:
            user_id: Unique user identifier
            initial_data: Optional initial user data
        """
        user_data = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_session': datetime.now().isoformat(),
            'session_count': 0,
            'emotional_trends': {},
            'cognitive_distortions': [],
            'preferred_language': 'en',
            'successful_strategies': [],
            'topics_discussed': [],
            **(initial_data or {})
        }
        
        # Store as document
        self.vector_store.add_documents(
            collection_name=self.collection_name,
            documents=[json.dumps(user_data)],
            metadatas=[{'user_id': user_id, 'type': 'user_profile'}],
            ids=[f"user_{user_id}"]
        )
        
        logger.info(f"Created user memory: {user_id}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user memory
        
        Args:
            user_id: User identifier
        
        Returns:
            User data dict or None
        """
        try:
            results = self.vector_store.query_single(
                collection_name=self.collection_name,
                query_text=user_id,  # Simple query
                n_results=1,
                where={'user_id': user_id, 'type': 'user_profile'}
            )
            
            if results:
                user_data = json.loads(results[0]['document'])
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict) -> None:
        """
        Update user memory
        
        Args:
            user_id: User identifier
            updates: Dict of fields to update
        """
        user_data = self.get_user(user_id)
        
        if user_data is None:
            self.create_user(user_id, updates)
            return
        
        # Update fields
        user_data.update(updates)
        user_data['last_session'] = datetime.now().isoformat()
        user_data['session_count'] = user_data.get('session_count', 0) + 1
        
        # Delete old entry
        try:
            collection = self.vector_store.get_or_create_collection(self.collection_name)
            collection.delete(ids=[f"user_{user_id}"])
        except:
            pass
        
        # Add updated entry
        self.vector_store.add_documents(
            collection_name=self.collection_name,
            documents=[json.dumps(user_data)],
            metadatas=[{'user_id': user_id, 'type': 'user_profile'}],
            ids=[f"user_{user_id}"]
        )
        
        logger.info(f"Updated user memory: {user_id}")
    
    def add_emotional_trend(self, user_id: str, emotion: str, intensity: int) -> None:
        """Track emotional trends"""
        user_data = self.get_user(user_id) or {}
        
        trends = user_data.get('emotional_trends', {})
        if emotion not in trends:
            trends[emotion] = []
        
        trends[emotion].append({
            'intensity': intensity,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 10 entries per emotion
        trends[emotion] = trends[emotion][-10:]
        
        self.update_user(user_id, {'emotional_trends': trends})
    
    def add_distortion(self, user_id: str, distortion: str) -> None:
        """Track cognitive distortions"""
        user_data = self.get_user(user_id) or {}
        
        distortions = user_data.get('cognitive_distortions', [])
        distortions.append({
            'type': distortion,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 20
        distortions = distortions[-20:]
        
        self.update_user(user_id, {'cognitive_distortions': distortions})
    
    def add_successful_strategy(self, user_id: str, strategy: str) -> None:
        """Track successful coping strategies"""
        user_data = self.get_user(user_id) or {}
        
        strategies = user_data.get('successful_strategies', [])
        if strategy not in strategies:
            strategies.append(strategy)
        
        self.update_user(user_id, {'successful_strategies': strategies})
    
    def format_for_llm(self, user_id: str) -> str:
        """
        Format user memory for LLM context
        
        Args:
            user_id: User identifier
        
        Returns:
            Formatted user memory string
        """
        user_data = self.get_user(user_id)
        
        if not user_data:
            return ""
        
        formatted = ["<USER_MEMORY>"]
        formatted.append(f"Session Count: {user_data.get('session_count', 0)}")
        formatted.append(f"Preferred Language: {user_data.get('preferred_language', 'en')}")
        
        # Emotional trends
        trends = user_data.get('emotional_trends', {})
        if trends:
            formatted.append("\nEmotional Patterns:")
            for emotion, entries in trends.items():
                avg_intensity = sum(e['intensity'] for e in entries) / len(entries)
                formatted.append(f"- {emotion}: avg intensity {avg_intensity:.1f}/10")
        
        # Common distortions
        distortions = user_data.get('cognitive_distortions', [])
        if distortions:
            distortion_types = [d['type'] for d in distortions[-5:]]
            formatted.append(f"\nRecent Cognitive Distortions: {', '.join(set(distortion_types))}")
        
        # Successful strategies
        strategies = user_data.get('successful_strategies', [])
        if strategies:
            formatted.append(f"\nSuccessful Strategies: {', '.join(strategies)}")
        
        formatted.append("</USER_MEMORY>")
        
        return "\n".join(formatted)


# Global instance
_user_memory = None


def get_user_memory() -> UserMemory:
    """Get or create global user memory instance"""
    global _user_memory
    if _user_memory is None:
        _user_memory = UserMemory()
    return _user_memory
