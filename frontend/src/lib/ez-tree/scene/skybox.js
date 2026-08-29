import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';

export class Skybox extends THREE.Object3D {
  constructor() {
    super();

    this.name = 'skybox';

    // Create sky
    this.sky = new Sky();
    this.sky.scale.setScalar(450000);
    this.add(this.sky);
    this.sky.visible = false; // Sky在夜间模式会渲染成纯黑，改用scene.background固定优雅深蓝

    const uniforms = this.sky.material.uniforms;
    uniforms.sunPosition.value.set(-55, -8, -100);
    uniforms.up.value.set(0, 1, 0);
    uniforms.rayleigh.value = 1.8;
    uniforms.turbidity.value = 5;
    uniforms.mieCoefficient.value = 0.003;
    uniforms.mieDirectionalG.value = 0.7;

    // Ambient light — bright enough to prevent crushed blacks
    this.ambient = new THREE.AmbientLight(0x6a88aa, 0.55);
    this.ambient.name = 'ambient';
    this.add(this.ambient);

    // Sun (directional light) — positioned front-right-above to illuminate the
    // face of the tree as seen from the default camera (z=+145, looking at origin)
    this.sun = new THREE.DirectionalLight(0xe0edff, 4.9);
    this.sun.name = 'sun';
    this.sun.position.set(80, 75, 120);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    this.sun.shadow.camera.near = 1;
    this.sun.shadow.camera.far = 2000;
    const d = 300;
    this.sun.shadow.camera.left = -d;
    this.sun.shadow.camera.right = d;
    this.sun.shadow.camera.top = d;
    this.sun.shadow.camera.bottom = -d;
    this.sun.shadow.bias = -0.0005;
    this.add(this.sun);

    this.sunTarget = new THREE.Object3D();
    this.sunTarget.position.set(0, 0, 0);
    this.add(this.sunTarget);
    this.sun.target = this.sunTarget;

    // Hemisphere light — cool blue sky above, dark ground below
    this.hemi = new THREE.HemisphereLight(0x3a5a8a, 0x0a1a3a, 0.42);
    this.hemi.name = 'hemi';
    this.add(this.hemi);
  }
}
