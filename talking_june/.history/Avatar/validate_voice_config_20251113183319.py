"""
Voice Configuration Validator
Checks all config files and Python code for correct voice settings
"""
import json
import re
from pathlib import Path

print("=" * 80)
print("VOICE CONFIGURATION VALIDATOR")
print("=" * 80)

errors = []
warnings = []
success = []

# Check Python code
print("\n1. Checking Python code (tts.py)...")
tts_file = Path("june/june_va/models/tts.py")
if tts_file.exists():
    content = tts_file.read_text()
    
    # Check for incorrect male voices
    if 'en-IN-Neural2-C' in content:
        errors.append("❌ tts.py still has en-IN-Neural2-C (male voice)")
    else:
        success.append("✅ tts.py: No en-IN-Neural2-C found")
    
    # Check for correct female voices
    if 'en-IN-Neural2-D' in content:
        success.append("✅ tts.py: Found en-IN-Neural2-D (female voice)")
    else:
        warnings.append("⚠️  tts.py: en-IN-Neural2-D not found")
    
    if 'en-US-Neural2-F' in content:
        success.append("✅ tts.py: Found en-US-Neural2-F (female voice)")
    else:
        warnings.append("⚠️  tts.py: en-US-Neural2-F not found")

# Check config files
print("\n2. Checking configuration files...")
config_files = [
    "june/config.json",
    "june/config-enhanced-multilingual.json",
    "june/gcloud-multilang-config.json",
]

for config_path in config_files:
    config_file = Path(config_path)
    if not config_file.exists():
        warnings.append(f"⚠️  {config_path} not found")
        continue
    
    try:
        config = json.loads(config_file.read_text())
        tts_config = config.get("tts", {}).get("generation_args", {})
        
        voice_name = tts_config.get("voice_name", "")
        ssml_gender = tts_config.get("ssml_gender", "")
        
        # Check for male voice with female gender
        if "Neural2-C" in voice_name and "FEMALE" in ssml_gender:
            errors.append(f"❌ {config_path}: Male voice (Neural2-C) with FEMALE gender")
        elif "Neural2-C" in voice_name:
            warnings.append(f"⚠️  {config_path}: Using Neural2-C (male voice)")
        else:
            success.append(f"✅ {config_path}: No Neural2-C found")
        
        # Check for correct female voices
        if "Neural2-D" in voice_name or "Neural2-F" in voice_name:
            success.append(f"✅ {config_path}: Using female voice ({voice_name})")
        
        # Check voice preferences
        voice_prefs = tts_config.get("voice_preferences", {})
        for lang, prefs in voice_prefs.items():
            voice = prefs.get("voice_name", "")
            if "Neural2-C" in voice and lang.startswith("en"):
                errors.append(f"❌ {config_path}: {lang} uses male voice (Neural2-C)")
            elif "Neural2-D" in voice or "Neural2-F" in voice:
                success.append(f"✅ {config_path}: {lang} uses female voice ({voice})")
    
    except Exception as e:
        errors.append(f"❌ Error reading {config_path}: {str(e)}")

# Print results
print("\n" + "=" * 80)
print("VALIDATION RESULTS")
print("=" * 80)

if success:
    print("\n✅ PASSED CHECKS:")
    for s in success:
        print(f"  {s}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for w in warnings:
        print(f"  {w}")

if errors:
    print("\n❌ ERRORS FOUND:")
    for e in errors:
        print(f"  {e}")
    print("\n⚠️  FIX REQUIRED! Errors must be resolved before running.")
else:
    print("\n" + "=" * 80)
    print("🎉 ALL CHECKS PASSED! Voice configuration is correct.")
    print("=" * 80)
    print("\nYou can now safely run the application:")
    print("  - run_all.bat")
    print("  - RUN_PROJECT_SMART.bat")
    print("  - RUN_QUICK.bat")

print()
