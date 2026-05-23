# Fix therapy_response.py - restore complete generate method with optimized transformer settings

with open('therapy_response.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the corrupted section
# The issue: missing code between logging and response.json()

# Define the complete corrected section
old_section = """            # DEBUG: Log what we're sending to the model
            logger.info("=== DEBUGGING GPT-OSS 120B PIPELINE ===")
            logger.info(f"User Input: {user_input[:100]}")
            logger.info(f"Retrieved Docs Count: {len(evidence.get('techniques', []))}")
            result = response.json()
            therapy_response = result.get("response", "").strip()"""

new_section = """            # DEBUG: Log what we're sending to the model
            logger.info("=== DEBUGGING GPT-OSS 120B PIPELINE ===")
            logger.info(f"User Input: {user_input[:100]}")
            logger.info(f"Retrieved Docs Count: {len(evidence.get('techniques', []))}")
            if evidence.get('techniques'):
                for i, t in enumerate(evidence['techniques'][:2]):
                    logger.info(f"  Doc {i+1}: {t.get('source', 'Unknown')} - {t.get('content', '')[:100]}...")
            logger.info(f"Final Prompt Length: {len(prompt)} chars")
            logger.info(f"Prompt Preview: {prompt[:500]}...")
            
            # Call Ollama with optimized transformer settings for CBT therapy
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    # OPTIMIZED FOR CBT THERAPY (Hindi/Hinglish support)
                    "temperature": 0.55,        # Stable, less hallucination, structured
                    "top_p": 0.92,              # Natural, emotional, conversational
                    "top_k": 50,                # Balanced exploration & accuracy
                    "typical_p": 0.89,          # Reduces rambling, keeps focus
                    "min_p": 0.08,              # Eliminates nonsense & aggressive tone
                    "repeat_penalty": 1.18,     # Stops repetitive phrases
                    "presence_penalty": 0.6,    # Encourages new insights
                    "frequency_penalty": 0.5,   # Prevents idea repetition
                    "num_predict": 700,         # Rich step-by-step therapy
                    "stop": ["User:", "\\n\\nUser:", "Therapist:"]  # Clean single response
                }
            }
            
            logger.info("Generating therapy response...")
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            therapy_response = result.get("response", "").strip()"""

# Replace
content = content.replace(old_section, new_section)

# Write fixed file
with open('therapy_response.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ therapy_response.py fixed with optimized transformer settings!")
print("✓ Temperature: 0.55 (stable)")
print("✓ Top_p: 0.92 (natural)")
print("✓ Top_k: 50 (balanced)")
print("✓ Typical_p: 0.89 (focused)")
print("✓ Min_p: 0.08 (no nonsense)")
print("✓ Repeat_penalty: 1.18 (no repetition)")
print("✓ Num_predict: 700 (rich therapy)")
