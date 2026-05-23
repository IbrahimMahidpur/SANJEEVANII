# Add this import at the top of therapy_response.py after existing imports
import sys
import os

# Add path to prompts directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from prompts.hinglish_examples import get_examples_for_language, format_examples_for_prompt


# Add this method to TherapyResponseGenerator class (after __init__)
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
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in user_input)
    
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


# Updated system prompt with language support
THERAPY_PROMPT_TEMPLATE_MULTILINGUAL = """You are a skilled CBT therapist who speaks English, Hindi, and Hinglish fluently. Provide a COMPLETE therapeutic response that addresses the user's concern fully.

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

print("✓ Language detection and multilingual prompt template ready!")
print("✓ Add _detect_language() method to TherapyResponseGenerator class")
print("✓ Update THERAPY_PROMPT_TEMPLATE to THERAPY_PROMPT_TEMPLATE_MULTILINGUAL")
print("✓ In generate() method, detect language and add few-shot examples")
