"""
WebSocket Bridge Server for June VA + TalkingHead Integration

This server provides:
1. HTTP server (port 8001) - Serves audio files from shared_audio directory
2. WebSocket server (port 8765) - Real-time communication between June and TalkingHead

Usage:
    python bridge_server.py
"""

import asyncio
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

import websockets

# Configuration
AUDIO_DIR = Path(__file__).parent / "shared_audio"
HOST = "localhost"
WS_PORT = 8765
HTTP_PORT = 8001

# Store connected clients
connected_clients = set()


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS support for cross-origin requests."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


def run_http_server():
    """Run HTTP server to serve audio files."""
    # Ensure audio directory exists
    AUDIO_DIR.mkdir(exist_ok=True)
    
    # Change to audio directory
    os.chdir(AUDIO_DIR)
    
    httpd = HTTPServer((HOST, HTTP_PORT), CORSHTTPRequestHandler)
    print(f"[HTTP] 🎵 Serving audio files on http://{HOST}:{HTTP_PORT}/")
    print(f"[HTTP] 📁 Audio directory: {AUDIO_DIR}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[HTTP] Shutting down HTTP server...")
        httpd.shutdown()


async def handle_client(websocket):
    """Handle individual WebSocket client connections."""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    connected_clients.add(websocket)
    print(f"[WS] ✅ Client connected: {client_id} (Total: {len(connected_clients)})")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"[WS] 📨 Received from {client_id}: {data}")

            # Broadcast received message to all other connected clients
            # so TalkingHead (browser) clients get notified when June sends TTS.
            if connected_clients:
                message_json = json.dumps(data)
                disconnected = set()
                for client in connected_clients:
                    # don't send back to the sender
                    if client is websocket:
                        continue
                    try:
                        await client.send(message_json)
                        print(f"[WS] ✉️ Forwarded to client: {data}")
                    except websockets.ConnectionClosed:
                        disconnected.add(client)
                for client in disconnected:
                    connected_clients.discard(client)
    except websockets.ConnectionClosed:
        print(f"[WS] ❌ Client disconnected: {client_id}")
    except Exception as e:
        print(f"[WS] ⚠️ Error with client {client_id}: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"[WS] 👋 Client removed: {client_id} (Total: {len(connected_clients)})")


async def broadcast_to_clients(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    if not connected_clients:
        print("[WS] ⚠️ No clients connected to broadcast to")
        return
    
    message_json = json.dumps(message)
    disconnected = set()
    
    for client in connected_clients:
        try:
            await client.send(message_json)
            print(f"[WS] ✉️ Sent to client: {message}")
        except websockets.ConnectionClosed:
            disconnected.add(client)
    
    # Clean up disconnected clients
    for client in disconnected:
        connected_clients.discard(client)


async def ws_main():
    """Run WebSocket server."""
    async with websockets.serve(handle_client, HOST, WS_PORT):
        print(f"[WS] 🔌 WebSocket server running on ws://{HOST}:{WS_PORT}")
        print("[WS] 👂 Waiting for TalkingHead to connect...")
        await asyncio.Future()  # Run forever


def main():
    """Start both HTTP and WebSocket servers."""
    print("=" * 60)
    print("🌉 June VA ↔ TalkingHead Bridge Server")
    print("=" * 60)
    
    # Start HTTP server in a daemon thread
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Give HTTP server time to start
    import time
    time.sleep(0.5)
    
    print("\n✅ Bridge server ready!")
    print("\n" + "=" * 60)
    print("🎭 IMPORTANT: ACTIVATE AUDIO IN BROWSER!")
    print("=" * 60)
    print("1. Open: http://localhost:8080")
    print("2. 🔵 CLICK THE BLUE BUTTON to activate audio!")
    print("3. Run: python -m june_va")
    print("4. Start talking!\n")
    print("⚠️  Audio will NOT play until you click the blue button!")
    print("=" * 60 + "\n")
    
    # Start WebSocket server (blocking)
    try:
        asyncio.run(ws_main())
    except KeyboardInterrupt:
        print("\n\n[Bridge] 👋 Shutting down...")


if __name__ == "__main__":
    main()
