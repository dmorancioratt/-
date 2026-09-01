export type MissionCabinId =
  | 'resource-library'
  | 'radar'
  | 'path'
  | 'avatar'
  | 'ai-suggest'
  | 'weekly-plan'
  | 'timeline'

type MissionCabinHeading = {
  code: string
  title: string
  english: string
}

// Static navigation labels only. User progress and profile data must come from APIs.
export const missionCabins: Pick<Record<MissionCabinId, MissionCabinHeading>, 'avatar'> = {
  avatar: {
    code: '03',
    title: '数字成长档案舱',
    english: 'GROWTH PROFILE',
  },
}
