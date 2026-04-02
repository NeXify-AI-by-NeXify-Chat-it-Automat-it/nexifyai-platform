import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Sphere, Box, Torus, Icosahedron } from '@react-three/drei';
import * as THREE from 'three';

/* ═══════════ HERO PARTICLES (Neural Network) ═══════════ */
const NODE_COUNT = 60;
const EDGE_COUNT = 80;

function NetworkNodes() {
  const meshRef = useRef();
  const positions = useMemo(() => {
    const pos = new Float32Array(NODE_COUNT * 3);
    for (let i = 0; i < NODE_COUNT; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 6;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 4;
    }
    return pos;
  }, []);

  const sizes = useMemo(() => {
    const s = new Float32Array(NODE_COUNT);
    for (let i = 0; i < NODE_COUNT; i++) s[i] = 0.3 + Math.random() * 0.7;
    return s;
  }, []);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime() * 0.15;
    const posArr = meshRef.current.geometry.attributes.position.array;
    for (let i = 0; i < NODE_COUNT; i++) {
      posArr[i * 3] += Math.sin(t + i * 0.5) * 0.001;
      posArr[i * 3 + 1] += Math.cos(t + i * 0.3) * 0.001;
    }
    meshRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={NODE_COUNT} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-size" count={NODE_COUNT} array={sizes} itemSize={1} />
      </bufferGeometry>
      <pointsMaterial size={0.06} color="#ff9b7a" transparent opacity={0.8} sizeAttenuation />
    </points>
  );
}

function NetworkEdges() {
  const linesRef = useRef();
  const positions = useMemo(() => {
    const pos = [];
    for (let i = 0; i < EDGE_COUNT; i++) {
      const x1 = (Math.random() - 0.5) * 8, y1 = (Math.random() - 0.5) * 6, z1 = (Math.random() - 0.5) * 4;
      const x2 = x1 + (Math.random() - 0.5) * 3, y2 = y1 + (Math.random() - 0.5) * 2, z2 = z1 + (Math.random() - 0.5) * 2;
      pos.push(x1, y1, z1, x2, y2, z2);
    }
    return new Float32Array(pos);
  }, []);

  useFrame(({ clock }) => {
    if (linesRef.current) {
      linesRef.current.rotation.y = clock.getElapsedTime() * 0.02;
      linesRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.01) * 0.05;
    }
  });

  return (
    <lineSegments ref={linesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={EDGE_COUNT * 2} array={positions} itemSize={3} />
      </bufferGeometry>
      <lineBasicMaterial color="#ff9b7a" transparent opacity={0.08} />
    </lineSegments>
  );
}

function FloatingCore() {
  const ref = useRef();
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.x = clock.getElapsedTime() * 0.1;
      ref.current.rotation.y = clock.getElapsedTime() * 0.15;
    }
  });
  return (
    <group ref={ref}>
      <Icosahedron args={[1.2, 1]}>
        <meshBasicMaterial color="#ff9b7a" wireframe transparent opacity={0.15} />
      </Icosahedron>
      <Icosahedron args={[0.8, 0]}>
        <MeshDistortMaterial color="#ff9b7a" transparent opacity={0.06} distort={0.3} speed={2} />
      </Icosahedron>
    </group>
  );
}

function DataStreams() {
  const ref = useRef();
  const count = 200;
  const positions = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 8;
      const radius = 2 + Math.random() * 3;
      p[i * 3] = Math.cos(angle) * radius;
      p[i * 3 + 1] = (Math.random() - 0.5) * 6;
      p[i * 3 + 2] = Math.sin(angle) * radius;
    }
    return p;
  }, []);

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.y = clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.02} color="#ffb59e" transparent opacity={0.4} sizeAttenuation />
    </points>
  );
}

export function HeroScene() {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 60 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[5, 5, 5]} intensity={0.5} color="#ff9b7a" />
        <Suspense fallback={null}>
          <FloatingCore />
          <NetworkNodes />
          <NetworkEdges />
          <DataStreams />
          <Float speed={0.5} rotationIntensity={0.2} floatIntensity={0.3}>
            <Sphere args={[0.15, 16, 16]} position={[3, 2, -1]}>
              <meshStandardMaterial color="#ff9b7a" emissive="#ff9b7a" emissiveIntensity={0.5} transparent opacity={0.6} />
            </Sphere>
          </Float>
          <Float speed={0.8} rotationIntensity={0.3} floatIntensity={0.4}>
            <Box args={[0.2, 0.2, 0.2]} position={[-3, -1.5, 0.5]} rotation={[0.5, 0.5, 0]}>
              <meshStandardMaterial color="#ff9b7a" emissive="#ff9b7a" emissiveIntensity={0.3} transparent opacity={0.4} wireframe />
            </Box>
          </Float>
          <Float speed={0.6} rotationIntensity={0.15} floatIntensity={0.2}>
            <Torus args={[0.3, 0.08, 8, 20]} position={[3.5, -2, -0.5]} rotation={[1, 0.5, 0]}>
              <meshStandardMaterial color="#ff9b7a" emissive="#ff9b7a" emissiveIntensity={0.3} transparent opacity={0.3} />
            </Torus>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}

/* ═══════════ INTEGRATIONS GLOBE ═══════════ */
function GlobeWireframe() {
  const ref = useRef();
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.y = clock.getElapsedTime() * 0.08;
      ref.current.rotation.x = 0.2;
    }
  });
  return (
    <group ref={ref}>
      <Sphere args={[2, 24, 24]}>
        <meshBasicMaterial color="#ff9b7a" wireframe transparent opacity={0.08} />
      </Sphere>
      <Sphere args={[2.05, 16, 16]}>
        <meshBasicMaterial color="#ff9b7a" wireframe transparent opacity={0.04} />
      </Sphere>
    </group>
  );
}

function GlobeNodes() {
  const ref = useRef();
  const count = 40;
  const positions = useMemo(() => {
    const p = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const phi = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;
      const r = 2.02;
      p[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      p[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      p[i * 3 + 2] = r * Math.cos(phi);
    }
    return p;
  }, []);

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.y = clock.getElapsedTime() * 0.08;
      ref.current.rotation.x = 0.2;
    }
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.08} color="#ff9b7a" transparent opacity={0.9} sizeAttenuation />
    </points>
  );
}

function ConnectionArcs() {
  const ref = useRef();
  const arcs = useMemo(() => {
    const lines = [];
    for (let i = 0; i < 12; i++) {
      const phi1 = Math.acos(2 * Math.random() - 1);
      const theta1 = Math.random() * Math.PI * 2;
      const phi2 = Math.acos(2 * Math.random() - 1);
      const theta2 = Math.random() * Math.PI * 2;
      const r = 2.02;
      for (let t = 0; t <= 10; t++) {
        const f = t / 10;
        const p = 1 + 0.3 * Math.sin(f * Math.PI);
        const ph = phi1 + (phi2 - phi1) * f;
        const th = theta1 + (theta2 - theta1) * f;
        lines.push(p * r * Math.sin(ph) * Math.cos(th), p * r * Math.sin(ph) * Math.sin(th), p * r * Math.cos(ph));
      }
    }
    return new Float32Array(lines);
  }, []);

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.y = clock.getElapsedTime() * 0.08;
      ref.current.rotation.x = 0.2;
    }
  });

  return (
    <line ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={arcs.length / 3} array={arcs} itemSize={3} />
      </bufferGeometry>
      <lineBasicMaterial color="#ff9b7a" transparent opacity={0.15} />
    </line>
  );
}

export function IntegrationsGlobe() {
  return (
    <div style={{ width: '100%', height: '400px', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.2} />
        <pointLight position={[5, 3, 5]} intensity={0.3} color="#ff9b7a" />
        <Suspense fallback={null}>
          <GlobeWireframe />
          <GlobeNodes />
          <ConnectionArcs />
        </Suspense>
      </Canvas>
    </div>
  );
}

/* ═══════════ PROCESS PIPELINE 3D ═══════════ */
function PipelineNode({ position, active, label }) {
  const ref = useRef();
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.scale.setScalar(1 + Math.sin(clock.getElapsedTime() * 2 + position[0]) * 0.05);
    }
  });
  return (
    <group position={position}>
      <Icosahedron ref={ref} args={[0.3, 0]}>
        <meshStandardMaterial
          color={active ? '#ff9b7a' : '#364050'}
          emissive={active ? '#ff9b7a' : '#000'}
          emissiveIntensity={active ? 0.4 : 0}
          transparent
          opacity={active ? 0.9 : 0.5}
        />
      </Icosahedron>
    </group>
  );
}

function PipelineConnector({ from, to }) {
  const points = useMemo(() => {
    return [new THREE.Vector3(...from), new THREE.Vector3(...to)];
  }, [from, to]);
  const geo = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);
  return (
    <line geometry={geo}>
      <lineBasicMaterial color="#ff9b7a" transparent opacity={0.2} />
    </line>
  );
}

export function ProcessScene() {
  const nodes = [[-3, 0, 0], [-1, 0, 0], [1, 0, 0], [3, 0, 0]];
  return (
    <div style={{ width: '100%', height: '200px' }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[0, 3, 3]} intensity={0.5} color="#ff9b7a" />
        <Suspense fallback={null}>
          {nodes.map((pos, i) => (
            <Float key={i} speed={1 + i * 0.3} floatIntensity={0.15}>
              <PipelineNode position={pos} active={true} />
            </Float>
          ))}
          {nodes.slice(0, -1).map((from, i) => (
            <PipelineConnector key={i} from={from} to={nodes[i + 1]} />
          ))}
        </Suspense>
      </Canvas>
    </div>
  );
}

/* ═══════════ FLOATING ACCENT SHAPES (reusable) ═══════════ */
export function AccentShapes() {
  return (
    <div style={{ position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      <Canvas camera={{ position: [0, 0, 5], fov: 60 }} dpr={[1, 1]} gl={{ antialias: false, alpha: true }}>
        <Suspense fallback={null}>
          <Float speed={0.4} rotationIntensity={0.5} floatIntensity={0.6}>
            <Torus args={[1, 0.05, 8, 30]} position={[4, 2, -2]} rotation={[1, 0, 0.5]}>
              <meshBasicMaterial color="#ff9b7a" transparent opacity={0.08} />
            </Torus>
          </Float>
          <Float speed={0.3} rotationIntensity={0.3} floatIntensity={0.4}>
            <Box args={[0.5, 0.5, 0.5]} position={[-4, -1, -1]} rotation={[0.7, 0.3, 0]}>
              <meshBasicMaterial color="#ff9b7a" transparent opacity={0.06} wireframe />
            </Box>
          </Float>
        </Suspense>
      </Canvas>
    </div>
  );
}
