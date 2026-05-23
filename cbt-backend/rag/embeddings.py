"""
Embedding Model Wrapper
Uses sentence-transformers for generating embeddings
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
                       - Dimension: 384
                       - Fast inference
                       - Good quality for semantic search
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            normalize: Whether to normalize embeddings (recommended for cosine similarity)
        
        Returns:
            numpy array of shape (n_texts, dimension)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )
        
        return embeddings
    
    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            normalize: Whether to normalize embedding
        
        Returns:
            numpy array of shape (dimension,)
        """
        embedding = self.encode([text], normalize=normalize)
        return embedding[0]
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score between 0 and 1
        """
        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)
        
        # Cosine similarity (embeddings are already normalized)
        similarity = np.dot(emb1, emb2)
        
        return float(similarity)
    
    def batch_similarity(self, query: str, candidates: List[str]) -> List[float]:
        """
        Calculate similarity between query and multiple candidates
        
        Args:
            query: Query text
            candidates: List of candidate texts
        
        Returns:
            List of similarity scores
        """
        query_emb = self.encode_single(query)
        candidate_embs = self.encode(candidates)
        
        # Batch cosine similarity
        similarities = np.dot(candidate_embs, query_emb)
        
        return similarities.tolist()


# Global instance (lazy loaded)
_embedding_model = None


def get_embedding_model() -> EmbeddingModel:
    """Get or create global embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model
