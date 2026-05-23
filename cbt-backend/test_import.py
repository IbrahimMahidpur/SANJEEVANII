import sys
import traceback

try:
    import app
    print("App imported successfully!")
except Exception as e:
    print(f"Error importing app: {e}")
    traceback.print_exc()
