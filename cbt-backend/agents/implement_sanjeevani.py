# Script to implement Sanjeevani's multilingual approach in CBT

import re

with open('therapy_response.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add new methods after _detect_language method
new_methods = '''
    
    def _get_language_specific_instruction(self, language: str) -> str:
        """Get language-specific instruction for system prompt (Sanjeevani approach)"""
        
        if language == 'hinglish':
            return """
CRITICAL LANGUAGE INSTRUCTION:
- You are a CBT therapist fluent in Hinglish
- Mix Hindi and English NATURALLY like a caring friend
- ALWAYS use ROMAN SCRIPT (No Devanagari देवनागरी)
- Example: "Main samajh sakta hoon ki aap anxious feel kar rahe hain"
- Be conversational, warm, and empathetic
- Use common Hinglish words: main, aap, bahut, kaise, achha, tension, etc.
"""
        elif language == 'hindi':
            return """
CRITICAL LANGUAGE INSTRUCTION:
- You are a CBT therapist speaking Hindi
- RESPOND ONLY IN ROMAN SCRIPT TRANSLITERATED HINDI (No Devanagari)
- Example: "Main samajh sakta hoon ki aap chinta mehsoos kar rahe hain"
- Use simple, caring language like talking to a friend
- Keep it natural and warm
"""
        else:  # english
            return """
LANGUAGE INSTRUCTION:
- Respond in clear, natural English
- Be warm, professional, and empathetic
"""
    
    def _filter_devanagari(self, text: str, language: str) -> str:
        """Filter Devanagari characters for Hindi/Hinglish (Sanjeevani approach)"""
        if language in ['hindi', 'hinglish']:
            # Remove Devanagari range (U+0900 to U+097F)
            filtered = ''.join(char for char in text 
                              if not ('\\u0900' <= char <= '\\u097F'))
            return filtered
        return text
'''

# Find the position after _detect_language method
detect_lang_end = content.find('            return \'english\'')
if detect_lang_end != -1:
    # Find the end of the method (next def or class end)
    next_def = content.find('\n    def ', detect_lang_end)
    if next_def != -1:
        content = content[:next_def] + new_methods + content[next_def:]

# Update the generate method to use language-specific instructions
# Find where we build the prompt
old_prompt_build = '''            # Build prompt in correct order: System → Memory → RAG → Visual → User
            prompt_template = self.THERAPY_PROMPT_TEMPLATE'''

new_prompt_build = '''            # Detect user's language
            detected_language = self._detect_language(user_input)
            
            # Get language-specific instruction (Sanjeevani approach)
            lang_instruction = self._get_language_specific_instruction(detected_language)
            
            # Build prompt with language instruction
            prompt_template = lang_instruction + "\\n\\n" + self.THERAPY_PROMPT_TEMPLATE'''

content = content.replace(old_prompt_build, new_prompt_build)

# Update Ollama parameters (Sanjeevani approach)
old_options = '''                "options": {
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
                }'''

new_options = '''                "options": {
                    # OPTIMIZED FOR CBT THERAPY (Sanjeevani approach)
                    "temperature": 0.6,          # Slightly higher for natural flow
                    "top_p": 0.95,               # Higher for better quality
                    "top_k": 50,                 # Balanced exploration
                    "num_ctx": 8192,             # Larger context for 120B model
                    "repeat_penalty": 1.1,       # Slightly reduced penalty
                    "presence_penalty": 0.0,     # Default (Sanjeevani uses 0.0)
                    "frequency_penalty": 0.0,    # Default (Sanjeevani uses 0.0)
                    "num_predict": 1024,         # Longer responses (Sanjeevani: 1024)
                    "mirostat": 2,               # Enable Mirostat v2 for quality
                    "mirostat_tau": 5.0,         # Target entropy
                    "mirostat_eta": 0.1,         # Learning rate
                    "stop": ["User:", "\\n\\nUser:", "Therapist:", "।", "॥"]  # Include Hindi punctuation
                }'''

content = content.replace(old_options, new_options)

# Add Devanagari filtering to response
old_return = '''            therapy_response = result.get("response", "").strip()
            
            logger.info(f"Response generated ({len(therapy_response)} chars)")
            return therapy_response'''

new_return = '''            therapy_response = result.get("response", "").strip()
            
            # Filter Devanagari for Hindi/Hinglish (Sanjeevani approach)
            therapy_response = self._filter_devanagari(therapy_response, detected_language)
            
            logger.info(f"Response generated ({len(therapy_response)} chars) in {detected_language}")
            return therapy_response'''

content = content.replace(old_return, new_return)

# Write updated file
with open('therapy_response.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Sanjeevani's multilingual approach implemented!")
print("✓ Added dynamic language-specific instructions")
print("✓ Added Devanagari filtering")
print("✓ Updated parameters (temp: 0.6, Mirostat v2)")
print("✓ Increased num_predict to 1024")
