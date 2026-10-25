import { useEffect, useRef } from "react";
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  Group,
  IcosahedronGeometry,
  Mesh,
  MeshBasicMaterial,
  PerspectiveCamera,
  Points,
  PointsMaterial,
  Scene,
  ShaderMaterial,
  SphereGeometry,
  TorusGeometry,
  WebGLRenderer,
} from "three";

/** Text-free, high-DPI hero visual. Rendering is capped for mobile thermals. */
export function OrbScene() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    let renderer: WebGLRenderer;
    try {
      renderer = new WebGLRenderer({ alpha: true, antialias: true, powerPreference: "low-power" });
    } catch {
      mount.classList.add("orb-scene--fallback");
      return;
    }

    const scene = new Scene();
    const camera = new PerspectiveCamera(34, 1, 0.1, 30);
    camera.position.set(0, 0, 5.3);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.domElement.setAttribute("aria-hidden", "true");
    renderer.domElement.setAttribute("role", "presentation");
    mount.appendChild(renderer.domElement);

    const core = new Group();
    scene.add(core);

    const plasma = new ShaderMaterial({
      transparent: true,
      depthWrite: false,
      uniforms: { uTime: { value: 0 } },
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        varying vec3 vPosition;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          vec4 viewPosition = modelViewMatrix * vec4(position, 1.0);
          vViewPosition = -viewPosition.xyz;
          vPosition = position;
          gl_Position = projectionMatrix * viewPosition;
        }
      `,
      fragmentShader: `
        uniform float uTime;
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        varying vec3 vPosition;
        void main() {
          vec3 normal = normalize(vNormal);
          vec3 viewDirection = normalize(vViewPosition);
          float rim = pow(1.0 - max(dot(normal, viewDirection), 0.0), 2.4);
          float pulse = 0.5 + 0.5 * sin(vPosition.y * 5.0 + uTime * 1.3 + vPosition.x * 3.0);
          vec3 violet = vec3(0.25, 0.14, 0.92);
          vec3 rose = vec3(0.92, 0.20, 0.62);
          vec3 ice = vec3(0.18, 0.82, 1.0);
          vec3 color = mix(violet, rose, pulse * 0.65);
          color = mix(color, ice, rim * 0.72);
          gl_FragColor = vec4(color, 0.12 + rim * 0.72);
        }
      `,
    });
    const coreMesh = new Mesh(new SphereGeometry(1.02, 56, 40), plasma);
    core.add(coreMesh);

    const wireMaterial = new MeshBasicMaterial({
      color: 0x99d9ff,
      wireframe: true,
      transparent: true,
      opacity: 0.14,
      blending: AdditiveBlending,
    });
    const wire = new Mesh(new IcosahedronGeometry(1.22, 2), wireMaterial);
    core.add(wire);

    const ringMaterial = new MeshBasicMaterial({
      color: 0xc16cff,
      transparent: true,
      opacity: 0.48,
      blending: AdditiveBlending,
    });
    const rings = [0, 1].map((index) => {
      const ring = new Mesh(new TorusGeometry(index ? 1.52 : 1.42, 0.007, 6, 144), ringMaterial);
      ring.rotation.set(index ? 1.15 : 0.45, index ? -0.5 : 0.35, index ? 0.25 : -0.55);
      ring.scale.set(index ? 0.88 : 1, index ? 1.03 : 1, 1);
      core.add(ring);
      return ring;
    });

    const pointPositions = new Float32Array(180 * 3);
    for (let i = 0; i < 180; i += 1) {
      const angle = i * 2.399963;
      const radius = 1.6 + ((i * 37) % 100) / 100 * 1.35;
      pointPositions[i * 3] = Math.cos(angle) * radius;
      pointPositions[i * 3 + 1] = Math.sin(angle * 0.83) * radius * 0.7;
      pointPositions[i * 3 + 2] = Math.sin(angle) * radius * 0.48;
    }
    const pointGeometry = new BufferGeometry();
    pointGeometry.setAttribute("position", new BufferAttribute(pointPositions, 3));
    const points = new Points(pointGeometry, new PointsMaterial({
      color: 0xb9a4ff,
      size: 0.018,
      transparent: true,
      opacity: 0.66,
      sizeAttenuation: true,
    }));
    scene.add(points);

    const resize = () => {
      const { width, height } = mount.getBoundingClientRect();
      if (!width || !height) return;
      camera.aspect = width / height;
      camera.position.z = width < 520 ? 5.8 : 5.3;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height, false);
      renderer.render(scene, camera);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    const animate = (time: number) => {
      plasma.uniforms.uTime.value = time * 0.00035;
      core.rotation.y = time * 0.00009;
      core.rotation.x = Math.sin(time * 0.00018) * 0.08;
      core.position.y = Math.sin(time * 0.00055) * 0.045;
      rings[0].rotation.z = -0.55 + time * 0.00006;
      rings[1].rotation.z = 0.25 - time * 0.000045;
      points.rotation.y = -time * 0.000025;
      renderer.render(scene, camera);
      if (!reducedMotion) frame = window.requestAnimationFrame(animate);
    };
    animate(0);

    return () => {
      window.cancelAnimationFrame(frame);
      observer.disconnect();
      scene.traverse((object) => {
        if (object instanceof Mesh || object instanceof Points) {
          object.geometry.dispose();
          const material = object.material;
          (Array.isArray(material) ? material : [material]).forEach((item) => item.dispose());
        }
      });
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, []);

  return <div className="orb-scene" ref={mountRef} aria-hidden="true" />;
}
