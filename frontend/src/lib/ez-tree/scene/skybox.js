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
    uniforms.sunPosition.value.set(100, 30, 100);
    uniforms.up.value.set(0, 1, 0);
    uniforms.rayleigh.value = 1.2;
    uniforms.turbidity.value = 8;
    uniforms.mieCoefficient.value = 0.005;
    uniforms.mieDirectionalG.value = 0.8;

    // Ambient light
    this.ambient = new THREE.AmbientLight(0xffffff, 1.15);
    this.ambient.name = 'ambient';
    this.add(this.ambient);

    // Sun (directional light)
    this.sun = new THREE.DirectionalLight(0xffffff, 4.5);
    this.sun.name = 'sun';
    this.sun.position.set(60, 80, -120);
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

    // Hemisphere light
    this.hemi = new THREE.HemisphereLight(0x87ceeb, 0x556b2f, 0.3);
    this.hemi.name = 'hemi';
    this.add(this.hemi);
  }
}
