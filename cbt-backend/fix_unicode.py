import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode symbols with ASCII-safe alternatives
replacements = {
    '✓': '[OK]',
    '⚠': '[WARNING]',
    '✗': '[ERROR]',
    '🚀': '',
    '═': '=',
}

for unicode_char, ascii_char in replacements.items():
    content = content.replace(unicode_char, ascii_char)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Replaced Unicode symbols with ASCII-safe alternatives")
