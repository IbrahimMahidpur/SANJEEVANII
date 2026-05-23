# Script to fix multilingual prompt logic in therapy_response.py

with open('therapy_response.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove duplicate method definition
# The first one is around line 155, the second (good) one around line 193.
# We will identify them by their docstrings or content.

# Search for the first occurrence and remove it
first_def = content.find('    def _get_language_specific_instruction(self, language: str) -> str:')
second_def = content.find('    def _get_language_specific_instruction(self, language: str) -> str:', first_def + 1)

if first_def != -1 and second_def != -1:
    # We have duplicates. Remove the first one.
    # Find end of first method
    next_method = content.find('    def _filter_devanagari', first_def)
    if next_method != -1:
        content = content[:first_def] + content[next_method:]
        print("✓ Removed duplicate method definition")

# 2. Fix generate method prompt logic
# We want to remove the prepend logic and use the instruction for the format variable

# Remove the prepend logic
prepend_code = '''            # Get language-specific instruction (Sanjeevani approach)
            lang_instruction = self._get_language_specific_instruction(detected_language)
            
            # Build prompt with language instruction
            prompt_template = lang_instruction + "\\n\\n" + self.THERAPY_PROMPT_TEMPLATE
            if visual_context:
                # Insert visual context before user input
                prompt_template = prompt_template.replace(
                    'User says: "{user_input}"',
                    visual_context + '\\n\\nUser says: "{user_input}"'
                )'''

# We want to keep visual context logic but remove the prepend
replacement_code = '''            # Get language-specific instruction (Sanjeevani approach)
            lang_instruction = self._get_language_specific_instruction(detected_language)
            
            # Base template
            prompt_template = self.THERAPY_PROMPT_TEMPLATE
            
            if visual_context:
                # Insert visual context before user input
                prompt_template = prompt_template.replace(
                    'User says: "{user_input}"',
                    visual_context + '\\n\\nUser says: "{user_input}"'
                )'''

if prepend_code in content:
    content = content.replace(prepend_code, replacement_code)
    print("✓ Fixed prompt template construction")
else:
    # Try fuzzy match or manual replacement if exact string match fails
    # Let's try replacing the specific prepend line if the block match failed
    if 'prompt_template = lang_instruction + "\\n\\n" + self.THERAPY_PROMPT_TEMPLATE' in content:
        content = content.replace('prompt_template = lang_instruction + "\\n\\n" + self.THERAPY_PROMPT_TEMPLATE', 'prompt_template = self.THERAPY_PROMPT_TEMPLATE')
        print("✓ Fixed prompt template construction (simple replacement)")

# 3. Update the .format() call to use lang_instruction
old_format = '''            # Set output language instruction
            language_map = {
                'english': 'English only',
                'hindi': 'Hindi only (Devanagari or romanized)',
                'hinglish': 'Hinglish (natural mix of Hindi and English)'
            }
            output_lang_instruction = language_map.get(detected_language, 'English')'''

new_format = '''            # Set output language instruction using Sanjeevani logic
            # This puts the strong instruction RIGHT into the CRITICAL section
            output_lang_instruction = lang_instruction'''

if old_format in content:
    content = content.replace(old_format, new_format)
    print("✓ Updated format call to use strong instructions")

# 4. Remove the duplicate _detect_language call in generate method (lines 295-296 in viewed file)
# It was called once before prompt build, and again after.
duplicate_detect = '''            
            # Detect user's language
            detected_language = self._detect_language(user_input)'''
            
# We can just remove the second occurrence if it exists, or rely on the previous logic already having detected it
# The second occurrence is usually right before "Get few-shot examples"
# Let's find "Get few-shot examples" and see if detect logic is right before it

few_shot_marker = '            # Get few-shot examples for detected language'
detect_marker = '            detected_language = self._detect_language(user_input)'

# Logic: detected_language is needed for _get_language_specific_instruction (which we moved up)
# So we must ensure it is defined early.
# In my previous script I added detection logic early.
# So the second detection is redundant but harmless, unless it resets something. 
# We'll leave it or clean it if easy.

with open('therapy_response.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixes applied to therapy_response.py")
