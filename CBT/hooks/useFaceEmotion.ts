// CBT/hooks/useFaceEmotion.ts
/**
 * Custom React Hook for Face Detection + Emotion Recognition
 * Uses face-api.js for both detection and emotion classification
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { getEmotionClassifier, EmotionResult, EmotionType } from '../utils/emotionClassifier';


export interface FaceEmotionData {
  emotion: EmotionType;
  confidence: number;
  face_detected: boolean;
  crying_score: number;
  avoidance_detected: boolean;
  timestamp: number;
}

export interface UseFaceEmotionOptions {
  enabled?: boolean;
  fps?: number; // Frames per second for detection
  avoidanceThreshold?: number; // Seconds before avoidance detected
}

export interface UseFaceEmotionReturn {
  isActive: boolean;
  isLoading: boolean;
  error: string | null;
  currentEmotion: FaceEmotionData | null;
  faceDetected: boolean;
  avoidanceDetected: boolean;
  videoRef: React.RefObject<HTMLVideoElement>;
  startDetection: () => Promise<void>;
  stopDetection: () => void;
}

export const useFaceEmotion = (
  options: UseFaceEmotionOptions = {}
): UseFaceEmotionReturn => {
  const {
    enabled = true,
    fps = 10,
    avoidanceThreshold = 3000 // 3 seconds
  } = options;

  // State
  const [isActive, setIsActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentEmotion, setCurrentEmotion] = useState<FaceEmotionData | null>(null);
  const [faceDetected, setFaceDetected] = useState(false);
  const [avoidanceDetected, setAvoidanceDetected] = useState(false);

  // Refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastFaceTimeRef = useRef<number>(Date.now());
  const detectionIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Models (only face-api.js)
  const emotionClassifier = getEmotionClassifier();


  /**
   * Initialize webcam and models
   */
  const startDetection = useCallback(async () => {
    if (!enabled || isActive) return;

    setIsLoading(true);
    setError(null);

    try {
      // Load face-api.js models (includes face detection + emotion)
      console.log('Loading face detection models...');
      await emotionClassifier.loadModel();


      // Get webcam stream
      console.log('Requesting webcam access...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });

      streamRef.current = stream;

      // Attach stream to video element
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setIsActive(true);
      lastFaceTimeRef.current = Date.now();

      console.log('✓ Face detection started');
    } catch (err: any) {
      const errorMessage = err.name === 'NotAllowedError'
        ? 'Camera permission denied'
        : err.name === 'NotFoundError'
          ? 'No camera found'
          : 'Failed to start face detection';

      setError(errorMessage);
      console.error('Face detection error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [enabled, isActive, emotionClassifier]);

  /**
   * Stop detection and cleanup
   */
  const stopDetection = useCallback(() => {
    // Stop animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    // Stop interval
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }

    // Stop webcam stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Clear video
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsActive(false);
    setFaceDetected(false);
    setAvoidanceDetected(false);
    setCurrentEmotion(null);

    console.log('Face detection stopped');
  }, []);

  /**
   * Detection loop
   */
  useEffect(() => {
    if (!isActive || !videoRef.current) return;

    const detectLoop = async () => {
      if (!videoRef.current || !emotionClassifier.isReady()) {
        return;
      }

      try {
        // Use face-api.js for detection + emotion (single call)
        const emotionResult: EmotionResult | null = await emotionClassifier.classifyEmotion(
          videoRef.current
        );

        const now = Date.now();
        const isFaceDetected = emotionResult !== null && emotionResult.confidence > 0;

        setFaceDetected(isFaceDetected);

        // Update last face time
        if (isFaceDetected) {
          lastFaceTimeRef.current = now;
        }

        // Check for avoidance
        const timeSinceLastFace = now - lastFaceTimeRef.current;
        const isAvoidance = timeSinceLastFace > avoidanceThreshold;
        setAvoidanceDetected(isAvoidance);

        // Update current emotion data
        const emotionData: FaceEmotionData = {
          emotion: emotionResult?.emotion || 'neutral',
          confidence: emotionResult?.confidence || 0,
          face_detected: isFaceDetected,
          crying_score: emotionResult?.crying_likelihood || 0,
          avoidance_detected: isAvoidance,
          timestamp: now
        };

        setCurrentEmotion(emotionData);

      } catch (err) {
        console.error('Detection loop error:', err);
      }
    };

    // Run detection at specified FPS
    const interval = 1000 / fps;
    detectionIntervalRef.current = setInterval(detectLoop, interval);

    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, [isActive, fps, avoidanceThreshold, emotionClassifier]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      stopDetection();
    };
  }, [stopDetection]);

  return {
    isActive,
    isLoading,
    error,
    currentEmotion,
    faceDetected,
    avoidanceDetected,
    videoRef,
    startDetection,
    stopDetection
  };
};

export default useFaceEmotion;
