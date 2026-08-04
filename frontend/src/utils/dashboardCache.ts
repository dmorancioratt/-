export type DashboardSnapshot<T> = {
  data: T
  updatedAt: string
  schemaVersion: number
}

const DASHBOARD_SCHEMA_VERSION = 4

export function readDashboardSnapshot<T>(key: string): DashboardSnapshot<T> | null {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed || typeof parsed !== 'object' || !parsed.data || !parsed.updatedAt || parsed.schemaVersion !== DASHBOARD_SCHEMA_VERSION) return null
    return parsed as DashboardSnapshot<T>
  } catch {
    return null
  }
}

export function writeDashboardSnapshot<T>(key: string, data: T): DashboardSnapshot<T> {
  const snapshot = { data, updatedAt: new Date().toISOString(), schemaVersion: DASHBOARD_SCHEMA_VERSION }
  localStorage.setItem(key, JSON.stringify(snapshot))
  return snapshot
}

export function formatSnapshotTime(value: string) {
  if (!value) return '尚未更新'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '时间未知'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

export function settledValue<T>(result: PromiseSettledResult<T>, fallback: T): T {
  return result.status === 'fulfilled' ? result.value : fallback
}
