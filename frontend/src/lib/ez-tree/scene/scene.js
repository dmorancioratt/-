import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Tree, TreePreset } from '../index.js';
import { Environment } from './environment.js';

export async function createScene(container, renderer) {
  const w = container.clientWidth;
  const h = container.clientHeight;

  renderer.setClearColor(0);
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x87CEEB, 0.0006);

  const environment = new Environment();
  scene.add(environment);

  const camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 2000);
  camera.position.set(110, 75, 110);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = true;
  controls.minPolarAngle = 0;
  controls.maxPolarAngle = Math.PI;
  controls.minDistance = 30;
  controls.maxDistance = 300;
  controls.target.set(0, 35, 0);
  controls.update();

  const tree = new Tree();
  tree.loadPreset('Oak Large');
  tree.options.seed = 29919;
  tree.options.leaves.tint = 0x4A8C3A;
  tree.options.leaves.textured = true;
  tree.options.leaves.type = 'oak';
  tree.options.leaves.alphaTest = 0.5;
  tree.generate();
  tree.castShadow = true;
  tree.receiveShadow = true;
  scene.add(tree);

  // Add a forest of trees in the background
  const forest = new THREE.Group();
  forest.name = 'Forest';

  const treeCount = 100;
  const minDistance = 175;
  const maxDistance = 500;

  function createBackgroundTree() {
    const r = minDistance + Math.random() * maxDistance;
    const theta = 2 * Math.PI * Math.random();
    const presets = Object.keys(TreePreset);
    const index = Math.floor(Math.random() * presets.length);

    const t = new Tree();
    t.position.set(r * Math.cos(theta), 0, r * Math.sin(theta));
    t.loadPreset(presets[index]);
    t.options.seed = 10000 * Math.random();
    t.generate();
    t.castShadow = true;
    t.receiveShadow = true;

    forest.add(t);
  }

  // Create forest trees
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

  return {
    scene,
    environment,
    tree,
    forest,
    camera,
    controls,
    composer
  };
}
