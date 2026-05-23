"""
Quick fix script to add missing emotion parsing code to app.py
"""

# Read the file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "logger.info(f"[Session {session_id}] Received audio")"
# and insert emotion parsing code after the STT section

fixed_lines = []
inserted = False

for i, line in enumerate(lines):
    fixed_lines.append(line)
    
    # Look for the line after "os.remove(path)" exception handling
    if 'except:' in line and i > 0 and 'os.remove' in lines[i-2]:
        # Check if next line is "pass"
        if i+1 < len(lines) and 'pass' in lines[i+1]:
            fixed_lines.append(lines[i+1])  # Add the "pass" line
            
            # Now insert the missing code
            if not inserted:
                fixed_lines.append('\n')
                fixed_lines.append('        if not transcript:\n')
                fixed_lines.append('            return JSONResponse({"error":"transcription_failed"}, status_code=500)\n')
                fixed_lines.append('        \n')
                fixed_lines.append('        logger.info(f"[Session {session_id}] Transcript: {transcript}")\n')
                fixed_lines.append('        \n')
                fixed_lines.append('        # Parse emotion data from frontend\n')
                fixed_lines.append('        emotion_data = None\n')
                fixed_lines.append('        if emotion:\n')
                fixed_lines.append('            try:\n')
                fixed_lines.append('                import json\n')
                fixed_lines.append('                emotion_data = json.loads(emotion)\n')
                fixed_lines.append('                logger.info(f"[Session {session_id}] Emotion parameter received: {emotion}")\n')
                fixed_lines.append('                logger.info(f"[Session {session_id}] Visual context: {emotion_data.get(\'emotion\', \'unknown\')} ({emotion_data.get(\'confidence\', 0):.0%})")\n')
                fixed_lines.append('            except Exception as e:\n')
                fixed_lines.append('                logger.warning(f"[Session {session_id}] Failed to parse emotion data: {e}")\n')
                fixed_lines.append('                emotion_data = None\n')
                fixed_lines.append('\n')
                fixed_lines.append('        # 2) Enhanced Safety Check\n')
                fixed_lines.append('        conversation_history = []\n')
                fixed_lines.append('        if memory_manager:\n')
                fixed_lines.append('            conversation_history = memory_manager.session_memory.get_conversation_history(session_id, last_n=5)\n')
                fixed_lines.append('        \n')
                inserted = True
                
                # Skip lines until we find "is_safe = True" or "if safety_checker:"
                skip_until = i + 2
                while skip_until < len(lines) and 'is_safe' not in lines[skip_until] and 'if safety_checker' not in lines[skip_until]:
                    skip_until += 1
                
                # Continue from there
                continue

# Write the fixed file
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✓ app.py fixed! Emotion parsing code added.")
