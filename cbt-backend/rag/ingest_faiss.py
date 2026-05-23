"""
Document Ingestion Pipeline - FAISS Version
Loads documents from knowledge folder into FAISS
"""

# Import numpy compatibility shim first
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy_compat  # noqa

from pathlib import Path
from typing import List, Dict
import logging
from .vector_store_faiss import get_vector_store
from .embeddings import get_embedding_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_documents_from_folder(folder_path: str) -> List[Dict[str, str]]:
    """Load all .txt files from folder"""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        logger.error(f"Folder not found: {folder_path}")
        return documents
    
    for file_path in folder.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            category = file_path.stem.replace('_', ' ').title()
            
            documents.append({
                'content': content,
                'source': file_path.name,
                'category': category
            })
            
            logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
    
    return documents


def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split document into overlapping chunks"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def ingest_documents(
    folder_path: str = None,
    collection_name: str = "cbt_knowledge",
    chunk_size: int = 500,
    reset: bool = False
):
    """
    Ingest documents from folder into FAISS
    
    Args:
        folder_path: Path to knowledge folder
        collection_name: Collection name
        chunk_size: Size of text chunks
        reset: Whether to reset collection
    """
    # Default to knowledge folder
    if folder_path is None:
        current_dir = Path(__file__).parent
        folder_path = current_dir / "knowledge"
    
    logger.info(f"Starting FAISS ingestion from: {folder_path}")
    
    # Load documents
    documents = load_documents_from_folder(str(folder_path))
    
    if not documents:
        logger.warning("No documents found to ingest")
        return
    
    # Get vector store and embedding model
    vector_store = get_vector_store()
    embedding_model = get_embedding_model()
    
    # Reset collection if requested
    if reset:
        logger.info(f"Resetting collection: {collection_name}")
        try:
            vector_store.delete_collection(collection_name)
        except:
            pass
    
    # Process each document
    all_chunks = []
    all_metadatas = []
    
    for doc in documents:
        chunks = chunk_document(doc['content'], chunk_size=chunk_size)
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                'source': doc['source'],
                'category': doc['category'],
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
        
        logger.info(f"Chunked {doc['source']}: {len(chunks)} chunks")
    
    # Generate embeddings
    logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = embedding_model.encode(all_chunks)
    
    # Add to FAISS
    logger.info(f"Adding to FAISS index...")
    vector_store.add_documents(
        collection_name=collection_name,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas
    )
    
    logger.info(f"✓ Ingestion complete! Total documents: {len(all_chunks)}")
    logger.info(f"Collection '{collection_name}' ready for retrieval")


def main():
    """Main ingestion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest CBT knowledge documents into FAISS')
    parser.add_argument('--folder', type=str, help='Path to knowledge folder')
    parser.add_argument('--collection', type=str, default='cbt_knowledge', help='Collection name')
    parser.add_argument('--chunk-size', type=int, default=500, help='Chunk size')
    parser.add_argument('--reset', action='store_true', help='Reset collection before ingesting')
    
    args = parser.parse_args()
    
    ingest_documents(
        folder_path=args.folder,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        reset=args.reset
    )


if __name__ == "__main__":
    main()
