# Quick fix script to test if agents work
import sys
sys.path.insert(0, '.')

print("="*60)
print("Testing Agent Initialization")
print("="*60)

# Test imports
from agents.analyzer import get_analyzer
from agents.evidence_agent import get_evidence_collector
from agents.therapy_response import get_therapy_generator

# Initialize
analyzer = get_analyzer()
evidence = get_evidence_collector()
therapy = get_therapy_generator()

print(f"\nAnalyzer: {analyzer is not None}")
print(f"Evidence Collector: {evidence is not None}")
print(f"Therapy Generator: {therapy is not None}")

if therapy:
    print("\n✓ Therapy generator is working!")
    print(f"Type: {type(therapy)}")
    
    # Test it
    test_response = therapy.generate(
        user_input="I'm feeling anxious",
        analysis={'emotions': ['anxiety'], 'intensity': 7},
        evidence={'techniques': [], 'rag_context': ''},
        session_memory="",
        user_memory=""
    )
    
    print(f"\nTest Response: {test_response[:100]}...")
else:
    print("\n✗ Therapy generator is None!")

print("="*60)
