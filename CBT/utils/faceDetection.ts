// CBT/utils/faceDetection.ts
/**
 * Face Detection Utility using TensorFlow.js BlazeFace
 * Lightweight, fast face detection for real-time use
 */

import * as blazeface from '@tensorflow-models/blazeface';
import '@tensorflow/tfjs-backend-webgl';
import * as tf from '@tensorflow/tfjs-core';

export interface FaceDetectionResult {
  face_detected: boolean;
  box: { x: number; y: number; width: number; height: number } | null;
  confidence: number;
  landmarks?: Array<{ x: number; y: number }>;
}

class FaceDetector {
  private model: blazeface.BlazeFaceModel | null = null;
  private isLoading: boolean = false;
  private isLoaded: boolean = false;

  /**
   * Load the BlazeFace model
   */
  async loadModel(): Promise<void> {
    if (this.isLoaded || this.isLoading) return;

    this.isLoading = true;
    try {
      console.log('Loading BlazeFace model...');

      // Set backend to WebGL for performance
      await tf.setBackend('webgl');
      await tf.ready();

      // Load BlazeFace model
      this.model = await blazeface.load();
      this.isLoaded = true;
      console.log('✓ BlazeFace model loaded successfully');
    } catch (error) {
      console.error('Failed to load BlazeFace model:', error);
      throw error;
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Detect face in video element
   */
  async detectFace(
    videoElement: HTMLVideoElement
  ): Promise<FaceDetectionResult> {
    if (!this.model) {
      throw new Error('Model not loaded. Call loadModel() first.');
    }

    if (!videoElement || videoElement.readyState < 2) {
      return {
        face_detected: false,
        box: null,
        confidence: 0
      };
    }

    try {
      // Detect faces
      const predictions = await this.model.estimateFaces(videoElement, false);

      if (predictions.length === 0) {
        return {
          face_detected: false,
          box: null,
          confidence: 0
        };
      }

      // Get first (primary) face
      const face = predictions[0];

      // Extract bounding box
      const topLeft = face.topLeft as [number, number];
      const bottomRight = face.bottomRight as [number, number];

      const box = {
        x: topLeft[0],
        y: topLeft[1],
        width: bottomRight[0] - topLeft[0],
        height: bottomRight[1] - topLeft[1]
      };

      // Get landmarks if available
      const landmarks = face.landmarks?.map((point: any) => ({
        x: point[0],
        y: point[1]
      }));

      return {
        face_detected: true,
        box,
        confidence: face.probability ? face.probability[0] : 0.9,
        landmarks
      };
    } catch (error) {
      console.error('Face detection error:', error);
      return {
        face_detected: false,
        box: null,
        confidence: 0
      };
    }
  }

  /**
   * Check if model is ready
   */
  isReady(): boolean {
    return this.isLoaded && this.model !== null;
  }

  /**
   * Dispose model and free memory
   */
  dispose(): void {
    if (this.model) {
      this.model = null;
      this.isLoaded = false;
      console.log('BlazeFace model disposed');
    }
  }
}

// Singleton instance
let faceDetectorInstance: FaceDetector | null = null;

export const getFaceDetector = (): FaceDetector => {
  if (!faceDetectorInstance) {
    faceDetectorInstance = new FaceDetector();
  }
  return faceDetectorInstance;
};

export default getFaceDetector;
