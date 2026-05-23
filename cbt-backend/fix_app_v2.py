# Simple line-by-line fix for app.py
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The problem: line 284 onwards has wrong indentation and missing code
# We need to insert proper code after line 283 (STT transcribe)

new_lines = lines[:283]  # Keep everything up to and including line 283

# Add the missing code with correct indentation
new_lines.append('\n')
new_lines.append('        try:\n')
new_lines.append('            os.remove(path)\n')
new_lines.append('        except:\n')
new_lines.append('            pass\n')
new_lines.append('\n')
new_lines.append('        if not transcript:\n')
new_lines.append('            return JSONResponse({"error":"transcription_failed"}, status_code=500)\n')
new_lines.append('        \n')
new_lines.append('        logger.info(f"[Session {session_id}] Transcript: {transcript}")\n')
new_lines.append('        \n')
new_lines.append('        # Parse emotion data from frontend\n')
new_lines.append('        emotion_data = None\n')
new_lines.append('        if emotion:\n')
new_lines.append('            try:\n')
new_lines.append('                import json\n')
new_lines.append('                emotion_data = json.loads(emotion)\n')
new_lines.append('                logger.info(f"[Session {session_id}] Emotion: {emotion_data.get(\'emotion\')} ({emotion_data.get(\'confidence\', 0):.0%})")\n')
new_lines.append('            except Exception as e:\n')
new_lines.append('                logger.warning(f"[Session {session_id}] Failed to parse emotion: {e}")\n')
new_lines.append('                emotion_data = None\n')
new_lines.append('\n')
new_lines.append('        # 2) Enhanced Safety Check\n')
new_lines.append('        conversation_history = []\n')
new_lines.append('        if memory_manager:\n')
new_lines.append('            conversation_history = memory_manager.session_memory.get_conversation_history(session_id, last_n=5)\n')
new_lines.append('        \n')
new_lines.append('        is_safe = True\n')
new_lines.append('        if safety_checker:\n')
new_lines.append('            is_safe, risk_assessment = safety_checker.check_safety(transcript, conversation_history)\n')
new_lines.append('        \n')
new_lines.append('        if not is_safe:\n')
new_lines.append('            logger.error(f"[Session {session_id}] CRISIS DETECTED")\n')
new_lines.append('            crisis_text = safety_checker.get_crisis_response() if safety_checker else "Please seek immediate help."\n')
new_lines.append('            audio_path = synthesize_tts(crisis_text, lang_code=language or DEFAULT_LANG)\n')
new_lines.append('            \n')

# Now find where the rest of the code continues (after the crisis handling)
# Look for "# 3) Agent 1: Analyze"
found_agent1 = False
for i in range(284, len(lines)):
    if '# 3) Agent 1: Analyze' in lines[i] or 'Agent 1' in lines[i]:
        # Add the rest from here
        new_lines.extend(lines[i:])
        found_agent1 = True
        break

if not found_agent1:
    print("ERROR: Could not find Agent 1 section!")
else:
    # Write the fixed file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✓ app.py fixed with proper indentation and emotion parsing!")
