import React, { useEffect, useRef, useState } from 'react'
import { speak, cancelSpeech } from '../lib/voice.js'
import { SEED_QUESTIONS, getNextQuestion, generatePack, sendToZapier, transcriptToText } from '../lib/extract.js'
import { loadExtractList, saveExtractList } from '../lib/storage.js'
import { ZAPIER_WEBHOOK_URL } from '../lib/config.js'

const TOTAL_QUESTIONS = 10

function getRecognition() {
  if (typeof window === 'undefined') return null
  const Ctor = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!Ctor) return null
  const recognition = new Ctor()
  recognition.continuous = true
  recognition.interimResults = true
  recognition.lang = 'en-US'
  return recognition
}

function PackView({ record, onCopy, onSend, onBack }) {
  const { pack, sent } = record
  const [copied, setCopied] = useState(false)
  const [sendStatus, setSendStatus] = useState(sent ? 'sent' : 'idle')

  const doCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(pack, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      onCopy?.()
    } catch {
      setCopied(false)
    }
  }

  const doSend = async () => {
    setSendStatus('sending')
    const ok = await onSend()
    setSendStatus(ok ? 'sent' : 'failed')
  }

  return (
    <div>
      <div className="card">
        <div className="pack-title">{pack.title}</div>
        <div className="pack-summary">{pack.summary}</div>

        {pack.marketing_hook && <div className="pack-hook">"{pack.marketing_hook}"</div>}

        {Array.isArray(pack.skills) && pack.skills.length > 0 && (
          <>
            <div className="pack-section-title">Skills</div>
            {pack.skills.map((s, i) => (
              <div className="pack-item" key={i}>
                <b>{s.skill}</b> {s.level ? `— ${s.level}` : ''}
                {s.description ? <div>{s.description}</div> : null}
              </div>
            ))}
          </>
        )}

        {Array.isArray(pack.experience_highlights) && pack.experience_highlights.length > 0 && (
          <>
            <div className="pack-section-title">Experience Highlights</div>
            {pack.experience_highlights.map((h, i) => (
              <div className="pack-item" key={i}>
                {h}
              </div>
            ))}
          </>
        )}

        {Array.isArray(pack.stories) && pack.stories.length > 0 && (
          <>
            <div className="pack-section-title">Stories</div>
            {pack.stories.map((s, i) => (
              <div className="pack-item" key={i}>
                <b>{s.title}</b>
                {s.lesson ? <div>{s.lesson}</div> : null}
              </div>
            ))}
          </>
        )}

        {Array.isArray(pack.frameworks) && pack.frameworks.length > 0 && (
          <>
            <div className="pack-section-title">Frameworks</div>
            {pack.frameworks.map((f, i) => (
              <div className="pack-item" key={i}>
                <b>{f.name}</b>
                {f.description ? <div>{f.description}</div> : null}
              </div>
            ))}
          </>
        )}

        {Array.isArray(pack.monetizable_products) && pack.monetizable_products.length > 0 && (
          <>
            <div className="pack-section-title">Monetizable Products</div>
            {pack.monetizable_products.map((p, i) => (
              <div className="pack-item" key={i}>
                <b>{p.product_name}</b> {p.format ? `— ${p.format}` : ''}
                <div>
                  {p.price_range} {p.target_audience ? `· ${p.target_audience}` : ''}
                </div>
              </div>
            ))}
          </>
        )}

        <div className="pack-section-title">Full Transcript</div>
        <div className="pack-item" style={{ whiteSpace: 'pre-wrap' }}>
          {pack.full_transcript}
        </div>

        <div className="pack-actions">
          <button className="ghost-btn" onClick={doCopy}>
            {copied ? 'Copied!' : 'Copy Pack'}
          </button>
          {sendStatus === 'sent' ? (
            <span className="badge sent">SENT TO RAWVOLT ✓</span>
          ) : (
            <button className="ghost-btn" onClick={doSend} disabled={sendStatus === 'sending'}>
              {sendStatus === 'sending' ? 'Sending…' : sendStatus === 'failed' ? 'Save locally — send later' : 'Send to RAWVOLT'}
            </button>
          )}
        </div>
      </div>
      <button className="ghost-btn" onClick={onBack}>
        ← Back
      </button>
    </div>
  )
}

export default function ExtractModule({ voice }) {
  const [view, setView] = useState('consent') // consent | interview | generating | pack | history
  const [consented, setConsented] = useState(false)
  const [questions, setQuestions] = useState(SEED_QUESTIONS)
  const [index, setIndex] = useState(0)
  const [transcript, setTranscript] = useState([])
  const [answer, setAnswer] = useState('')
  const [listening, setListening] = useState(false)
  const [loadingNext, setLoadingNext] = useState(false)
  const [activeRecord, setActiveRecord] = useState(null)
  const [history, setHistory] = useState(() => loadExtractList())
  const recognitionRef = useRef(null)

  useEffect(() => {
    const rec = getRecognition()
    if (!rec) return
    rec.onresult = (e) => {
      let finalText = ''
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) finalText += e.results[i][0].transcript
      }
      if (finalText.trim()) {
        setAnswer((prev) => (prev ? `${prev} ${finalText.trim()}` : finalText.trim()))
      }
    }
    rec.onend = () => setListening(false)
    rec.onerror = () => setListening(false)
    recognitionRef.current = rec
    return () => {
      try {
        rec.stop()
      } catch {
        // already stopped
      }
    }
  }, [])

  useEffect(() => {
    if (view === 'interview' && questions[index]) {
      speak(questions[index], voice)
    }
    return () => cancelSpeech()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, index])

  const toggleListening = () => {
    const rec = recognitionRef.current
    if (!rec) return
    if (listening) {
      rec.stop()
      setListening(false)
    } else {
      try {
        rec.start()
        setListening(true)
      } catch {
        // recognition already running
      }
    }
  }

  const beginInterview = () => {
    setQuestions(SEED_QUESTIONS)
    setIndex(0)
    setTranscript([])
    setAnswer('')
    setView('interview')
  }

  const submitAnswer = async () => {
    const trimmed = answer.trim()
    const newTranscript = [...transcript, { question: questions[index], answer: trimmed }]
    setTranscript(newTranscript)
    setAnswer('')
    if (recognitionRef.current && listening) {
      recognitionRef.current.stop()
      setListening(false)
    }

    if (newTranscript.length >= TOTAL_QUESTIONS) {
      setView('generating')
      const pack = await generatePack(newTranscript)
      const record = { id: `${Date.now()}`, createdAt: new Date().toISOString(), pack, transcript: newTranscript, sent: false }

      let sent = false
      if (ZAPIER_WEBHOOK_URL) {
        const result = await sendToZapier(ZAPIER_WEBHOOK_URL, pack, newTranscript)
        sent = !!result.ok
      }
      record.sent = sent

      const updatedHistory = [record, ...history].slice(0, 20)
      setHistory(updatedHistory)
      saveExtractList(updatedHistory)
      setActiveRecord(record)
      setView('pack')
      return
    }

    setLoadingNext(true)
    const fallback = SEED_QUESTIONS[newTranscript.length] || 'Anything else worth knowing?'
    const nextQ = await getNextQuestion(newTranscript, fallback)
    setQuestions((prev) => {
      const copy = [...prev]
      copy[newTranscript.length] = nextQ
      return copy
    })
    setIndex(newTranscript.length)
    setLoadingNext(false)
  }

  const resendRecord = async (record) => {
    const result = await sendToZapier(ZAPIER_WEBHOOK_URL, record.pack, record.transcript)
    if (result.ok) {
      const updated = history.map((h) => (h.id === record.id ? { ...h, sent: true } : h))
      setHistory(updated)
      saveExtractList(updated)
      setActiveRecord({ ...record, sent: true })
    }
    return result.ok
  }

  if (view === 'history') {
    return (
      <div>
        <div className="section-title">Knowledge Packs</div>
        <div className="section-desc">Last {history.length} interviews, saved on this device.</div>
        {history.length === 0 && <div className="empty-hint">No packs yet. Run an interview to create one.</div>}
        {history.map((h) => (
          <div
            className="pack-history-item"
            key={h.id}
            onClick={() => {
              setActiveRecord(h)
              setView('pack')
            }}
          >
            <div>
              <div className="pack-history-title">{h.pack.title}</div>
              <div className="pack-history-date">{new Date(h.createdAt).toLocaleString()}</div>
            </div>
            {h.sent && <span className="badge sent">SENT</span>}
          </div>
        ))}
        <button className="ghost-btn" onClick={() => setView('consent')}>
          ← Back
        </button>
      </div>
    )
  }

  if (view === 'pack' && activeRecord) {
    return (
      <PackView
        record={activeRecord}
        onSend={() => resendRecord(activeRecord)}
        onBack={() => setView('consent')}
      />
    )
  }

  if (view === 'generating') {
    return <div className="loading-text">⟳ Building your Knowledge Pack…</div>
  }

  if (view === 'interview') {
    const progress = Math.round((transcript.length / TOTAL_QUESTIONS) * 100)
    return (
      <div>
        <div className="progress-label">
          Question {Math.min(index + 1, TOTAL_QUESTIONS)} of {TOTAL_QUESTIONS}
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="card">
          <div className="question-text">{questions[index]}</div>
          <div className="mic-row">
            {recognitionRef.current && (
              <button className={`mic-btn${listening ? ' listening' : ''}`} onClick={toggleListening}>
                🎙
              </button>
            )}
            <span className="section-desc" style={{ marginBottom: 0 }}>
              {recognitionRef.current
                ? listening
                  ? 'Listening…'
                  : 'Tap the mic to speak, or type below.'
                : 'Voice input not supported here — type your answer.'}
            </span>
          </div>
          <textarea
            className="answer-area"
            placeholder="Your answer…"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />
          <button
            className="primary-btn"
            style={{ marginTop: 14 }}
            onClick={submitAnswer}
            disabled={!answer.trim() || loadingNext}
          >
            {loadingNext ? 'Thinking…' : index + 1 === TOTAL_QUESTIONS ? 'Finish' : 'Next'}
          </button>
        </div>
      </div>
    )
  }

  // consent screen
  return (
    <div>
      <div className="card">
        <div className="section-title">Extract</div>
        <div className="section-desc">
          Free interview. Rubin packages your knowledge into a digital product and sells it. Rev-share agreed in
          writing.
        </div>
        <div className="consent-box">
          <input
            type="checkbox"
            id="consent-check"
            checked={consented}
            onChange={(e) => setConsented(e.target.checked)}
          />
          <label htmlFor="consent-check">
            I agree to be interviewed and understand my answers will be packaged into a knowledge product by
            RAWVOLT. I will receive a rev-share agreement in writing.
          </label>
        </div>
        <button className="primary-btn" disabled={!consented} onClick={beginInterview}>
          Begin Interview
        </button>
      </div>
      <button className="ghost-btn" onClick={() => setView('history')}>
        View Pack History ({history.length})
      </button>
    </div>
  )
}
