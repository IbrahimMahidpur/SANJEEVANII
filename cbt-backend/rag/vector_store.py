"""
Vector Store using ChromaDB
Handles document storage and retrieval
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document storage and retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info("ChromaDB initialized successfully")
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> chromadb.Collection:
        """
        Get existing collection or create new one
        
        Args:
            name: Collection name
            metadata: Optional metadata for collection
        
        Returns:
            ChromaDB collection
        """
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata or {}
            )
            logger.info(f"Collection '{name}' ready. Count: {collection.count()}")
            return collection
        except Exception as e:
            logger.error(f"Error creating collection '{name}': {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to collection
        
        Args:
            collection_name: Name of collection
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs (auto-generated if None)
        """
        collection = self.get_or_create_collection(collection_name)
        
        # Generate IDs if not provided
        if ids is None:
            existing_count = collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Add documents
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to '{collection_name}'")
    
    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query collection for similar documents
        
        Args:
            collection_name: Name of collection
            query_texts: List of query texts
            n_results: Number of results per query
            where: Metadata filter
            where_document: Document content filter
        
        Returns:
            Query results with documents, distances, and metadatas
        """
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        return results
    
    def query_single(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query collection for a single query text
        
        Args:
            collection_name: Name of collection
            query_text: Query text
            n_results: Number of results
            where: Metadata filter
        
        Returns:
            List of result dicts with document, metadata, and distance
        """
        results = self.query(
            collection_name=collection_name,
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else None,
                'id': results['ids'][0][i]
            })
        
        return formatted_results
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection '{collection_name}': {e}")
    
    def list_collections(self) -> List[str]:
        """List all collection names"""
        collections = self.client.list_collections()
        return [c.name for c in collections]
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get document count in collection"""
        collection = self.get_or_create_collection(collection_name)
        return collection.count()
    
    def reset(self) -> None:
        """Reset entire database (use with caution!)"""
        logger.warning("Resetting entire ChromaDB database!")
        self.client.reset()


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
