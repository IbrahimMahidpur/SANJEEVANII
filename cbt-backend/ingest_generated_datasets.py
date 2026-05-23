# ingest_generated_datasets.py
"""
FAISS-based ingestion system for generated CBT datasets
Embeds and indexes all generated JSON files into FAISS vector store
"""
import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm

# Configuration
DATA_DIR = "generated_datasets"
FAISS_INDEX_PATH = "rag/faiss_generated.index"
METADATA_PATH = "rag/faiss_generated_metadata.pkl"
EMB_MODEL = "sentence-transformers/all-mpnet-base-v2"  # High quality embeddings

# Chunking configuration
CHUNK_SIZE_WORDS = 250
CHUNK_OVERLAP_WORDS = 50

print("Loading embedding model...")
embedder = SentenceTransformer(EMB_MODEL)
embedding_dim = embedder.get_sentence_embedding_dimension()

print(f"Embedding dimension: {embedding_dim}")
print(f"Model: {EMB_MODEL}")

def chunk_text(text, chunk_size_words=CHUNK_SIZE_WORDS, overlap_words=CHUNK_OVERLAP_WORDS):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size_words])
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
        i += (chunk_size_words - overlap_words)
        if i >= len(words):
            break
    return chunks if chunks else [text]  # Return original if no chunks created

def process_dataset_file(filepath):
    """Process a single JSON dataset file"""
    with open(filepath, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    all_chunks = []
    all_metadata = []
    
    for item in items:
        # Extract text based on item type
        if "turns" in item:  # Conversation format
            # Combine conversation turns into single text
            text = " ".join([turn["text"] for turn in item["turns"]])
        else:
            text = item.get("text", "")
        
        if not text.strip():
            continue
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Create metadata for each chunk
        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadata.append({
                "source_file": os.path.basename(filepath),
                "category": item.get("category", "unknown"),
                "topic": item.get("topic", "general"),
                "language": item.get("language", "english"),
                "safety_level": item.get("safety_level", "safe"),
                "original_id": item.get("id", ""),
                "created_at": item.get("created_at", ""),
                "tags": item.get("tags", [])
            })
    
    return all_chunks, all_metadata

def main():
    print("\n" + "="*60)
    print("FAISS Ingestion for Generated CBT Datasets")
    print("="*60 + "\n")
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: {DATA_DIR} not found. Run generate_cbt_datasets.py first.")
        return
    
    # Collect all JSON files
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {DATA_DIR}")
        return
    
    print(f"Found {len(json_files)} dataset files:")
    for f in json_files:
        print(f"  - {f}")
    print()
    
    # Process all files
    all_chunks = []
    all_metadata = []
    
    for json_file in json_files:
        filepath = os.path.join(DATA_DIR, json_file)
        print(f"Processing {json_file}...")
        
        chunks, metadata = process_dataset_file(filepath)
        all_chunks.extend(chunks)
        all_metadata.extend(metadata)
        
        print(f"  ✓ Added {len(chunks):,} chunks")
    
    print(f"\nTotal chunks to embed: {len(all_chunks):,}")
    
    # Generate embeddings in batches
    print("\nGenerating embeddings...")
    batch_size = 256
    all_embeddings = []
    
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Embedding"):
        batch = all_chunks[i:i+batch_size]
        embeddings = embedder.encode(batch, show_progress_bar=False, convert_to_numpy=True)
        all_embeddings.append(embeddings)
    
    # Combine all embeddings
    all_embeddings = np.vstack(all_embeddings).astype('float32')
    
    print(f"Embeddings shape: {all_embeddings.shape}")
    
    # Create FAISS index
    print("\nCreating FAISS index...")
    index = faiss.IndexFlatL2(embedding_dim)  # L2 distance
    
    # Add vectors to index
    index.add(all_embeddings)
    
    print(f"✓ Index created with {index.ntotal:,} vectors")
    
    # Save index
    print(f"\nSaving FAISS index to {FAISS_INDEX_PATH}...")
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    # Save metadata
    print(f"Saving metadata to {METADATA_PATH}...")
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump({
            'metadata': all_metadata,
            'chunks': all_chunks
        }, f)
    
    print("\n" + "="*60)
    print("✓ Ingestion Complete!")
    print("="*60)
    print(f"Total vectors indexed: {len(all_chunks):,}")
    print(f"Index file: {FAISS_INDEX_PATH}")
    print(f"Metadata file: {METADATA_PATH}")
    print(f"Embedding model: {EMB_MODEL}")
    print(f"Embedding dimension: {embedding_dim}")
    
    # Statistics
    print("\nDataset Statistics:")
    categories = {}
    languages = {}
    safety_levels = {}
    
    for meta in all_metadata:
        cat = meta['category']
        lang = meta['language']
        safety = meta['safety_level']
        
        categories[cat] = categories.get(cat, 0) + 1
        languages[lang] = languages.get(lang, 0) + 1
        safety_levels[safety] = safety_levels.get(safety, 0) + 1
    
    print("\nBy Category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count:,} chunks")
    
    print("\nBy Language:")
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {count:,} chunks")
    
    print("\nBy Safety Level:")
    for safety, count in sorted(safety_levels.items(), key=lambda x: -x[1]):
        print(f"  {safety}: {count:,} chunks")
    
    print("\n✓ Ready for RAG retrieval!")

if __name__ == "__main__":
    main()
