import React, { useState } from 'react'
import { isLockedToday, communityCount } from '../lib/tracker.js'

function buildHistoryDisplay(state) {
  const days = []
  const base = new Date(state.doneDate)
  for (let i = 6; i >= 0; i--) {
    const d = new Date(base)
    d.setDate(d.getDate() - i)
    const dateStr = d.toDateString()
    let ratio
    if (dateStr === state.doneDate) {
      ratio = state.standards.length ? state.doneIds.length / state.standards.length : 0
    } else {
      const found = state.history.find((h) => h.date === dateStr)
      ratio = found ? found.ratio : 0
    }
    days.push({ dateStr, ratio, label: d.toLocaleDateString('en-US', { weekday: 'narrow' }) })
  }
  return days
}

export default function StandardModule({ state, onToggle, onAdd, onRemove }) {
  const [draft, setDraft] = useState('')
  const [shareStatus, setShareStatus] = useState('')
  const locked = isLockedToday(state)
  const total = state.standards.length
  const done = state.doneIds.length
  const pct = total ? Math.round((done / total) * 100) : 0
  const history = buildHistoryDisplay(state)
  const community = communityCount()

  const submitDraft = () => {
    if (locked) return
    onAdd(draft)
    setDraft('')
  }

  const shareText = `⚡ Day locked. Streak: ${state.streak}. #RAWVOLT`

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({ text: shareText })
      } catch {
        // user cancelled — no-op
      }
      return
    }
    try {
      await navigator.clipboard.writeText(shareText)
      setShareStatus('Copied!')
      setTimeout(() => setShareStatus(''), 2000)
    } catch {
      setShareStatus('Could not copy')
      setTimeout(() => setShareStatus(''), 2000)
    }
  }

  return (
    <div>
      <div className="voltage-wrap">
        <div className="voltage-label">
          <span>Voltage</span>
          <span>{pct}%</span>
        </div>
        <div className="voltage-track">
          <div className={`voltage-fill${locked ? ' locked' : ''}`} style={{ width: `${pct}%` }} />
        </div>
      </div>

      {locked && (
        <div className="locked-banner">
          DAY LOCKED
          <div className="sub">It doesn't unlock. That's the point.</div>
          <button className="ghost-btn share-btn" onClick={handleShare}>
            {shareStatus || 'Share'}
          </button>
        </div>
      )}

      <div className="stats-row">
        <div className="stat-box">
          <div className="stat-num">{state.streak}</div>
          <div className="stat-label">Streak</div>
        </div>
        <div className="stat-box">
          <div className="stat-num">{state.best}</div>
          <div className="stat-label">Best</div>
        </div>
      </div>

      <div className="card">
        <div className="section-title">Standards</div>
        <div className="section-desc">Your non-negotiables. Up to 7. Do them before the day ends.</div>

        {total === 0 && <div className="empty-hint">No standards set yet. Add your first one below.</div>}

        {state.standards.map((s) => {
          const isDone = state.doneIds.includes(s.id)
          return (
            <div className="standard-row" key={s.id}>
              <button className={`check-circle${isDone ? ' done' : ''}`} onClick={() => onToggle(s.id)}>
                {isDone ? '✓' : ''}
              </button>
              <span className={`standard-text${isDone ? ' done' : ''}`}>{s.text}</span>
              {!locked && (
                <button className="remove-btn" onClick={() => onRemove(s.id)} aria-label="Remove">
                  ✕
                </button>
              )}
            </div>
          )
        })}

        {!locked && total < 7 && (
          <div className="add-row">
            <input
              type="text"
              placeholder="Add a standard..."
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submitDraft()}
              maxLength={80}
            />
            <button className="add-btn" onClick={submitDraft} disabled={!draft.trim()}>
              +
            </button>
          </div>
        )}
      </div>

      <div className="card">
        <div className="section-title">Last 7 Days</div>
        <div className="history-row">
          {history.map((h) => (
            <div className="history-dot-wrap" key={h.dateStr}>
              <div className={`history-dot${h.ratio === 1 ? ' full' : h.ratio > 0 ? ' partial' : ''}`}>
                {h.ratio === 1 ? '⚡' : h.ratio > 0 ? '◐' : ''}
              </div>
              <div className="history-day-label">{h.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="live-counter">
        🔥 <b>{community.toLocaleString()}</b> people locked today
        <span className="label">Rawvolt Community</span>
      </div>
    </div>
  )
}
