import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Tree, TreePreset } from '../index.js';
import { Environment } from './environment.js';

// Default camera for front-facing slightly-upward view
// Positioned far enough back to see the full tree canopy with skills visible
const DEFAULT_CAMERA_POS = new THREE.Vector3(0, 32, 145);
const DEFAULT_TARGET = new THREE.Vector3(0, 38, 0);

// Create a 3D starfield shell around the scene so stars rotate with the camera,
// producing an immersive starry-night sky. Colors mix pure white + cool blue + warm pale yellow
// to mimic real stellar color temperature variation.
function createStarfield() {
  const STAR_COUNT = 1200;
  const MIN_RADIUS = 650;
  const MAX_RADIUS = 1400;

  const positions = new Float32Array(STAR_COUNT * 3);
  const colors = new Float32Array(STAR_COUNT * 3);
  const sizes = new Float32Array(STAR_COUNT);

  const _tmp = new THREE.Color();
  const STAR_PALETTE = [
    new THREE.Color(0xffffff),   // 60% — pure cool-white stars (class A/F)
    new THREE.Color(0xcfe4ff),   // 25% — pale ice-blue stars (class B/O-ish tint)
    new THREE.Color(0xfff4dc),   // 12% — warm yellow-white (class G/K sun-like)
    new THREE.Color(0xffd8b0)    // 3%  — faint orange tint (class M red dwarf, dim)
  ];
  const PALETTE_WEIGHTS = [0.60, 0.25, 0.12, 0.03];

  function pickPaletteIndex() {
    const r = Math.random();
    let acc = 0;
    for (let i = 0; i < PALETTE_WEIGHTS.length; i++) {
      acc += PALETTE_WEIGHTS[i];
      if (r <= acc) return i;
    }
    return 0;
  }

  for (let i = 0; i < STAR_COUNT; i++) {
    // Spherical distribution, bias Y upward since camera never sees below ground.
    // 85% of stars in the upper hemisphere (y >= 0), 15% below for continuity.
    const u = Math.random();
    const v = (Math.random() - 0.5) * (Math.random() < 0.85 ? 1.0 : 0.5);
    const theta = 2 * Math.PI * u;
    const phi = Math.acos(2 * v * (Math.random() < 0.85 ? 1 : -1));
    const radius = MIN_RADIUS + Math.random() * (MAX_RADIUS - MIN_RADIUS);

    const sinPhi = Math.sin(phi);
    const x = radius * sinPhi * Math.cos(theta);
    const y = radius * Math.cos(phi);
    const z = radius * sinPhi * Math.sin(theta);

    positions[i * 3 + 0] = x;
    positions[i * 3 + 1] = Math.abs(y) * 0.6 + 40; // keep most stars above tree canopy
    positions[i * 3 + 2] = z;

    // Star color from weighted palette
    const paletteIdx = pickPaletteIndex();
    _tmp.copy(STAR_PALETTE[paletteIdx]);
    // subtle per-star brightness jitter so stars don't look uniform
    const jitter = 0.7 + Math.random() * 0.3;
    _tmp.multiplyScalar(jitter);
    colors[i * 3 + 0] = _tmp.r;
    colors[i * 3 + 1] = _tmp.g;
    colors[i * 3 + 2] = _tmp.b;

    // Size: a few bright big stars, many tiny ones
    const rSize = Math.random();
    if (rSize > 0.985) sizes[i] = 2.4 + Math.random() * 1.4;       // 1.5% very bright
    else if (rSize > 0.90) sizes[i] = 1.5 + Math.random() * 0.9;   // 10% medium-bright
    else sizes[i] = 0.5 + Math.random() * 0.9;                     // rest small pinpoints
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  geometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1));

  const material = new THREE.PointsMaterial({
    size: 1.2,
    vertexColors: true,
    transparent: true,
    opacity: 0.95,
    depthWrite: false,              // stars render behind tree properly
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
  });

  const stars = new THREE.Points(geometry, material);
  stars.name = 'Starfield';
  stars.frustumCulled = false;     // always visible around camera
  return stars;
}

export async function createScene(container, renderer) {
  const w = container.clientWidth;
  const h = container.clientHeight;

  renderer.setClearColor(0x000000, 0);
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.28;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  // Fixed elegant deep-blue background (stable, never renders black or bright band)
  scene.background = new THREE.Color(0x0d2a5c);
  // Soft blue twilight fog — light enough not to crush tree to black,
  // but still cohesive with the deep-blue page background
  scene.fog = new THREE.FogExp2(0x0d2a5c, 0.0011);

  const environment = new Environment();
  scene.add(environment);

  // 3D starry-sky backdrop (immersive, rotates with camera)
  const stars = createStarfield();
  scene.add(stars);

  const camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 2000);
  camera.position.copy(DEFAULT_CAMERA_POS);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  // Restrict polar angle: prevent going under the tree (min) or too far overhead (max)
  // 0 = straight down, PI/2 = horizontal, >PI/2 = looking up
  controls.minPolarAngle = Math.PI * 0.20;  // ~36° from above — allows reasonable overhead view
  controls.maxPolarAngle = Math.PI * 0.52;  // ~94° — slightly past horizontal, prevents going under tree
  controls.minDistance = 70;
  controls.maxDistance = 280;
  controls.target.copy(DEFAULT_TARGET);
  controls.update();

  const tree = new Tree();
  tree.loadPreset('Oak Large');
  tree.options.seed = 29919;
  // Blue-green leaves — brighter than pure green, cohesive with tech-blue theme
  tree.options.leaves.tint = 0x9fe0f8;
  tree.options.leaves.textured = true;
  tree.options.leaves.type = 'oak';
  tree.options.leaves.alphaTest = 0.5;
  tree.generate();
  tree.castShadow = true;
  tree.receiveShadow = true;
  scene.add(tree);

  // Reduced background forest for performance
  const forest = new THREE.Group();
  forest.name = 'Forest';

  const treeCount = 20;
  const minDistance = 180;
  const maxDistance = 450;

  function createBackgroundTree() {
    const r = minDistance + Math.random() * maxDistance;
    const theta = 2 * Math.PI * Math.random();
    const presets = Object.keys(TreePreset);
    const index = Math.floor(Math.random() * presets.length);

    const t = new Tree();
    t.position.set(r * Math.cos(theta), 0, r * Math.sin(theta));
    t.loadPreset(presets[index]);
    t.options.seed = 10000 * Math.random();
    // Background trees: slightly darker than main tree but not black
    t.options.leaves.tint = 0x3a7098;
    t.generate();
    t.castShadow = false;
    t.receiveShadow = false;

    forest.add(t);
  }

  for (let i = 0; i < treeCount; i++) {
    createBackgroundTree();
  }

  scene.add(forest);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  const smaaPass = new SMAAPass(
    container.clientWidth * renderer.getPixelRatio(),
    container.clientHeight * renderer.getPixelRatio());
  composer.addPass(smaaPass);

  composer.addPass(new OutputPass());

  // Store defaults for reset
  const initialState = {
    cameraPos: DEFAULT_CAMERA_POS.clone(),
    target: DEFAULT_TARGET.clone()
  };

    return {
    scene,
    environment,
    tree,
    forest,
    stars,
    camera,
    controls,
    composer,
    initialState
  };
}
