type StoredPageState<T> = {
  version: number
  savedAt: string
  value: T
}

const STORAGE_PREFIX = 'skillbridge:page-state:v1'

function userScope() {
  try {
    const user = JSON.parse(localStorage.getItem('auth_user') || 'null')
    return String(user?.id || user?.username || 'anonymous')
  } catch {
    return 'anonymous'
  }
}

function stateKey(page: string) {
  return `${STORAGE_PREFIX}:${userScope()}:${page}`
}

export function loadPageState<T>(page: string): T | undefined {
  try {
    const raw = localStorage.getItem(stateKey(page))
    if (!raw) return undefined
    const stored = JSON.parse(raw) as StoredPageState<T>
    return stored?.version === 1 ? stored.value : undefined
  } catch {
    return undefined
  }
}

export function savePageState<T>(page: string, value: T) {
  const stored: StoredPageState<T> = {
    version: 1,
    savedAt: new Date().toISOString(),
    value
  }
  localStorage.setItem(stateKey(page), JSON.stringify(stored))
}

export function removePageState(page: string) {
  localStorage.removeItem(stateKey(page))
}
