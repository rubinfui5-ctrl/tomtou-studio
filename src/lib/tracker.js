import { todayStr, yesterdayOf } from './storage.js'

export function upsertHistory(history, date, ratio) {
  const filtered = history.filter((h) => h.date !== date)
  const updated = [...filtered, { date, ratio }]
  updated.sort((a, b) => new Date(a.date) - new Date(b.date))
  return updated.slice(-7)
}

export function isLockedToday(state) {
  return (
    state.standards.length > 0 &&
    state.doneIds.length === state.standards.length &&
    state.lastLocked === state.doneDate
  )
}

export function checkRollover(state) {
  const today = todayStr()
  if (state.doneDate === today) return state
  const ratio = state.standards.length ? state.doneIds.length / state.standards.length : 0
  const newHistory = upsertHistory(state.history, state.doneDate, ratio)
  return { ...state, doneDate: today, doneIds: [], history: newHistory }
}

export function toggleStandard(state, id) {
  if (isLockedToday(state)) {
    return { next: state, event: null }
  }
  const has = state.doneIds.includes(id)
  const newDoneIds = has ? state.doneIds.filter((x) => x !== id) : [...state.doneIds, id]
  const ratio = state.standards.length ? newDoneIds.length / state.standards.length : 0
  let newHistory = upsertHistory(state.history, state.doneDate, ratio)
  let streak = state.streak
  let best = state.best
  let lastLocked = state.lastLocked
  let event = null

  const willLock =
    state.standards.length > 0 && newDoneIds.length === state.standards.length && state.lastLocked !== state.doneDate

  if (willLock) {
    const yesterday = yesterdayOf(state.doneDate)
    streak = state.lastLocked === yesterday ? state.streak + 1 : 1
    best = Math.max(state.best, streak)
    lastLocked = state.doneDate
    newHistory = upsertHistory(newHistory, state.doneDate, 1)
    event = 'locked'
  } else if (!has) {
    event = 'progress'
  }

  const next = { ...state, doneIds: newDoneIds, history: newHistory, streak, best, lastLocked }
  return { next, event, streak }
}

export function communityCount() {
  const now = new Date()
  const start = new Date(now.getFullYear(), 0, 0)
  const dayOfYear = Math.floor((now - start) / 86400000)
  const hourFactor = now.getHours() * 3 + Math.floor(now.getMinutes() / 10)
  return dayOfYear * 7 + 142 + hourFactor
}

export const ENCOURAGE_PROGRESS_LINES = [
  "That's one. Keep going.",
  'Good. Next.',
  'One down. Stay on it.',
  'Locked in. Next standard.',
]

export function lockLine(streak) {
  const lines = [
    `Day locked. That's your word. Streak: ${streak}.`,
    'Locked. Like your word. Come back tomorrow.',
    `Voltage full. Day sealed. Streak: ${streak}.`,
  ]
  return lines[Math.floor(Math.random() * lines.length)]
}

export function progressLine() {
  return ENCOURAGE_PROGRESS_LINES[Math.floor(Math.random() * ENCOURAGE_PROGRESS_LINES.length)]
}
