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

export async function createScene(container, renderer) {
  const w = container.clientWidth;
  const h = container.clientHeight;

  renderer.setClearColor(0x000000, 0);
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  // Soft blue twilight fog — light enough not to crush tree to black,
  // but still cohesive with the deep-blue page background
  scene.fog = new THREE.FogExp2(0x1a3a5c, 0.0008);

  const environment = new Environment();
  scene.add(environment);

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
  tree.options.leaves.tint = 0x4a8090;
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
    t.options.leaves.tint = 0x3a6880;
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
    camera,
    controls,
    composer,
    initialState
  };
}
