# rag/retriever_generated.py
"""
Enhanced RAG Retriever for Generated CBT Datasets
Uses FAISS index with metadata filtering and reranking
"""
import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

class EnhancedRAGRetriever:
    """Enhanced retriever with metadata filtering and quality scoring"""
    
    def __init__(
        self,
        index_path: str = "rag/faiss_generated.index",
        metadata_path: str = "rag/faiss_generated_metadata.pkl",
        model_name: str = "sentence-transformers/all-mpnet-base-v2"
    ):
        """Initialize enhanced retriever"""
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        print(f"Loading FAISS index from {index_path}...")
        self.index = faiss.read_index(index_path)
        
        print(f"Loading metadata from {metadata_path}...")
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.metadata = data['metadata']
            self.chunks = data['chunks']
        
        print(f"Loading embedding model: {model_name}...")
        self.embedder = SentenceTransformer(model_name)
        
        print(f"✓ Retriever ready with {self.index.ntotal:,} vectors")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[List[str]] = None,
        language_filter: Optional[str] = None,
        safety_filter: Optional[str] = None,
        similarity_threshold: float = 0.6
    ) -> List[Dict]:
        """
        Retrieve relevant chunks with optional filtering
        
        Args:
            query: Search query
            top_k: Number of results to return
            category_filter: Filter by categories (e.g., ['trauma_cbt', 'panic_disorder_cbt'])
            language_filter: Filter by language ('english', 'hinglish')
            safety_filter: Filter by safety level ('safe', 'clinician_guided')
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of dicts with 'content', 'source', 'score', 'metadata'
        """
        # Embed query
        query_embedding = self.embedder.encode([query], convert_to_numpy=True).astype('float32')
        
        # Search FAISS index (get more than top_k for filtering)
        search_k = min(top_k * 10, self.index.ntotal)  # Get 10x for filtering
        distances, indices = self.index.search(query_embedding, search_k)
        
        # Convert L2 distances to similarity scores (0-1)
        # Lower distance = higher similarity
        max_distance = np.max(distances[0]) if len(distances[0]) > 0 else 1.0
        similarities = 1 - (distances[0] / (max_distance + 1e-6))
        
        # Collect results with metadata
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            # Get metadata
            meta = self.metadata[idx]
            
            # Apply filters
            if category_filter and meta['category'] not in category_filter:
                continue
            
            if language_filter and meta['language'] != language_filter:
                continue
            
            if safety_filter and meta['safety_level'] != safety_filter:
                continue
            
            # Apply similarity threshold
            if similarity < similarity_threshold:
                continue
            
            results.append({
                'content': self.chunks[idx],
                'source': f"{meta['category']} - {meta['topic']}",
                'score': float(similarity),
                'metadata': meta
            })
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def format_for_llm(self, results: List[Dict]) -> str:
        """Format retrieved results for LLM prompt"""
        if not results:
            return "<CBT_EVIDENCE>No specific CBT evidence retrieved for this query.</CBT_EVIDENCE>"
        
        formatted_parts = []
        for i, result in enumerate(results, 1):
            formatted_parts.append(f"""<RAG>
Source: {result['source']}
Relevance: {result['score']:.2%}
Content: {result['content']}
</RAG>""")
        
        return "\n".join(formatted_parts)
    
    def get_stats(self) -> Dict:
        """Get retriever statistics"""
        categories = {}
        languages = {}
        safety_levels = {}
        
        for meta in self.metadata:
            cat = meta['category']
            lang = meta['language']
            safety = meta['safety_level']
            
            categories[cat] = categories.get(cat, 0) + 1
            languages[lang] = languages.get(lang, 0) + 1
            safety_levels[safety] = safety_levels.get(safety, 0) + 1
        
        return {
            'total_chunks': len(self.chunks),
            'categories': categories,
            'languages': languages,
            'safety_levels': safety_levels
        }


# Global instance
_retriever = None

def get_enhanced_retriever() -> EnhancedRAGRetriever:
    """Get or create global enhanced retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = EnhancedRAGRetriever()
    return _retriever
