import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will add the enhancement function and then use it in voice_session

enhancement_function = '''
def enhance_for_tts(text: str) -> str:
    """
    Process text to sound more conversational and human-like in Hinglish
    Adds natural pauses (commas) and normalizes pronunciation triggers.
    """
    enhanced = text
    
    # 1. Add pauses after common conversational fillers/starters
    starters = ['achha', 'dekhiye', 'sunie', 'suniye', 'hmm', 'okay', 'to', 'toh', 'bas']
    for word in starters:
        # Case insensitive replace at start of sentence or after punctuation
        # Start of string
        enhanced = re.sub(f'(?i)^{word}\\s+', f'{word.capitalize()}, ', enhanced)
        # After punctuation
        enhanced = re.sub(f'(?i)([.!?]\\s+){word}\\s+', f'\\1{word.capitalize()}, ', enhanced)
        
    # 2. Add flow pauses around Hindi connectors for better phrasing
    # "ki" (that) -> often implies a pause before clause
    enhanced = re.sub(r'(?i)\s+ki\s+', ', ki ', enhanced)
    
    # "lekin/par" (but) -> pause before
    enhanced = re.sub(r'(?i)\s+(lekin|par|magar)\s+', ', \\1 ', enhanced)
    
    # "toh" (then) -> pause before
    enhanced = re.sub(r'(?i)\s+toh\s+', ', toh ', enhanced)
    
    # "kyunki" (because) -> pause before
    enhanced = re.sub(r'(?i)\s+kyunki\s+', ', kyunki ', enhanced)
    
    # "taki" (so that)
    enhanced = re.sub(r'(?i)\s+taki\s+', ', taki ', enhanced)
    
    # 3. Clean up double pronunciation issues
    # "hai" sometimes sounds short. "hain" is nasal. 
    # Ensure clear separation.
    enhanced = enhanced.replace(' hai.', ' hai. ')
    
    # 4. Remove multiple commas created by above rules
    enhanced = re.sub(r',\s*,', ',', enhanced)
    
    return enhanced
'''

# Insert the function before the API routes (e.g., before @app.get)
if 'def enhance_for_tts' not in content:
    # Find a good place, maybe after clean_text_for_speech
    insert_pos = content.find('def clean_text_for_speech')
    # Find end of that function
    # It ends at '    return clean'
    end_pos = content.find('@app.get', insert_pos)
    
    if end_pos != -1:
        content = content[:end_pos] + enhancement_function + '\n\n' + content[end_pos:]
        print("✓ Added enhance_for_tts function")

# 5. Apply the enhancement in voice_session
# Existing: clean_response = clean_text_for_speech(therapy_response)
# Target: clean_response = enhance_for_tts(clean_text_for_speech(therapy_response))

old_call = 'clean_response = clean_text_for_speech(therapy_response)'
new_call = 'clean_response = enhance_for_tts(clean_text_for_speech(therapy_response))'

if old_call in content:
    content = content.replace(old_call, new_call)
    print("✓ Applied enhancement in voice_session")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
