"""
Quick Setup Script for Enhanced CBT System
Handles numpy compatibility and starts the system
"""

import subprocess
import sys
import os

def main():
    print("🚀 Setting up Enhanced CBT System...")
    
    # Check if we're in the right directory
    if not os.path.exists('rag'):
        print("❌ Error: Run this from cbt-backend directory")
        sys.exit(1)
    
    print("\n1. Checking dependencies...")
    try:
        import chromadb
        import sentence_transformers
        print("✓ Core dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "chromadb", "sentence-transformers"])
    
    print("\n2. Testing ChromaDB...")
    try:
        # Test ChromaDB with numpy workaround
        import numpy as np
        if not hasattr(np, 'float_'):
            # Add compatibility shim
            np.float_ = np.float64
            np.int_ = np.int64
        
        from rag.vector_store import get_vector_store
        vs = get_vector_store()
        print("✓ ChromaDB initialized successfully")
        
        print("\n3. Ingesting knowledge base...")
        from rag.ingest import ingest_documents
        ingest_documents(reset=True)
        print("✓ Knowledge base ingested")
        
    except Exception as e:
        print(f"⚠️  ChromaDB issue: {e}")
        print("System will work but RAG features may be limited")
    
    print("\n4. Testing other components...")
    try:
        from memory.memory_manager import get_memory_manager
        from safety.enhanced_safety import get_safety_checker
        from agents.analyzer import get_analyzer
        
        mm = get_memory_manager()
        sc = get_safety_checker()
        an = get_analyzer()
        
        print("✓ Memory system ready")
        print("✓ Safety system ready")
        print("✓ Agent system ready")
        
    except Exception as e:
        print(f"❌ Component error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Setup complete!")
    print("\nTo start the backend:")
    print("  python app.py")
    print("\nTo access the app:")
    print("  http://localhost:3000/cbt")

if __name__ == "__main__":
    main()
