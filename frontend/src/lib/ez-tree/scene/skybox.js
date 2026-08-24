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

    const uniforms = this.sky.material.uniforms;
    uniforms.sunPosition.value.set(80, 40, 120);
    uniforms.up.value.set(0, 1, 0);
    uniforms.rayleigh.value = 2.0;
    uniforms.turbidity.value = 6;
    uniforms.mieCoefficient.value = 0.003;
    uniforms.mieDirectionalG.value = 0.7;

    // Ambient light — bright enough to prevent crushed blacks
    this.ambient = new THREE.AmbientLight(0xb0c8e0, 1.0);
    this.ambient.name = 'ambient';
    this.add(this.ambient);

    // Sun (directional light) — positioned front-right-above to illuminate the
    // face of the tree as seen from the default camera (z=+145, looking at origin)
    this.sun = new THREE.DirectionalLight(0xfff4e0, 3.2);
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
    this.hemi = new THREE.HemisphereLight(0x8fc4e8, 0x2a3a4a, 0.6);
    this.hemi.name = 'hemi';
    this.add(this.hemi);
  }
}
