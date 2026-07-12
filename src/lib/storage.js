const STANDARD_KEY = 'rawvolt-standard-v1'
const ONBOARD_KEY = 'rawvolt-onboarded'
const EXTRACT_KEY = 'rawvolt-extract-list'

export function todayStr(d = new Date()) {
  return d.toDateString()
}

export function yesterdayOf(dateStr) {
  const d = new Date(dateStr)
  d.setDate(d.getDate() - 1)
  return d.toDateString()
}

export function defaultState() {
  return {
    standards: [],
    doneDate: todayStr(),
    doneIds: [],
    streak: 0,
    best: 0,
    lastLocked: null,
    history: [],
    encourage: true,
    guideVoice: 'tom',
  }
}

export function loadState() {
  try {
    const raw = localStorage.getItem(STANDARD_KEY)
    if (!raw) return defaultState()
    const parsed = JSON.parse(raw)
    return { ...defaultState(), ...parsed }
  } catch {
    return defaultState()
  }
}

export function saveState(state) {
  try {
    localStorage.setItem(STANDARD_KEY, JSON.stringify(state))
  } catch {
    // storage unavailable — ignore
  }
}

export function loadOnboarded() {
  return localStorage.getItem(ONBOARD_KEY) === 'true'
}

export function setOnboarded() {
  try {
    localStorage.setItem(ONBOARD_KEY, 'true')
  } catch {
    // ignore
  }
}

export function loadExtractList() {
  try {
    const raw = localStorage.getItem(EXTRACT_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function saveExtractList(list) {
  try {
    localStorage.setItem(EXTRACT_KEY, JSON.stringify(list.slice(0, 20)))
  } catch {
    // ignore
  }
}
