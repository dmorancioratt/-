import type * as THREE from 'three'

export type EzTreeSceneContext = {
  scene: THREE.Scene
  environment: { update: (time: number) => void }
  tree: THREE.Object3D
  forest: THREE.Object3D[]
  stars: THREE.Points
  camera: THREE.PerspectiveCamera
  controls: {
    target: THREE.Vector3
    enabled: boolean
    update: () => void
  }
  composer: {
    render: () => void
    setSize: (width: number, height: number) => void
  }
  initialState: {
    position: THREE.Vector3
    target: THREE.Vector3
  }
}

export function createScene(
  container: HTMLElement,
  renderer: THREE.WebGLRenderer,
): Promise<EzTreeSceneContext>
