"""
FAISS-based Vector Store (ChromaDB alternative)
Works with Python 3.13 without numpy compatibility issues
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store with pickle persistence"""
    
    def __init__(self, persist_directory: str = "./faiss_db"):
        """
        Initialize FAISS vector store
        
        Args:
            persist_directory: Directory to persist FAISS indices
        """
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Store collections as dict of indices
        self.collections = {}
        
        logger.info(f"FAISS Vector Store initialized at: {persist_directory}")
    
    def _get_collection_path(self, collection_name: str) -> tuple:
        """Get file paths for collection"""
        base_path = os.path.join(self.persist_directory, collection_name)
        return (
            f"{base_path}.index",      # FAISS index
            f"{base_path}.metadata",   # Metadata pickle
            f"{base_path}.docs"        # Documents pickle
        )
    
    def get_or_create_collection(self, name: str, dimension: int = 384) -> Dict:
        """
        Get or create collection
        
        Args:
            name: Collection name
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
        
        Returns:
            Collection dict
        """
        if name in self.collections:
            return self.collections[name]
        
        index_path, metadata_path, docs_path = self._get_collection_path(name)
        
        # Try to load existing
        if os.path.exists(index_path):
            try:
                index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    metadatas = pickle.load(f)
                with open(docs_path, 'rb') as f:
                    documents = pickle.load(f)
                
                collection = {
                    'name': name,
                    'index': index,
                    'metadatas': metadatas,
                    'documents': documents,
                    'ids': list(range(len(documents)))
                }
                
                self.collections[name] = collection
                logger.info(f"Loaded collection '{name}': {len(documents)} documents")
                return collection
                
            except Exception as e:
                logger.warning(f"Could not load collection '{name}': {e}")
        
        # Create new
        index = faiss.IndexFlatL2(dimension)  # L2 distance
        collection = {
            'name': name,
            'index': index,
            'metadatas': [],
            'documents': [],
            'ids': []
        }
        
        self.collections[name] = collection
        logger.info(f"Created new collection: {name}")
        return collection
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: np.ndarray,
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to collection
        
        Args:
            collection_name: Collection name
            documents: List of document texts
            embeddings: Document embeddings (n_docs, dimension)
            metadatas: Optional metadata dicts
            ids: Optional document IDs
        """
        collection = self.get_or_create_collection(collection_name, embeddings.shape[1])
        
        # Add to FAISS index
        collection['index'].add(embeddings.astype('float32'))
        
        # Add metadata and documents
        collection['documents'].extend(documents)
        collection['metadatas'].extend(metadatas or [{} for _ in documents])
        
        # Generate IDs if not provided
        if ids is None:
            start_id = len(collection['ids'])
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        collection['ids'].extend(ids)
        
        # Persist
        self._save_collection(collection)
        
        logger.info(f"Added {len(documents)} documents to '{collection_name}'")
    
    def query(
        self,
        collection_name: str,
        query_embeddings: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query collection
        
        Args:
            collection_name: Collection name
            query_embeddings: Query embeddings (n_queries, dimension)
            n_results: Number of results per query
            where: Metadata filter (simple dict matching)
        
        Returns:
            Query results
        """
        collection = self.get_or_create_collection(collection_name)
        
        if collection['index'].ntotal == 0:
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            }
        
        # Search FAISS
        distances, indices = collection['index'].search(
            query_embeddings.astype('float32'),
            min(n_results, collection['index'].ntotal)
        )
        
        # Format results
        results = {
            'documents': [],
            'metadatas': [],
            'distances': [],
            'ids': []
        }
        
        for query_idx in range(len(query_embeddings)):
            query_docs = []
            query_metas = []
            query_dists = []
            query_ids = []
            
            for idx, dist in zip(indices[query_idx], distances[query_idx]):
                if idx < 0:  # FAISS returns -1 for missing results
                    continue
                
                # Apply metadata filter if provided
                if where:
                    metadata = collection['metadatas'][idx]
                    if not all(metadata.get(k) == v for k, v in where.items()):
                        continue
                
                query_docs.append(collection['documents'][idx])
                query_metas.append(collection['metadatas'][idx])
                query_dists.append(float(dist))
                query_ids.append(collection['ids'][idx])
            
            results['documents'].append(query_docs)
            results['metadatas'].append(query_metas)
            results['distances'].append(query_dists)
            results['ids'].append(query_ids)
        
        return results
    
    def query_single(
        self,
        collection_name: str,
        query_embedding: np.ndarray,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query for single embedding
        
        Args:
            collection_name: Collection name
            query_embedding: Single query embedding (dimension,)
            n_results: Number of results
            where: Metadata filter
        
        Returns:
            List of result dicts
        """
        query_embeddings = query_embedding.reshape(1, -1)
        results = self.query(collection_name, query_embeddings, n_results, where)
        
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            })
        
        return formatted_results
    
    def _save_collection(self, collection: Dict) -> None:
        """Save collection to disk"""
        index_path, metadata_path, docs_path = self._get_collection_path(collection['name'])
        
        # Save FAISS index
        faiss.write_index(collection['index'], index_path)
        
        # Save metadata and documents
        with open(metadata_path, 'wb') as f:
            pickle.dump(collection['metadatas'], f)
        with open(docs_path, 'wb') as f:
            pickle.dump(collection['documents'], f)
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get document count"""
        collection = self.get_or_create_collection(collection_name)
        return len(collection['documents'])
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete collection"""
        if collection_name in self.collections:
            del self.collections[collection_name]
        
        # Delete files
        index_path, metadata_path, docs_path = self._get_collection_path(collection_name)
        for path in [index_path, metadata_path, docs_path]:
            if os.path.exists(path):
                os.remove(path)
        
        logger.info(f"Deleted collection: {collection_name}")
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        collections = set(self.collections.keys())
        
        # Also check disk
        for file in os.listdir(self.persist_directory):
            if file.endswith('.index'):
                collections.add(file.replace('.index', ''))
        
        return list(collections)


# Global instance
_vector_store = None


def get_vector_store() -> FAISSVectorStore:
    """Get or create global FAISS vector store"""
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore()
    return _vector_store
