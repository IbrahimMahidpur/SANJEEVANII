
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the lines that add breaks
# We'll replace them with empty strings or comments
content = content.replace('safe_reply = safe_reply.replace(". ", ". <break time=\\\"400ms\\\"/> ")', '')
content = content.replace('safe_reply = safe_reply.replace("? ", "? <break time=\\\"500ms\\\"/> ")', '')
content = content.replace('safe_reply = safe_reply.replace(", ", ", <break time=\\\"200ms\\\"/> ")', '')

# Also simplify the SSML wrapper to remove start/end breaks if they are annoying
old_ssml = '''        ssml = f"""<speak>
            <break time="400ms"/>
            {safe_reply}
            <break time="600ms"/>
        </speak>"""'''

new_ssml = '''        ssml = f"""<speak>
            {safe_reply}
        </speak>"""'''

# Try to find and replace the SSML block
# Use flexible replacement since indentation might vary
if old_ssml in content:
    content = content.replace(old_ssml, new_ssml)
else:
    # If exact match fails, try regex or just manual cleaner
    # The user is sensitive to pauses, so let's kill the break tags we added
    content = re.sub(r'<break time="\d+ms"/>', '', content)
    # But wait, we passed safe_reply into f-string, so removing it from source code content via regex might be risky if we target the *generation* logic.
    # The safe_reply.replace calls are what adds them. I already removed those specific lines above.
    # Now I just need to clean up the wrapper.
    if '<break time="400ms"/>' in content and '{safe_reply}' in content:
        # Use a more aggressive replacement for the wrapper part
        content = re.sub(r'ssml = f"""<speak>.*?{safe_reply}.*?</speak>"""', 'ssml = f"""<speak>{safe_reply}</speak>"""', content, flags=re.DOTALL)


with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
    
print("Removed manual breaks from app.py")
