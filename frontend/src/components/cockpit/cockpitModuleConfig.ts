export type CockpitModuleId = 'resource' | 'skill' | 'path' | 'profile' | 'calendar' | 'achievement' | 'assistant'

export type CockpitModuleConfig = {
  id: CockpitModuleId
  panel: 'resource-library' | 'jobs' | 'radar' | 'path' | 'timeline' | 'weekly-plan' | 'interview' | 'ai-suggest' | 'avatar'
  label: string
  subtitle: string
  model: string
  position: [number, number, number]
  rotation: [number, number, number]
  scale: number
  hoverOffset: [number, number, number]
  tooltipLift: number
  focusOffset: [number, number, number]
}

/**
 * These coordinates follow the cabin's physical equipment bays. The z-axis
 * separates rear-wall terminals, the central desk and floor displays, so the
 * scene still reads as a room rather than a planar module grid.
 *
 * Skill/profile use the opposite source files from the earlier layout. Their
 * GLBs were visually inspected: 43d... is the node graph and c2e... is the
 * identity terminal.
 */
export const cockpitModules: CockpitModuleConfig[] = [
  {
    id: 'skill', panel: 'radar', label: '能力图谱', subtitle: 'SKILL GRAPH',
    model: '/cockpit-models/b4af90cb5de5f430ddb16352bc946691.glb',
    position: [-6.102, 2.581, -1.68], rotation: [.11, .469, -.009], scale: 3.322,
    hoverOffset: [.04, .035, .16], tooltipLift: .96, focusOffset: [.2, .15, 4.55],
  },
  {
    id: 'path', panel: 'path', label: '学习路径', subtitle: 'LEARNING PATH',
    model: '/cockpit-models/0238490c0021c3fe8ed2c83fbb174fa1.glb',
    position: [-.104, 3.226, -1.439], rotation: [.01, 0, 0], scale: 5.477,
    hoverOffset: [0, .035, .17], tooltipLift: .84, focusOffset: [0, .08, 4.55],
  },
  {
    id: 'profile', panel: 'avatar', label: '成长档案', subtitle: 'GROWTH PROFILE',
    model: '/cockpit-models/c2e5a511e7d2eea5d60b06c3f7c797e7.glb',
    position: [5.357, 3.296, -1.36], rotation: [.218, -.68, -.037], scale: 3.596,
    hoverOffset: [-.03, .035, .17], tooltipLift: .96, focusOffset: [-.2, .12, 4.55],
  },
  {
    id: 'resource', panel: 'resource-library', label: '资源库', subtitle: 'RESOURCE VAULT',
    model: '/cockpit-models/afae85ee1afa72638ac23f578e88dd09.glb',
    position: [-4.8, -1.72, 1.652], rotation: [.233, .533, .044], scale: 3.341,
    hoverOffset: [.04, .10, .10], tooltipLift: 1.05, focusOffset: [.25, .22, 4.05],
  },
  {
    id: 'assistant', panel: 'ai-suggest', label: 'AI 助手', subtitle: 'AI COMPANION',
    model: '/cockpit-models/714f21221afae8f61f62077ab1235b7b.glb',
    position: [-.02, -.04, 1.05], rotation: [.015, .08, 0], scale: 1.88,
    hoverOffset: [0, .10, .10], tooltipLift: 1.08, focusOffset: [.1, .25, 3.75],
  },
  {
    id: 'calendar', panel: 'weekly-plan', label: '计划日历', subtitle: 'MISSION CALENDAR',
    model: '/cockpit-models/c60c44fe7dc32d1d989edabb8c9432dc.glb',
    position: [4.782, .323, 1.123], rotation: [.53, -.692, .164], scale: 3.371,
    hoverOffset: [-.03, .045, .15], tooltipLift: .88, focusOffset: [-.15, .12, 4.15],
  },
  {
    id: 'achievement', panel: 'timeline', label: '成就奖杯柜', subtitle: 'ACHIEVEMENT VAULT',
    model: '/cockpit-models/f7426268d4c1a8e9565b6191b0180dd7.glb',
    position: [3.951, -1.761, 2.793], rotation: [.156, -.857, .017], scale: 2.854,
    hoverOffset: [-.035, .09, .10], tooltipLift: .78, focusOffset: [-.2, .12, 3.7],
  },
]

export const defaultCamera = {
  position: [0, 0, 13.2] as [number, number, number],
  target: [0, 0, 0] as [number, number, number],
}
