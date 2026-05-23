// CBT/components/FaceDetector.tsx
/**
 * Face Detector Component
 * Displays webcam feed and visual feedback for face detection
 */

import React, { useEffect } from 'react';
import { useFaceEmotion } from '../hooks/useFaceEmotion';

interface FaceDetectorProps {
  enabled?: boolean;
  onEmotionChange?: (emotion: any) => void;
  showVideo?: boolean; // Show webcam feed (for debugging)
}

export const FaceDetector: React.FC<FaceDetectorProps> = ({
  enabled = true,
  onEmotionChange,
  showVideo = false
}) => {
  const {
    isActive,
    isLoading,
    error,
    currentEmotion,
    faceDetected,
    avoidanceDetected,
    videoRef,
    startDetection,
    stopDetection
  } = useFaceEmotion({
    enabled,
    fps: 10,
    avoidanceThreshold: 3000
  });

  // Start detection when component mounts
  useEffect(() => {
    if (enabled) {
      startDetection();
    }

    return () => {
      stopDetection();
    };
  }, [enabled]);

  // Notify parent of emotion changes
  useEffect(() => {
    if (currentEmotion && onEmotionChange) {
      onEmotionChange(currentEmotion);
    }
  }, [currentEmotion, onEmotionChange]);

  return (
    <div className="face-detector">
      {/* Hidden video element for face detection */}
      <video
        ref={videoRef}
        style={{
          position: showVideo ? 'fixed' : 'absolute',
          top: showVideo ? '10px' : '-9999px',
          right: showVideo ? '10px' : '-9999px',
          width: showVideo ? '200px' : '1px',
          height: showVideo ? '150px' : '1px',
          borderRadius: showVideo ? '8px' : '0',
          border: showVideo ? '2px solid #4a9eff' : 'none',
          zIndex: showVideo ? 1000 : -1,
          opacity: showVideo ? 1 : 0,
          transform: 'scaleX(-1)' // Mirror for natural view
        }}
        playsInline
        muted
      />

      {/* Status indicator (optional) */}
      {showVideo && (
        <div
          style={{
            position: 'fixed',
            top: '170px',
            right: '10px',
            padding: '8px 12px',
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            borderRadius: '6px',
            fontSize: '12px',
            zIndex: 1000
          }}
        >
          {isLoading && '⏳ Loading...'}
          {error && `❌ ${error}`}
          {isActive && !error && (
            <div>
              <div>
                {faceDetected ? '✅ Face detected' : '⚠️ No face'}
              </div>
              {currentEmotion && (
                <div>
                  Emotion: {currentEmotion.emotion} (
                  {(currentEmotion.confidence * 100).toFixed(0)}%)
                </div>
              )}
              {avoidanceDetected && (
                <div style={{ color: '#ff6b6b' }}>
                  ⚠️ Avoidance detected
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FaceDetector;
