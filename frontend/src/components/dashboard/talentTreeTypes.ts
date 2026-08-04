export type LifeTreeItem = {
  name: string
  score: number
  category: string
  status: 'mastered' | 'growing' | 'missing'
}

export type TalentBranch = 'professional' | 'engineering' | 'general'

export type TalentNodeData = {
  kind: 'core' | 'branch' | 'skill'
  label: string
  subtitle: string
  progress: number
  status: LifeTreeItem['status']
  branch: TalentBranch
  selected?: boolean
  item?: LifeTreeItem
}

export type EnergyEdgeData = {
  status: LifeTreeItem['status']
  active?: boolean
}
