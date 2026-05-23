"""
Enhanced Safety System
Multi-layer crisis detection
"""

from typing import List, Dict, Tuple
import logging
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.embeddings import get_embedding_model

logger = logging.getLogger(__name__)


class EnhancedSafety:
    """Enhanced crisis detection with multiple layers"""
    
    # Crisis keywords (Layer 1)
    CRISIS_KEYWORDS = [
        "kill myself", "kill me", "i want to die", "suicide", "end my life",
        "hurt myself", "i'm going to jump", "i'm going to overdose",
        "i will kill myself", "want to die", "better off dead",
        "no reason to live", "can't go on", "end it all"
    ]
    
    # Crisis phrases for semantic matching (Layer 2)
    CRISIS_PHRASES = [
        "I want to kill myself",
        "I'm planning to commit suicide",
        "I want to end my life",
        "I'm going to hurt myself",
        "I don't want to live anymore",
        "Life is not worth living",
        "I'm better off dead",
        "I have a plan to kill myself"
    ]
    
    # Indian crisis helplines
    CRISIS_RESPONSE = """I'm really concerned about your safety right now. Please reach out for immediate help:

🇮🇳 India Crisis Helplines (24/7):
• Aasra: +91 9820466726
• Vandrevala Foundation: 1860 2662 345
• iCall: +91 9152987821
• Sneha India: +91 44 2464 0050
• COOJ Mental Health: +91 8322252525
• National Emergency: 112

You don't have to face this alone. Please call one of these numbers right now. They have trained counselors who can help."""
    
    def __init__(self, similarity_threshold: float = 0.80):
        """
        Initialize enhanced safety system
        
        Args:
            similarity_threshold: Threshold for semantic similarity (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.embedding_model = get_embedding_model()
        
        # Pre-compute crisis phrase embeddings
        logger.info("Computing crisis phrase embeddings...")
        self.crisis_embeddings = self.embedding_model.encode(self.CRISIS_PHRASES)
        logger.info(f"Safety system ready with {len(self.CRISIS_PHRASES)} crisis patterns")
    
    def check_keywords(self, text: str) -> bool:
        """
        Layer 1: Keyword-based detection
        
        Args:
            text: Input text
        
        Returns:
            True if crisis keywords detected
        """
        text_lower = text.lower()
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Crisis keyword detected: {keyword}")
                return True
        return False
    
    def check_semantic_similarity(self, text: str) -> Tuple[bool, float]:
        """
        Layer 2: Semantic similarity detection
        
        Args:
            text: Input text
        
        Returns:
            (is_crisis, max_similarity)
        """
        # Get embedding for input text
        text_embedding = self.embedding_model.encode_single(text)
        
        # Calculate similarities with crisis phrases
        import numpy as np
        similarities = np.dot(self.crisis_embeddings, text_embedding)
        max_similarity = float(np.max(similarities))
        
        is_crisis = max_similarity >= self.similarity_threshold
        
        if is_crisis:
            logger.warning(f"Crisis detected via semantic similarity: {max_similarity:.2f}")
        
        return is_crisis, max_similarity
    
    def calculate_risk_score(
        self,
        text: str,
        conversation_history: List[Dict] = None
    ) -> Dict[str, any]:
        """
        Layer 3: Comprehensive risk scoring
        
        Args:
            text: Current input text
            conversation_history: Optional conversation history
        
        Returns:
            Risk assessment dict
        """
        # Keyword check
        keyword_detected = self.check_keywords(text)
        keyword_score = 1.0 if keyword_detected else 0.0
        
        # Semantic check
        semantic_crisis, semantic_score = self.check_semantic_similarity(text)
        
        # History check (escalation pattern)
        history_score = 0.0
        if conversation_history:
            # Check if distress is escalating
            recent_messages = conversation_history[-3:]
            distress_words = ['anxious', 'depressed', 'hopeless', 'worthless', 'alone']
            
            distress_count = sum(
                1 for msg in recent_messages
                if any(word in msg.get('content', '').lower() for word in distress_words)
            )
            
            history_score = min(distress_count / 3.0, 1.0)
        
        # Calculate total risk score
        total_score = (
            keyword_score * 0.5 +
            semantic_score * 0.4 +
            history_score * 0.1
        )
        
        # Determine risk level
        if total_score >= 0.7 or keyword_detected or semantic_crisis:
            risk_level = "HIGH_RISK"
        elif total_score >= 0.4:
            risk_level = "MEDIUM_RISK"
        else:
            risk_level = "LOW_RISK"
        
        return {
            'risk_level': risk_level,
            'total_score': total_score,
            'keyword_detected': keyword_detected,
            'semantic_score': semantic_score,
            'history_score': history_score,
            'requires_intervention': risk_level == "HIGH_RISK"
        }
    
    def get_crisis_response(self) -> str:
        """Get crisis response message"""
        return self.CRISIS_RESPONSE
    
    def check_safety(
        self,
        text: str,
        conversation_history: List[Dict] = None
    ) -> Tuple[bool, Dict]:
        """
        Main safety check function
        
        Args:
            text: Input text
            conversation_history: Optional conversation history
        
        Returns:
            (is_safe, risk_assessment)
        """
        risk_assessment = self.calculate_risk_score(text, conversation_history)
        is_safe = not risk_assessment['requires_intervention']
        
        if not is_safe:
            logger.error(f"CRISIS DETECTED - Risk Level: {risk_assessment['risk_level']}")
        
        return is_safe, risk_assessment


# Global instance
_safety_checker = None


def get_safety_checker() -> EnhancedSafety:
    """Get or create global safety checker instance"""
    global _safety_checker
    if _safety_checker is None:
        _safety_checker = EnhancedSafety()
    return _safety_checker
