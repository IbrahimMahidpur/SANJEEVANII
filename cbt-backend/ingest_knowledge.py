"""
Standalone Knowledge Base Ingestion Script
Patches numpy compatibility BEFORE any imports
"""

# CRITICAL: Patch numpy FIRST, before any other imports
import numpy as np
if not hasattr(np, 'float_'):
    np.float_ = np.float64
    np.int_ = np.int64
    np.bool_ = np.bool
    np.object_ = np.object
    np.str_ = np.str_
    np.complex_ = np.complex128
    print("✓ Applied numpy compatibility patch")

# Now safe to import everything else
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.vector_store_faiss import get_vector_store
from rag.embeddings import get_embedding_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_ingest():
    """Load and ingest CBT knowledge base"""
    
    # Get knowledge folder
    knowledge_folder = Path(__file__).parent / "rag" / "knowledge"
    
    if not knowledge_folder.exists():
        logger.error(f"Knowledge folder not found: {knowledge_folder}")
        return False
    
    logger.info(f"Loading documents from: {knowledge_folder}")
    
    # Load all .txt files
    all_chunks = []
    all_metadatas = []
    
    for file_path in knowledge_folder.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            category = file_path.stem.replace('_', ' ').title()
            logger.info(f"Loaded: {file_path.name} ({len(content)} chars)")
            
            # Simple chunking by paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < 500:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            logger.info(f"  Chunked into {len(chunks)} pieces")
            
            # Add to collection
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    'source': file_path.name,
                    'category': category,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
        
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
    
    if not all_chunks:
        logger.error("No documents loaded!")
        return False
    
    logger.info(f"\n✓ Loaded {len(all_chunks)} total chunks")
    
    # Get vector store and embedding model
    logger.info("Initializing FAISS vector store...")
    vector_store = get_vector_store()
    
    logger.info("Loading embedding model (this may take a moment)...")
    embedding_model = get_embedding_model()
    
    # Reset collection
    try:
        vector_store.delete_collection("cbt_knowledge")
        logger.info("Cleared existing collection")
    except:
        pass
    
    # Generate embeddings
    logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
    embeddings = embedding_model.encode(all_chunks)
    logger.info(f"✓ Generated embeddings (shape: {embeddings.shape})")
    
    # Add to FAISS
    logger.info("Adding to FAISS index...")
    vector_store.add_documents(
        collection_name="cbt_knowledge",
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas
    )
    
    logger.info(f"\n🎉 SUCCESS! Ingested {len(all_chunks)} documents into FAISS")
    logger.info("Knowledge base is ready for retrieval!")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CBT Knowledge Base Ingestion (FAISS)")
    print("="*60 + "\n")
    
    success = load_and_ingest()
    
    if success:
        print("\n✅ Ingestion complete!")
        print("You can now use the RAG system for evidence-based responses.")
    else:
        print("\n❌ Ingestion failed. Check the logs above.")
        sys.exit(1)
