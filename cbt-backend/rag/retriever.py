"""
Retriever for RAG
Handles document retrieval and formatting
"""

from typing import List, Dict, Optional
from .vector_store import get_vector_store
import logging

logger = logging.getLogger(__name__)


class Retriever:
    """Document retriever with RAG formatting"""
    
    def __init__(
        self,
        collection_name: str = "cbt_knowledge",
        top_k: int = 3,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize retriever
        
        Args:
            collection_name: ChromaDB collection to query
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score (0-1)
        """
        self.collection_name = collection_name
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.vector_store = get_vector_store()
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents
        
        Args:
            query: Query text
            top_k: Override default top_k
            metadata_filter: Filter by metadata
        
        Returns:
            List of relevant documents with metadata
        """
        k = top_k or self.top_k
        
        try:
            results = self.vector_store.query_single(
                collection_name=self.collection_name,
                query_text=query,
                n_results=k,
                where=metadata_filter
            )
            
            # Filter by similarity threshold
            # ChromaDB returns distance (lower is better), convert to similarity
            filtered_results = []
            for result in results:
                # Distance to similarity: similarity = 1 - (distance / 2)
                # Assuming L2 distance normalized to [0, 2]
                distance = result.get('distance', 0)
                similarity = max(0, 1 - (distance / 2))
                
                if similarity >= self.similarity_threshold:
                    result['similarity'] = similarity
                    filtered_results.append(result)
            
            logger.info(f"Retrieved {len(filtered_results)}/{k} documents above threshold")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def format_rag_context(self, results: List[Dict]) -> str:
        """
        Format retrieved documents as RAG context
        
        Args:
            results: List of retrieved documents
        
        Returns:
            Formatted RAG context string
        """
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
        """
        Get relevant context for query
        
        Args:
            query: Query text
            top_k: Number of documents
            format_for_llm: Whether to format as RAG context
        
        Returns:
            RAG context string or raw documents
        """
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
        """
        Get context filtered by category
        
        Args:
            query: Query text
            category: Category to filter by
            top_k: Number of documents
        
        Returns:
            Formatted RAG context
        """
        results = self.retrieve(
            query,
            top_k=top_k,
            metadata_filter={"category": category}
        )
        return self.format_rag_context(results)


# Global instance
_retriever = None


def get_retriever() -> Retriever:
    """Get or create global retriever instance"""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever
