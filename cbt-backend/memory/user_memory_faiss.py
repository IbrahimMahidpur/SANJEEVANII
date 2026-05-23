"""
User Memory - FAISS Version
Stores user patterns, preferences, and history using FAISS + pickle
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
import pickle
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class FAISSUserMemory:
    """Long-term user memory storage using pickle"""
    
    def __init__(self, storage_dir: str = "./faiss_db/user_memory"):
        """Initialize user memory"""
        self.storage_dir = storage_dir
        Path(storage_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"User memory initialized at: {storage_dir}")
    
    def _get_user_path(self, user_id: str) -> str:
        """Get file path for user"""
        return os.path.join(self.storage_dir, f"{user_id}.pkl")
    
    def create_user(self, user_id: str, initial_data: Optional[Dict] = None) -> None:
        """Create new user memory"""
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
        
        # Save to pickle
        with open(self._get_user_path(user_id), 'wb') as f:
            pickle.dump(user_data, f)
        
        logger.info(f"Created user memory: {user_id}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user memory"""
        user_path = self._get_user_path(user_id)
        
        if not os.path.exists(user_path):
            return None
        
        try:
            with open(user_path, 'rb') as f:
                user_data = pickle.load(f)
            return user_data
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict) -> None:
        """Update user memory"""
        user_data = self.get_user(user_id)
        
        if user_data is None:
            self.create_user(user_id, updates)
            return
        
        # Update fields
        user_data.update(updates)
        user_data['last_session'] = datetime.now().isoformat()
        user_data['session_count'] = user_data.get('session_count', 0) + 1
        
        # Save
        with open(self._get_user_path(user_id), 'wb') as f:
            pickle.dump(user_data, f)
        
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
        """Format user memory for LLM context"""
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


def get_user_memory() -> FAISSUserMemory:
    """Get or create global user memory instance"""
    global _user_memory
    if _user_memory is None:
        _user_memory = FAISSUserMemory()
    return _user_memory
