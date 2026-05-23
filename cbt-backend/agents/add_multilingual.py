# Script to add multilingual support to therapy_response.py

with open('therapy_response.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to insert imports
import_insert_line = None
for i, line in enumerate(lines):
    if 'import requests' in line:
        import_insert_line = i + 1
        break

# Add imports
new_imports = [
    'import sys\n',
    'import os\n',
    '\n',
    '# Add path to prompts directory\n',
    'sys.path.append(os.path.join(os.path.dirname(__file__), \'..\'))\n',
    'from prompts.hinglish_examples import get_examples_for_language, format_examples_for_prompt\n',
    '\n'
]

lines = lines[:import_insert_line] + new_imports + lines[import_insert_line:]

# Find the __init__ method and add _detect_language after it
init_end_line = None
for i, line in enumerate(lines):
    if 'self.model = "gpt-oss:120b-cloud"' in line:
        init_end_line = i + 1
        break

# Add _detect_language method
detect_language_method = '''    
    def _detect_language(self, user_input: str) -> str:
        """
        Detect language of user input: english, hindi, or hinglish
        
        Args:
            user_input: User's message
        
        Returns:
            'english', 'hindi', or 'hinglish'
        """
        user_lower = user_input.lower()
        
        # Hindi/Devanagari script detection
        has_devanagari = any('\\u0900' <= char <= '\\u097F' for char in user_input)
        
        # Common Hindi/Hinglish words (romanized)
        hindi_words = [
            'main', 'mujhe', 'hai', 'hoon', 'ka', 'ki', 'ko', 'se', 'mein',
            'aap', 'tum', 'yeh', 'woh', 'kya', 'kaise', 'kyun', 'kab',
            'bahut', 'thoda', 'zyada', 'kam', 'achha', 'bura', 'sahi', 'galat',
            'kar', 'ho', 'tha', 'thi', 'the', 'hoga', 'hogi', 'honge',
            'nahi', 'nahin', 'haan', 'ji', 'yaar', 'bhai', 'dost',
            'kuch', 'sab', 'sabhi', 'koi', 'kaun', 'jab', 'tab',
            'par', 'lekin', 'aur', 'ya', 'toh', 'bhi', 'hi',
            'udaas', 'khush', 'gussa', 'tension', 'pareshan', 'thaka',
            'dukh', 'sukh', 'dar', 'chinta', 'ghabrahat'
        ]
        
        # Count Hindi words
        hindi_word_count = sum(1 for word in hindi_words if word in user_lower)
        
        # English words (common therapy-related)
        english_words = [
            'feeling', 'think', 'thought', 'help', 'need', 'want', 'can',
            'anxious', 'depressed', 'stressed', 'worried', 'scared', 'angry',
            'happy', 'sad', 'tired', 'exhausted', 'overwhelmed'
        ]
        
        # Count English words
        english_word_count = sum(1 for word in english_words if word in user_lower)
        
        # Decision logic
        if has_devanagari:
            return 'hindi'
        elif hindi_word_count >= 3 and english_word_count >= 2:
            return 'hinglish'  # Mix of both
        elif hindi_word_count >= 2:
            return 'hinglish'  # Mostly Hindi with some English
        elif english_word_count >= 2:
            return 'english'
        else:
            # Default based on word count
            if hindi_word_count > english_word_count:
                return 'hinglish'
            else:
                return 'english'

'''

lines = lines[:init_end_line] + [detect_language_method] + lines[init_end_line:]

# Update the THERAPY_PROMPT_TEMPLATE to include language support
# Find and replace the template
for i, line in enumerate(lines):
    if 'THERAPY_PROMPT_TEMPLATE = """You are a skilled CBT therapist' in line:
        # Find the end of the template
        template_end = None
        for j in range(i, len(lines)):
            if 'Therapist:"""' in lines[j]:
                template_end = j + 1
                break
        
        # Replace with new template
        new_template = '''    THERAPY_PROMPT_TEMPLATE = """You are a skilled CBT therapist who speaks English, Hindi, and Hinglish fluently. Provide a COMPLETE therapeutic response that addresses the user's concern fully.

<SESSION_HISTORY>
{session_history}
</SESSION_HISTORY>

<USER_BACKGROUND>
{memory}
</USER_BACKGROUND>

<EMOTIONAL_ANALYSIS>
{analysis}
</EMOTIONAL_ANALYSIS>

<CBT_EVIDENCE>
{evidence}
</CBT_EVIDENCE>

{few_shot_examples}

<OUTPUT_LANGUAGE>{output_language}</OUTPUT_LANGUAGE>

CRITICAL: You MUST respond in {output_language_instruction}. Match the user's language style exactly.

User says: "{user_input}"

Your response MUST include ALL of these elements in a natural, flowing conversation:

1. ACKNOWLEDGE & VALIDATE (1 sentence)
   - Show you heard them by referencing what they just said
   - Validate their emotional experience

2. IDENTIFY THE PATTERN (1-2 sentences)
   - What thought is driving this feeling?
   - What cognitive distortion might be present?
   - How is this thought affecting their behavior?

3. OFFER PERSPECTIVE (1-2 sentences)
   - Provide a balanced, alternative way to view the situation
   - Use CBT evidence from <CBT_EVIDENCE> if available
   - Challenge the unhelpful thought gently

4. ACTIONABLE SOLUTION (1 sentence)
   - Give ONE specific, practical step they can try right now
   - Make it small and achievable

5. CLOSE WITH SUPPORT (1 sentence)
   - End with encouragement or a gentle question
   - Keep the conversation open

CRITICAL REQUIREMENTS:
✓ Response must be COMPLETE - don't cut off mid-thought
✓ Address their SPECIFIC problem, not generic advice
✓ Provide a clear SOLUTION they can act on
✓ End with proper CONCLUSION/next step
✓ Keep it conversational and warm (4-6 sentences total)
✓ NO clinical jargon, NO markdown formatting
✓ MUST respond in {output_language_instruction}
✓ If you don't have enough context, ask clarifying questions

Therapist:"""
'''
        lines = lines[:i] + [new_template] + lines[template_end:]
        break

# Now find the generate() method and add language detection
# Search for the prompt.format call
for i, line in enumerate(lines):
    if 'prompt = prompt_template.format(' in line:
        # Find the closing parenthesis
        format_end = None
        for j in range(i, len(lines)):
            if ')' in lines[j] and 'session_history' in ''.join(lines[i:j+1]):
                format_end = j
                break
        
        # Insert language detection before this
        language_detection_code = '''            
            # Detect user's language
            detected_language = self._detect_language(user_input)
            
            # Get few-shot examples for detected language
            examples = get_examples_for_language(detected_language)
            few_shot_text = format_examples_for_prompt(examples)
            
            # Set output language instruction
            language_map = {
                'english': 'English only',
                'hindi': 'Hindi only (Devanagari or romanized)',
                'hinglish': 'Hinglish (natural mix of Hindi and English)'
            }
            output_lang_instruction = language_map.get(detected_language, 'English')
            
            logger.info(f"Detected language: {detected_language}")
            
'''
        lines = lines[:i] + [language_detection_code] + lines[i:]
        
        # Update the format call to include new parameters
        # Find it again (index shifted)
        for k in range(i, len(lines)):
            if 'prompt = prompt_template.format(' in lines[k]:
                # Find the closing parenthesis
                for m in range(k, len(lines)):
                    if 'session_history=session_memory' in lines[m]:
                        # Add new parameters before the closing
                        lines[m] = lines[m].rstrip() + ',\n'
                        lines.insert(m+1, f'                few_shot_examples=few_shot_text,\n')
                        lines.insert(m+2, f'                output_language=detected_language.upper(),\n')
                        lines.insert(m+3, f'                output_language_instruction=output_lang_instruction\n')
                        break
                break
        break

# Write the updated file
with open('therapy_response.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✓ therapy_response.py updated with multilingual support!")
print("✓ Added _detect_language() method")
print("✓ Updated THERAPY_PROMPT_TEMPLATE with language tags")
print("✓ Added few-shot example injection in generate() method")
