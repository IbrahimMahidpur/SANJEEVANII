import { useEffect, useRef, useState } from 'react';

export default function Sanjeevani() {
  const wsRef = useRef<WebSocket | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket bridge for real-time communication
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket('ws://localhost:8765');

        ws.onopen = () => {
          console.log('[Sanjeevani] ✅ Connected to bridge server');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('[Sanjeevani] 📨 Received:', data);

          // Forward messages to iframe
          if (iframeRef.current && iframeRef.current.contentWindow) {
            iframeRef.current.contentWindow.postMessage(data, '*');
          }
        };

        ws.onerror = (error) => {
          console.error('[Sanjeevani] ❌ WebSocket error:', error);
          setIsConnected(false);
        };

        ws.onclose = () => {
          console.log('[Sanjeevani] 🔌 Disconnected, retrying...');
          setIsConnected(false);
          setIsSessionActive(false); // Reset session state on disconnect
          // Auto-retry connection after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('[Sanjeevani] Failed to connect:', error);
        setIsConnected(false);
        // Retry on error
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        // 🔴 Tell June VA to stop listening
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'STOP_LISTENING' }));
        }
        wsRef.current.close();
      }
    };
  }, []);

  const toggleSession = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('[Sanjeevani] WebSocket not connected');
      return;
    }

    if (isSessionActive) {
      // Stop session
      wsRef.current.send(JSON.stringify({ type: 'STOP_LISTENING' }));
      // Clear history on stop so next session is fresh
      wsRef.current.send(JSON.stringify({ type: 'CLEAR_HISTORY' }));
      setIsSessionActive(false);
    } else {
      // Start session
      wsRef.current.send(JSON.stringify({ type: 'START_LISTENING' }));
      setIsSessionActive(true);
    }
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* TalkingHead Avatar - Top Portion Only (Upper Body) */}
      <div className="relative w-full h-screen overflow-hidden">
        <iframe
          ref={iframeRef}
          src="http://localhost:8080"
          className="w-full border-0"
          style={{
            height: '200vh', // Make iframe taller
            transform: 'translateY(-30%)', // Shift up to show upper portion
          }}
          title="Sanjeevani Avatar"
          allow="microphone; camera"
        />
      </div>

      {/* Control Overlay */}
      <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 z-50">
        {!isSessionActive ? (
          <button
            onClick={toggleSession}
            disabled={!isConnected}
            className={`px-8 py-4 rounded-full text-xl font-semibold shadow-lg transition-all duration-300 transform hover:scale-105 ${isConnected
              ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-blue-500/50'
              : 'bg-gray-600 text-gray-300 cursor-not-allowed'
              }`}
          >
            {isConnected ? '✨ Start Conversation' : 'Connecting...'}
          </button>
        ) : (
          <button
            onClick={toggleSession}
            className="px-6 py-3 rounded-full bg-red-500/80 text-white font-medium backdrop-blur-sm hover:bg-red-600 transition-all shadow-lg hover:shadow-red-500/30 flex items-center gap-2"
          >
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
            </span>
            End Session
          </button>
        )}
      </div>
    </div>
  );
}
