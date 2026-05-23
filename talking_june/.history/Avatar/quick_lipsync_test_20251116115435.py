import asyncio
import websockets
import json

async def test_lipsync():
    async with websockets.connect("ws://localhost:8765") as ws:
        # Use a known existing file from shared_audio
        audio_path = "tmpxmy0251_.wav"
        msg = {
            "type": "tts_done",
            "audioUrl": f"http://localhost:8001/{audio_path}"
        }
        await ws.send(json.dumps(msg))
        print(f"Test message sent! -> {msg['audioUrl']}")

if __name__ == "__main__":
    asyncio.run(test_lipsync())
