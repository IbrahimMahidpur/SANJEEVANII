"""
Agent 1: CBT Analyzer
Analyzes user input for emotions, thoughts, distortions, and patterns
"""

from typing import Dict, List
import json
import logging
import requests

logger = logging.getLogger(__name__)


class CBTAnalyzer:
    """Analyzes user input using structured CBT framework"""
    
    ANALYSIS_PROMPT = """You are a CBT analysis expert. Analyze the following user statement and provide a structured JSON response.

User Statement: "{user_input}"

Provide analysis in this EXACT JSON format:
{{
  "emotions": ["emotion1", "emotion2"],
  "intensity": 7,
  "negative_thoughts": ["thought1", "thought2"],
  "distortions": ["distortion_type1", "distortion_type2"],
  "behavior_patterns": ["pattern1", "pattern2"],
  "triggers": ["trigger1"]
}}

Common emotions: anxiety, fear, sadness, anger, shame, guilt, hopelessness
Intensity: 0-10 scale
Common distortions: catastrophizing, black-and-white thinking, mind-reading, overgeneralization, emotional reasoning, should statements, labeling, personalization
Common patterns: avoidance, rumination, withdrawal, procrastination

Respond ONLY with valid JSON, no additional text."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate"):
        """
        Initialize CBT Analyzer
        
        Args:
            ollama_url: Ollama API endpoint
        """
        self.ollama_url = ollama_url
        self.model = "gpt-oss:120b-cloud"
    
    def analyze(self, user_input: str) -> Dict:
        """
        Analyze user input
        
        Args:
            user_input: User's message
        
        Returns:
            Structured analysis dict
        """
        try:
            # Create prompt
            prompt = self.ANALYSIS_PROMPT.format(user_input=user_input)
            
            # Call Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower for more consistent JSON
                    "num_predict": 300
                }
            }
            
            logger.info("Calling Analyzer Agent...")
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get("response", "").strip()
            
            # Parse JSON
            try:
                analysis = json.loads(analysis_text)
                logger.info(f"Analysis complete: {len(analysis.get('emotions', []))} emotions, "
                          f"{len(analysis.get('distortions', []))} distortions")
                return analysis
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON: {analysis_text}")
                # Return default structure
                return self._default_analysis()
        
        except Exception as e:
            logger.error(f"Analyzer error: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict:
        """Return default analysis structure"""
        return {
            "emotions": ["uncertain"],
            "intensity": 5,
            "negative_thoughts": [],
            "distortions": [],
            "behavior_patterns": [],
            "triggers": []
        }


# Global instance
_analyzer = None


def get_analyzer() -> CBTAnalyzer:
    """Get or create global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = CBTAnalyzer()
    return _analyzer
