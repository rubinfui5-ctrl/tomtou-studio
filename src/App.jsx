import React, { useEffect, useMemo, useRef, useState } from 'react'
import { loadState, saveState, loadOnboarded, setOnboarded } from './lib/storage.js'
import { checkRollover, toggleStandard as toggleStandardFn, lockLine, progressLine } from './lib/tracker.js'
import { useVoices, speak, cancelSpeech } from './lib/voice.js'
import StandardModule from './modules/Standard.jsx'
import GuideModule from './modules/Guide.jsx'
import ExtractModule from './modules/Extract.jsx'

const ONBOARD_SCREENS = [
  'Set your standards. The things you must do before the day ends.',
  "Tap each one done. When all are done, the day LOCKS. It doesn't unlock. Like your word.",
  "Your streak builds. Come back tomorrow. That's how a man is built.",
]

function Onboarding({ voice, onFinish }) {
  const [screen, setScreen] = useState(0)

  useEffect(() => {
    speak(ONBOARD_SCREENS[screen], voice)
    return () => cancelSpeech()
  }, [screen, voice])

  const finish = () => {
    cancelSpeech()
    setOnboarded()
    onFinish()
  }

  return (
    <div className="overlay">
      <div className="onboard-screen">
        <div className="onboard-dots">
          {ONBOARD_SCREENS.map((_, i) => (
            <span key={i} className={`onboard-dot${i === screen ? ' active' : ''}`} />
          ))}
        </div>
        <p className="onboard-text">{ONBOARD_SCREENS[screen]}</p>
        <div className="onboard-actions">
          <button className="ghost-btn" onClick={finish}>
            Skip
          </button>
          <button
            className="primary-btn"
            onClick={() => {
              cancelSpeech()
              if (screen < ONBOARD_SCREENS.length - 1) setScreen(screen + 1)
              else finish()
            }}
          >
            {screen < ONBOARD_SCREENS.length - 1 ? 'Next' : "Let's Go"}
          </button>
        </div>
      </div>
    </div>
  )
}

function BottomNav({ tab, setTab }) {
  const tabs = [
    { id: 'standard', label: 'STANDARD', icon: '⚡' },
    { id: 'guide', label: 'GUIDE', icon: '🎙' },
    { id: 'extract', label: 'EXTRACT', icon: '💎' },
  ]
  return (
    <nav className="bottom-nav">
      {tabs.map((t) => (
        <button
          key={t.id}
          className={`nav-btn${tab === t.id ? ' active' : ''}`}
          onClick={() => setTab(t.id)}
        >
          <span className="nav-icon">{t.icon}</span>
          <span>{t.label}</span>
        </button>
      ))}
    </nav>
  )
}

export default function App() {
  const [state, setState] = useState(() => checkRollover(loadState()))
  const [tab, setTab] = useState('standard')
  const [showOnboarding, setShowOnboarding] = useState(() => !loadOnboarded())
  const { tomVoice, touVoice } = useVoices()
  const activeVoice = state.guideVoice === 'tou' ? touVoice : tomVoice
  const activeVoiceRef = useRef(activeVoice)
  activeVoiceRef.current = activeVoice

  useEffect(() => {
    saveState(state)
  }, [state])

  // Roll the day over if the app stays open across midnight.
  useEffect(() => {
    const id = setInterval(() => {
      setState((prev) => checkRollover(prev))
    }, 60000)
    return () => clearInterval(id)
  }, [])

  const updateState = (patch) => {
    setState((prev) => ({ ...prev, ...patch }))
  }

  const onToggleStandard = (id) => {
    setState((prev) => {
      const { next, event, streak } = toggleStandardFn(prev, id)
      if (prev.encourage) {
        if (event === 'locked') speak(lockLine(streak ?? next.streak), activeVoiceRef.current)
        else if (event === 'progress') speak(progressLine(), activeVoiceRef.current)
      }
      return next
    })
  }

  const addStandard = (text) => {
    const trimmed = text.trim()
    if (!trimmed || state.standards.length >= 7) return
    setState((prev) => ({
      ...prev,
      standards: [...prev.standards, { id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, text: trimmed }],
    }))
  }

  const removeStandard = (id) => {
    setState((prev) => ({
      ...prev,
      standards: prev.standards.filter((s) => s.id !== id),
      doneIds: prev.doneIds.filter((d) => d !== id),
    }))
  }

  const brandColor = state.guideVoice === 'tou' ? 'var(--yellow)' : 'var(--blue)'

  return (
    <div className="app">
      {showOnboarding && <Onboarding voice={activeVoice} onFinish={() => setShowOnboarding(false)} />}
      <header className="app-header">
        <h1 className="app-title">
          THE <span style={{ color: brandColor }}>STANDARD</span>
        </h1>
        <p className="app-tagline">Locked like your word</p>
      </header>
      <main className="app-body">
        {tab === 'standard' && (
          <StandardModule
            state={state}
            onToggle={onToggleStandard}
            onAdd={addStandard}
            onRemove={removeStandard}
            voice={activeVoice}
          />
        )}
        {tab === 'guide' && <GuideModule state={state} updateState={updateState} voices={{ tomVoice, touVoice }} />}
        {tab === 'extract' && <ExtractModule voice={activeVoice} guideVoice={state.guideVoice} />}
      </main>
      <BottomNav tab={tab} setTab={setTab} />
    </div>
  )
}
