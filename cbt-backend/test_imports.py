"""
Quick test to verify all components load correctly
"""

print("Testing component imports...")

try:
    from memory.session_memory import get_session_memory
    from memory.user_memory_faiss import get_user_memory
    print("✓ Memory imports OK")
    
    mm = get_session_memory()
    um = get_user_memory()
    print(f"  - Session memory: {mm is not None}")
    print(f"  - User memory: {um is not None}")
except Exception as e:
    print(f"✗ Memory import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from rag.retriever_faiss import get_retriever
    print("✓ RAG imports OK")
    
    r = get_retriever()
    print(f"  - Retriever: {r is not None}")
except Exception as e:
    print(f"✗ RAG import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from safety.enhanced_safety import get_safety_checker
    print("✓ Safety imports OK")
    
    s = get_safety_checker()
    print(f"  - Safety checker: {s is not None}")
except Exception as e:
    print(f"✗ Safety import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from agents.analyzer import get_analyzer
    from agents.evidence_agent import get_evidence_collector
    from agents.therapy_response import get_therapy_generator
    print("✓ Agents imports OK")
    
    a = get_analyzer()
    e = get_evidence_collector()
    t = get_therapy_generator()
    print(f"  - Analyzer: {a is not None}")
    print(f"  - Evidence collector: {e is not None}")
    print(f"  - Therapy generator: {t is not None}")
except Exception as ex:
    print(f"✗ Agents import failed: {ex}")
    import traceback
    traceback.print_exc()

print("\n✓ All component tests complete!")
