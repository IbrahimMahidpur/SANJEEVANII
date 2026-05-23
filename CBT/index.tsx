import React, { useEffect, useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import FaceDetector from './components/FaceDetector';
import type { FaceEmotionData } from './hooks/useFaceEmotion';

// --- Audio Hook ---

const useAudioAnalyzer = () => {
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = React.useState(false);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const [isPlaying, setIsPlaying] = React.useState(false);

  // NEW: Emotion state from face detection
  const currentEmotionRef = useRef<FaceEmotionData | null>(null);

  useEffect(() => {
    const startAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        const analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);

        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        source.connect(analyser);

        analyserRef.current = analyser;
        dataArrayRef.current = dataArray;
        audioContextRef.current = audioContext;
        sourceRef.current = source;

        // Setup MediaRecorder
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            chunksRef.current.push(e.data);
            console.log('[CBT] Data chunk received:', e.data.size, 'bytes');
          }
        };

        mediaRecorder.onerror = (e) => {
          console.error('[CBT] MediaRecorder error:', e);
          setIsRecording(false);
        };

        mediaRecorder.onstop = async () => {
          console.log('[CBT] MediaRecorder stopped, processing audio...');
          setIsProcessing(true);
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          console.log('[CBT] Audio blob size:', blob.size, 'bytes');
          chunksRef.current = [];

          // Send to Backend
          const formData = new FormData();
          formData.append('file', blob, 'recording.webm');
          formData.append('language', 'en-US');

          // NEW: Add emotion metadata if available
          if (currentEmotionRef.current) {
            formData.append('emotion', JSON.stringify(currentEmotionRef.current));
            console.log('[CBT] Sending emotion data:', currentEmotionRef.current.emotion);
          }

          try {
            console.log('[CBT] Sending audio to backend...');
            const response = await fetch('http://localhost:8002/voice-session', {
              method: 'POST',
              body: formData,
            });

            console.log('[CBT] Backend response status:', response.status);
            if (response.ok) {
              const audioBlob = await response.blob();
              console.log('[CBT] Received audio response, size:', audioBlob.size, 'bytes');
              const audioUrl = URL.createObjectURL(audioBlob);
              const audio = new Audio(audioUrl);

              // Set volume to maximum
              audio.volume = 1.0;
              console.log('[CBT] Audio volume set to:', audio.volume);

              audio.onplay = () => {
                console.log('[CBT] Playing audio response');
                setIsPlaying(true);
              };
              audio.onended = () => {
                console.log('[CBT] Audio playback ended');
                setIsPlaying(false);
              };
              audio.onerror = (e) => {
                console.error('[CBT] Audio playback error:', e);
                setIsPlaying(false);
              };

              audio.play().catch(err => {
                console.error('[CBT] Failed to play audio:', err);
              });
            } else {
              console.error('[CBT] Backend error:', response.statusText);
            }
          } catch (error) {
            console.error('[CBT] API call failed:', error);
          } finally {
            setIsProcessing(false);
          }
        };

      } catch (err) {
        console.error("Error accessing microphone:", err);
      }
    };

    startAudio();

    return () => {
      if (audioContextRef.current) audioContextRef.current.close();
      if (sourceRef.current) sourceRef.current.disconnect();
    };
  }, []);

  const getAverageFrequency = () => {
    if (!analyserRef.current || !dataArrayRef.current) return 0;
    analyserRef.current.getByteFrequencyData(dataArrayRef.current as any);
    let sum = 0;
    for (let i = 0; i < dataArrayRef.current.length; i++) {
      sum += dataArrayRef.current[i];
    }
    return sum / dataArrayRef.current.length;
  };

  const startRecording = () => {
    console.log('[CBT] Attempting to start recording...');
    if (mediaRecorderRef.current) {
      console.log('[CBT] MediaRecorder state:', mediaRecorderRef.current.state);
      if (mediaRecorderRef.current.state === 'inactive') {
        // Start with timeslice to ensure continuous recording
        // Collect data every 1000ms but don't stop automatically
        mediaRecorderRef.current.start(1000);
        setIsRecording(true);
        console.log('[CBT] Recording started with timeslice!');
      } else {
        console.log('[CBT] Cannot start - recorder not inactive');
      }
    } else {
      console.log('[CBT] MediaRecorder not initialized');
    }
  };

  const stopRecording = () => {
    console.log('[CBT] Attempting to stop recording...');
    if (mediaRecorderRef.current) {
      console.log('[CBT] MediaRecorder state:', mediaRecorderRef.current.state);
      if (mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
        console.log('[CBT] Recording stopped!');
      } else {
        console.log('[CBT] Cannot stop - recorder not recording');
      }
    } else {
      console.log('[CBT] MediaRecorder not initialized');
    }
  };

  const toggleRecording = () => {
    console.log('[CBT] Toggle recording clicked. Current state:', isRecording);
    if (isRecording) stopRecording();
    else startRecording();
  };

  return {
    getAverageFrequency,
    isRecording,
    isProcessing,
    isPlaying,
    toggleRecording,
    currentEmotionRef,
  };
};

// --- Shaders ---

const vertexShader = `
  uniform float uTime;
  uniform float uAudio;
  varying float vDistortion;

  // Simplex 3D Noise 
  vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
  vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
  vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
  float snoise(vec3 v) {
    const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
    const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
    vec3 i  = floor(v + dot(v, C.yyy) );
    vec3 x0 = v - i + dot(i, C.xxx) ;
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min( g.xyz, l.zxy );
    vec3 i2 = max( g.xyz, l.zxy );
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    i = mod289(i);
    vec4 p = permute( permute( permute(
              i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
    float n_ = 0.142857142857;
    vec3  ns = n_ * D.wyz - D.xzx;
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_ );
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    vec4 b0 = vec4( x.xy, y.xy );
    vec4 b1 = vec4( x.zw, y.zw );
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
    vec3 p0 = vec3(a0.xy,h.x);
    vec3 p1 = vec3(a0.zw,h.y);
    vec3 p2 = vec3(a1.xy,h.z);
    vec3 p3 = vec3(a1.zw,h.w);
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                  dot(p2,x2), dot(p3,x3) ) );
  }

  void main() {
    float noiseScale = 0.8;
    float noiseSpeed = 0.2; 
    float noiseStrength = 0.35 + uAudio * 0.8;
    
    float noise = snoise(vec3(position.x * noiseScale + uTime * noiseSpeed, position.y * noiseScale, position.z * noiseScale));
    vDistortion = noise;
    
    vec3 newPosition = position + normal * noise * noiseStrength;
    
    float expansion = 1.0 + uAudio * 0.5;
    newPosition *= expansion;

    vec4 mvPosition = modelViewMatrix * vec4(newPosition, 1.0);
    gl_Position = projectionMatrix * mvPosition;
    gl_PointSize = 4.0 * (10.0 / -mvPosition.z); 
  }
`;

const wireframeFragmentShader = `
  uniform vec3 uColor;
  varying float vDistortion;

  void main() {
    gl_FragColor = vec4(uColor, 0.6); 
  }
`;

const pointsFragmentShader = `
  uniform vec3 uColor;
  varying float vDistortion;

  void main() {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    float r = dot(cxy, cxy);
    if (r > 1.0) discard;

    gl_FragColor = vec4(uColor, 1.0); 
  }
`;

// --- Components ---

const WireframeOrb = ({ getAverageFrequency }: any) => {
  const groupRef = useRef<THREE.Group>(null);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uAudio: { value: 0 },
    uColor: { value: new THREE.Color('#88ccff') },
  }), []);

  useFrame((state) => {
    if (!groupRef.current) return;

    const time = state.clock.getElapsedTime();
    const freq = getAverageFrequency();
    const volume = Math.max(0, freq - 20) / 255;

    uniforms.uAudio.value = THREE.MathUtils.lerp(uniforms.uAudio.value, volume, 0.1);
    uniforms.uTime.value = time;

    uniforms.uColor.value.set('#88ccff');

    groupRef.current.rotation.y = time * 0.2;
    groupRef.current.rotation.z = time * 0.05;
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <sphereGeometry args={[2.8, 64, 64]} />
        <shaderMaterial
          wireframe={true}
          uniforms={uniforms}
          vertexShader={vertexShader}
          fragmentShader={wireframeFragmentShader}
          transparent
        />
      </mesh>

      <points>
        <sphereGeometry args={[2.8, 64, 64]} />
        <shaderMaterial
          uniforms={uniforms}
          vertexShader={vertexShader}
          fragmentShader={pointsFragmentShader}
          transparent
          depthWrite={false}
        />
      </points>
    </group>
  );
};

const CBT: React.FC = () => {
  const { getAverageFrequency, isRecording, isProcessing, isPlaying, toggleRecording, currentEmotionRef } = useAudioAnalyzer();
  const [currentEmotion, setCurrentEmotion] = useState<FaceEmotionData | null>(null);

  // Handle emotion changes from face detection
  const handleEmotionChange = (emotion: FaceEmotionData) => {
    setCurrentEmotion(emotion);
    currentEmotionRef.current = emotion;
  };

  return (
    <div className="w-full h-screen bg-black relative overflow-hidden" onClick={toggleRecording}>
      {/* Face Detection Component (runs in background) */}
      <FaceDetector
        enabled={true}
        onEmotionChange={handleEmotionChange}
        showVideo={false}
      />

      <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
        <color attach="background" args={['#000000']} />
        <WireframeOrb
          getAverageFrequency={getAverageFrequency}
          isRecording={isRecording}
          isProcessing={isProcessing}
          isPlaying={isPlaying}
        />
      </Canvas>

      {/* Status indicator */}
      <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 text-white/70 text-sm font-medium">
        {isRecording ? "🎤 Listening..." : isProcessing ? "🧠 Thinking..." : isPlaying ? "🔊 Speaking..." : "👆 Tap to Speak"}
      </div>
    </div>
  );
};

export default CBT;
