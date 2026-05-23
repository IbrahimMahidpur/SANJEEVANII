"""
Agent 2: Evidence Collector
Retrieves relevant CBT evidence from enhanced RAG system (195k chunks)
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class EvidenceCollector:
    """Collects CBT evidence from enhanced RAG knowledge base"""
    
    def __init__(self):
        """Initialize with enhanced retriever"""
        try:
            from rag.retriever_generated import get_enhanced_retriever
            self.retriever = get_enhanced_retriever()
            logger.info(f"✓ Enhanced RAG loaded with {self.retriever.index.ntotal:,} chunks")
        except Exception as e:
            logger.warning(f"Enhanced RAG unavailable, falling back: {e}")
            try:
                from rag.retriever_faiss import get_retriever
                self.retriever = get_retriever()
                logger.info("✓ Using fallback FAISS retriever")
            except Exception as e2:
                logger.error(f"All retrievers failed: {e2}")
                self.retriever = None
    
    def collect_evidence(
        self,
        analysis: Dict,
        user_input: str,
        top_k: int = 5
    ) -> Dict:
        """
        Collect relevant CBT evidence based on analysis
        
        Args:
            analysis: Analysis from Agent 1
            user_input: Original user input
            top_k: Number of evidence pieces to retrieve
        
        Returns:
            Dict with 'techniques' and 'rag_context'
        """
        if not self.retriever:
            return {'techniques': [], 'rag_context': ''}
        
        try:
            # Build search query from analysis and user input
            query_parts = [user_input]
            
            if analysis.get('emotions'):
                query_parts.append(f"emotions: {', '.join(analysis['emotions'])}")
            
            if analysis.get('distortions'):
                query_parts.append(f"cognitive distortions: {', '.join(analysis['distortions'])}")
            
            query = " ".join(query_parts)
            
            # Determine category filter based on analysis
            category_filter = self._determine_categories(analysis, user_input)
            
            # Retrieve with enhanced retriever
            if hasattr(self.retriever, 'retrieve'):  # Enhanced retriever
                results = self.retriever.retrieve(
                    query=query,
                    top_k=top_k,
                    category_filter=category_filter,
                    similarity_threshold=0.5  # Lower threshold for more results
                )
                
                # Format for LLM
                rag_context = self.retriever.format_for_llm(results)
                
                return {
                    'techniques': results,
                    'rag_context': rag_context
                }
            else:  # Fallback retriever
                results = self.retriever.retrieve(query, top_k=top_k)
                return {
                    'techniques': results,
                    'rag_context': self._format_fallback(results)
                }
                
        except Exception as e:
            logger.error(f"Evidence collection error: {e}")
            return {'techniques': [], 'rag_context': ''}
    
    def _determine_categories(self, analysis: Dict, user_input: str) -> List[str]:
        """Determine which dataset categories to search based on analysis"""
        categories = []
        
        text_lower = user_input.lower()
        
        # Check for trauma indicators
        trauma_keywords = ['trauma', 'ptsd', 'flashback', 'trigger', 'abuse', 'assault']
        if any(kw in text_lower for kw in trauma_keywords):
            categories.append('trauma_cbt')
        
        # Check for panic/anxiety
        panic_keywords = ['panic', 'anxiety', 'attack', 'heart racing', 'breathe', 'dizzy']
        if any(kw in text_lower for kw in panic_keywords):
            categories.append('panic_disorder_cbt')
        
        # Check for depression
        depression_keywords = ['depressed', 'hopeless', 'worthless', 'sleep', 'tired', 'motivation']
        if any(kw in text_lower for kw in depression_keywords):
            categories.append('depression_worksheets')
        
        # Check for relationship issues
        relationship_keywords = ['partner', 'relationship', 'marriage', 'fight', 'communication', 'trust']
        if any(kw in text_lower for kw in relationship_keywords):
            categories.append('relationship_cbt')
        
        # Check for Indian/cultural context
        cultural_keywords = ['family', 'parents', 'exam', 'career', 'arranged', 'pressure']
        if any(kw in text_lower for kw in cultural_keywords):
            categories.append('indian_hinglish_cbt')
        
        # If no specific category, return None to search all
        return categories if categories else None
    
    def _format_fallback(self, results: List[Dict]) -> str:
        """Format results from fallback retriever"""
        if not results:
            return "<CBT_EVIDENCE>No specific evidence found.</CBT_EVIDENCE>"
        
        formatted = []
        for r in results:
            formatted.append(f"""<RAG>
Source: {r.get('source', 'Unknown')}
Content: {r.get('content', '')}
</RAG>""")
        
        return "\n".join(formatted)


# Global instance
_evidence_collector = None

def get_evidence_collector() -> EvidenceCollector:
    """Get or create global evidence collector instance"""
    global _evidence_collector
    if _evidence_collector is None:
        _evidence_collector = EvidenceCollector()
    return _evidence_collector
