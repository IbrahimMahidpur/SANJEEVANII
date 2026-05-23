# Fix therapy_response.py - restore _detect_emotion_mismatch with Hindi/Hinglish support

with open('therapy_response.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the _detect_emotion_mismatch method and replace it completely
new_lines = []
in_mismatch_method = False
skip_until_next_method = False

for i, line in enumerate(lines):
    # Start of _detect_emotion_mismatch
    if 'def _detect_emotion_mismatch' in line:
        in_mismatch_method = True
        skip_until_next_method = True
        
        # Add the complete corrected method
        new_lines.append(line)  # def line
        new_lines.append('        """\n')
        new_lines.append('        Detect if facial emotion contradicts verbal query (Multilingual: English/Hindi/Hinglish)\n')
        new_lines.append('        Returns mismatch info if significant contradiction detected\n')
        new_lines.append('        """\n')
        new_lines.append('        if not emotion_data or not emotion_data.get(\'face_detected\'):\n')
        new_lines.append('            return None\n')
        new_lines.append('        \n')
        new_lines.append('        face_emotion = emotion_data.get(\'emotion\', \'neutral\')\n')
        new_lines.append('        confidence = emotion_data.get(\'confidence\', 0)\n')
        new_lines.append('        \n')
        new_lines.append('        # Only check if confidence is high enough\n')
        new_lines.append('        if confidence < 0.5:\n')
        new_lines.append('            return None\n')
        new_lines.append('        \n')
        new_lines.append('        user_input_lower = user_input.lower()\n')
        new_lines.append('        \n')
        new_lines.append('        # Define emotion keywords (English + Hindi + Hinglish)\n')
        new_lines.append('        emotion_keywords = {\n')
        new_lines.append('            \'happy\': [\n')
        new_lines.append('                # English\n')
        new_lines.append('                \'happy\', \'great\', \'wonderful\', \'excited\', \'joyful\', \'good\', \'better\',\n')
        new_lines.append('                # Hindi\n')
        new_lines.append('                \'khush\', \'achha\', \'mast\', \'badiya\',\n')
        new_lines.append('                # Hinglish\n')
        new_lines.append('                \'bahut achha\', \'ekdum mast\', \'sahi hai\'\n')
        new_lines.append('            ],\n')
        new_lines.append('            \'sad\': [\n')
        new_lines.append('                # English\n')
        new_lines.append('                \'sad\', \'depressed\', \'down\', \'unhappy\', \'miserable\', \'hopeless\',\n')
        new_lines.append('                # Hindi\n')
        new_lines.append('                \'udaas\', \'dukhi\', \'pareshan\', \'rona\',\n')
        new_lines.append('                # Hinglish\n')
        new_lines.append('                \'bahut dukh\', \'ro raha\', \'dil toot gaya\'\n')
        new_lines.append('            ],\n')
        new_lines.append('            \'angry\': [\n')
        new_lines.append('                # English\n')
        new_lines.append('                \'angry\', \'mad\', \'furious\', \'frustrated\', \'irritated\', \'annoyed\',\n')
        new_lines.append('                # Hindi\n')
        new_lines.append('                \'gussa\', \'krodh\', \'chidh\', \'naraz\',\n')
        new_lines.append('                # Hinglish\n')
        new_lines.append('                \'bahut gussa\', \'chidh gayi\', \'gussa aa raha\'\n')
        new_lines.append('            ],\n')
        new_lines.append('            \'anxious\': [\n')
        new_lines.append('                # English\n')
        new_lines.append('                \'anxious\', \'worried\', \'nervous\', \'stressed\', \'scared\', \'afraid\',\n')
        new_lines.append('                # Hindi\n')
        new_lines.append('                \'chinta\', \'ghabrahat\', \'dar\', \'tension\',\n')
        new_lines.append('                # Hinglish\n')
        new_lines.append('                \'bahut tension\', \'dar lag raha\', \'ghabra gaya\'\n')
        new_lines.append('            ],\n')
        new_lines.append('            \'tired\': [\n')
        new_lines.append('                # English\n')
        new_lines.append('                \'tired\', \'exhausted\', \'fatigued\', \'drained\', \'sleepy\',\n')
        new_lines.append('                # Hindi\n')
        new_lines.append('                \'thaka\', \'kamzor\', \'neend\', \'susti\',\n')
        new_lines.append('                # Hinglish\n')
        new_lines.append('                \'bahut thaka\', \'neend aa rahi\', \'bilkul thak gaya\'\n')
        new_lines.append('            ]\n')
        new_lines.append('        }\n')
        new_lines.append('        \n')
        new_lines.append('        # Detect verbal emotion from query\n')
        new_lines.append('        detected_verbal_emotion = None\n')
        new_lines.append('        for emotion, keywords in emotion_keywords.items():\n')
        new_lines.append('            if any(keyword in user_input_lower for keyword in keywords):\n')
        new_lines.append('                detected_verbal_emotion = emotion\n')
        new_lines.append('                break\n')
        new_lines.append('        \n')
        new_lines.append('        # No verbal emotion detected - no mismatch\n')
        new_lines.append('        if not detected_verbal_emotion:\n')
        new_lines.append('            return None\n')
        new_lines.append('        \n')
        new_lines.append('        # Check for contradictions (intelligent rules)\n')
        new_lines.append('        contradictions = {\n')
        new_lines.append('            \'happy\': [\'sad\', \'angry\', \'anxious\'],\n')
        new_lines.append('            \'sad\': [\'happy\'],\n')
        new_lines.append('            \'angry\': [\'happy\'],\n')
        new_lines.append('            \'anxious\': [\'happy\'],\n')
        new_lines.append('        }\n')
        new_lines.append('        \n')
        new_lines.append('        # Neutral is acceptable with any verbal emotion\n')
        new_lines.append('        if face_emotion == \'neutral\':\n')
        new_lines.append('            return None\n')
        new_lines.append('        \n')
        new_lines.append('        # Check if there\'s a contradiction\n')
        new_lines.append('        if face_emotion in contradictions:\n')
        new_lines.append('            if detected_verbal_emotion in contradictions[face_emotion]:\n')
        new_lines.append('                return {\n')
        new_lines.append('                    \'face_emotion\': face_emotion,\n')
        new_lines.append('                    \'verbal_emotion\': detected_verbal_emotion,\n')
        new_lines.append('                    \'confidence\': confidence,\n')
        new_lines.append('                    \'mismatch_type\': f"{face_emotion}_face_but_{detected_verbal_emotion}_words"\n')
        new_lines.append('                }\n')
        new_lines.append('        \n')
        new_lines.append('        return None\n')
        new_lines.append('    \n')
        continue
    
    # Skip lines until next method
    if skip_until_next_method:
        if line.strip().startswith('def ') and 'def _detect_emotion_mismatch' not in line:
            skip_until_next_method = False
            new_lines.append(line)
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Write fixed file
with open('therapy_response.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ therapy_response.py fixed with Hindi/Hinglish support!")
