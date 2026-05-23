"""
Retriever for RAG - FAISS Version
Handles document retrieval and formatting
"""

from typing import List, Dict, Optional
from .vector_store_faiss import get_vector_store
from .embeddings import get_embedding_model
import logging

logger = logging.getLogger(__name__)


class FAISSRetriever:
    """Document retriever with RAG formatting using FAISS"""
    
    def __init__(
        self,
        collection_name: str = "cbt_knowledge",
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ):
        """Initialize retriever"""
        self.collection_name = collection_name
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.vector_store = get_vector_store()
        self.embedding_model = get_embedding_model()
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve relevant documents"""
        k = top_k or self.top_k
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode_single(query)
            
            # Query FAISS
            results = self.vector_store.query_single(
                collection_name=self.collection_name,
                query_embedding=query_embedding,
                n_results=k,
                where=metadata_filter
            )
            
            # Filter by similarity threshold
            # FAISS returns L2 distance, convert to similarity
            filtered_results = []
            for result in results:
                distance = result.get('distance', 0)
                # Convert L2 distance to similarity (inverse relationship)
                # Lower distance = higher similarity
                similarity = max(0, 1 - (distance / 10))  # Normalize
                
                if similarity >= self.similarity_threshold:
                    result['similarity'] = similarity
                    filtered_results.append(result)
            
            logger.info(f"Retrieved {len(filtered_results)}/{k} documents above threshold")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def format_rag_context(self, results: List[Dict]) -> str:
        """Format retrieved documents as RAG context"""
        if not results:
            return ""
        
        rag_parts = []
        for i, result in enumerate(results, 1):
            doc_text = result['document']
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            category = metadata.get('category', '')
            
            rag_part = f"""<RAG_{i}>
Source: {source}
Category: {category}
Content: {doc_text}
</RAG_{i}>"""
            rag_parts.append(rag_part)
        
        rag_context = "\n\n".join(rag_parts)
        return f"\n\n<RETRIEVED_EVIDENCE>\n{rag_context}\n</RETRIEVED_EVIDENCE>\n\n"
    
    def get_relevant_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        format_for_llm: bool = True
    ) -> str:
        """Get relevant context for query"""
        results = self.retrieve(query, top_k=top_k)
        
        if format_for_llm:
            return self.format_rag_context(results)
        else:
            return "\n\n".join([r['document'] for r in results])
    
    def get_context_by_category(
        self,
        query: str,
        category: str,
        top_k: Optional[int] = None
    ) -> str:
        """Get context filtered by category"""
        results = self.retrieve(
            query,
            top_k=top_k,
            metadata_filter={"category": category}
        )
        return self.format_rag_context(results)


# Global instance
_retriever = None


def get_retriever() -> FAISSRetriever:
    """Get or create global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = FAISSRetriever()
    return _retriever
