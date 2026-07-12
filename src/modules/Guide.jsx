import React, { useEffect, useRef, useState } from 'react'
import { speak, speakSequence, cancelSpeech } from '../lib/voice.js'

const TOUR_SENTENCES = [
  'Welcome to The Standard.',
  'This is where you lock your day.',
  'Set your non-negotiables — the things you must do before the day ends.',
  'Tap each one as you complete it. The voltage bar fills.',
  'When every standard is done, the day LOCKS.',
  "It doesn't unlock. That's the point.",
  'Locked like your word.',
  'Your streak builds. Your history shows the last 7 days.',
  'Come back tomorrow. Do it again.',
  "That's how a man is built.",
]

const PHASE_LABELS = {
  inhale: 'Breathe In',
  hold1: 'Hold',
  exhale: 'Breathe Out',
  hold2: 'Hold',
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function BoxBreathing({ voice, onClose }) {
  const [phase, setPhase] = useState('inhale')
  const [cycle, setCycle] = useState(1)
  const cancelledRef = useRef(false)

  useEffect(() => {
    cancelledRef.current = false
    const phases = [
      { key: 'inhale', label: 'Breathe in' },
      { key: 'hold1', label: 'Hold' },
      { key: 'exhale', label: 'Breathe out' },
      { key: 'hold2', label: 'Hold' },
    ]

    async function run() {
      for (let c = 1; c <= 4; c++) {
        if (cancelledRef.current) return
        setCycle(c)
        for (const p of phases) {
          if (cancelledRef.current) return
          setPhase(p.key)
          speak(`${p.label}. One, two, three, four.`, voice)
          await delay(4000)
          if (cancelledRef.current) return
        }
      }
      if (!cancelledRef.current) onClose()
    }

    run()

    return () => {
      cancelledRef.current = true
      cancelSpeech()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="overlay">
      <span className="breath-cycle-label">Cycle {cycle} of 4</span>
      <div className="breath-circle-wrap">
        <div className={`breath-circle ${phase}`} />
      </div>
      <div className="breath-phase-label">{PHASE_LABELS[phase]}</div>
      <div className="breath-count">ONE · TWO · THREE · FOUR</div>
      <button className="overlay-close" onClick={onClose}>
        Close
      </button>
    </div>
  )
}

export default function GuideModule({ state, updateState, voices }) {
  const [touring, setTouring] = useState(false)
  const [breathing, setBreathing] = useState(false)
  const tourTokenRef = useRef({ cancelled: false })
  const activeVoice = state.guideVoice === 'tou' ? voices.touVoice : voices.tomVoice

  useEffect(() => {
    return () => cancelSpeech()
  }, [])

  const startTour = async () => {
    setTouring(true)
    const token = { cancelled: false }
    tourTokenRef.current = token
    await speakSequence(TOUR_SENTENCES, activeVoice, token, 350)
    if (!token.cancelled) setTouring(false)
  }

  const stopTour = () => {
    tourTokenRef.current.cancelled = true
    cancelSpeech()
    setTouring(false)
  }

  return (
    <div>
      <div className="voice-select-row">
        <button
          className={`brand-btn${state.guideVoice === 'tom' ? ' blue-active' : ''}`}
          onClick={() => updateState({ guideVoice: 'tom' })}
        >
          TOM
        </button>
        <button
          className={`brand-btn${state.guideVoice === 'tou' ? ' yellow-active' : ''}`}
          onClick={() => updateState({ guideVoice: 'tou' })}
        >
          TOU
        </button>
      </div>

      <div className="card">
        <div className="section-title">Spoken App Tour</div>
        <div className="section-desc">A 60-second walkthrough, in {state.guideVoice === 'tou' ? 'TOU' : 'TOM'}'s voice.</div>
        {touring ? (
          <button className="ghost-btn" onClick={stopTour}>
            ■ Stop
          </button>
        ) : (
          <button className="primary-btn" onClick={startTour}>
            Take the Tour
          </button>
        )}
      </div>

      <div className="card">
        <div className="section-title">Box Breathing</div>
        <div className="section-desc">4-4-4-4 breathwork. Four cycles, voice-led, about a minute.</div>
        <button className="primary-btn" onClick={() => setBreathing(true)}>
          Box Breathing
        </button>
      </div>

      <div className="card">
        <div className="toggle-row">
          <span className="toggle-label">Voice Encouragement</span>
          <button
            className={`toggle-switch${state.encourage ? ' on' : ''}`}
            onClick={() => updateState({ encourage: !state.encourage })}
            aria-label="Toggle voice encouragement"
          />
        </div>
        <div className="section-desc" style={{ marginTop: 8, marginBottom: 0 }}>
          When on, {state.guideVoice === 'tou' ? 'TOU' : 'TOM'} speaks short lines as you complete standards and lock the day.
        </div>
      </div>

      {breathing && (
        <BoxBreathing
          voice={activeVoice}
          onClose={() => {
            setBreathing(false)
          }}
        />
      )}
    </div>
  )
}
