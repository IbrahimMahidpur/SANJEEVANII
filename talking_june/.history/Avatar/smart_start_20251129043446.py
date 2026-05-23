"""
Smart Startup - Automatically stops old processes and starts fresh
"""
import socket
import subprocess
import time
import sys
from pathlib import Path

def is_port_in_use(port):
    """Check if port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return False
        except OSError:
            return True

def kill_port(port):
    """Kill process using the port."""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"  Killing process {pid} on port {port}...")
                    subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
                    time.sleep(1)
                    return True
        return False
    except Exception as e:
        print(f"  Error killing port {port}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 Smart Startup - June VA + TalkingHead")
    print("="*60 + "\n")
    
    # Check and clean ports
    ports = {
        8765: "WebSocket Bridge",
        8001: "HTTP Audio Server",
        8080: "TalkingHead Frontend"
    }
    
    print("Checking ports...\n")
    for port, name in ports.items():
        if is_port_in_use(port):
            print(f"⚠️  {name} (Port {port}) is already running")
            print(f"  Stopping old process...")
            kill_port(port)
            time.sleep(1)
            
            if is_port_in_use(port):
                print(f"❌ Failed to stop port {port}")
                print(f"   Please manually close the window using port {port}\n")
                input("Press Enter after closing...")
            else:
                print(f"✅ Port {port} is now free\n")
        else:
            print(f"✅ {name} (Port {port}) is free\n")
    
    print("="*60)
    print("Starting services...\n")
    
    root = Path(__file__).parent
    
    # Start Bridge Server
    print("1️⃣ Starting Bridge Server...")
    subprocess.Popen(
        'start "Bridge Server" cmd /k "python bridge_server.py"',
        shell=True,
        cwd=root
    )
    time.sleep(3)
    
    # Start TalkingHead
    print("2️⃣ Starting TalkingHead...")
    subprocess.Popen(
        f'start "TalkingHead" cmd /k "cd /d {root}\\TalkingHead && python -m http.server 8080"',
        shell=True
    )
    time.sleep(2)
    
    # Open Browser
    print("3️⃣ Opening browser...")
    subprocess.Popen('start http://localhost:8080', shell=True)
    time.sleep(2)
    
    # Start June VA
    print("4️⃣ Starting June VA...")
    creds = r"C:\Users\imahi\avatar_talking\Avatar\vaani-474822-49ec0963711e.json"
    subprocess.Popen(
        f'start "June VA" cmd /k "cd /d {root}\\june && set GOOGLE_APPLICATION_CREDENTIALS={creds} && python -m june_va --config config.json"',
        shell=True
    )
    
    print("\n" + "="*60)
    print("✅ All services started!")
    print("="*60 + "\n")
    
    print("📋 Next Steps:\n")
    print("1. Browser mein avatar dikhai dega")
    print("2. Press F12 → Console check karo")
    print("3. Dekho: '[June Bridge] ✅ Connected'")
    print("4. Avatar pe ek baar CLICK karo (AudioContext activate hoga)")
    print("5. June window mein dekho: '[system]> Listening...'")
    print("6. Microphone mein bolo!")
    print("7. Avatar lip-sync karega! 🎭\n")
    
    print("⚠️  IMPORTANT: Avatar pe ek baar click zaroor karo!")
    print("   (Audio play ke liye browser permission chahiye)\n")
    
    input("Press Enter to exit this window...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
