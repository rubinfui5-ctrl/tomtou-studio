import { useEffect, useMemo, useState } from 'react'

const MALE_NAMES = ['daniel', 'alex', 'arthur', 'google uk english male', 'fred', 'oliver']
const FEMALE_NAMES = ['samantha', 'karen', 'google uk english female', 'maria', 'victoria', 'moira']

function pickVoice(voices, heuristics, genderWord) {
  if (!voices.length) return null
  const byName = voices.find((v) => heuristics.some((h) => v.name.toLowerCase().includes(h)))
  if (byName) return byName
  const byGender = voices.find((v) => v.name.toLowerCase().includes(genderWord))
  if (byGender) return byGender
  const english = voices.find((v) => v.lang && v.lang.toLowerCase().startsWith('en'))
  return english || voices[0]
}

export function useVoices() {
  const [voices, setVoices] = useState(() =>
    typeof window !== 'undefined' && 'speechSynthesis' in window ? window.speechSynthesis.getVoices() : []
  )

  useEffect(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return
    function load() {
      setVoices(window.speechSynthesis.getVoices())
    }
    load()
    window.speechSynthesis.onvoiceschanged = load
    return () => {
      window.speechSynthesis.onvoiceschanged = null
    }
  }, [])

  const tomVoice = useMemo(() => pickVoice(voices, MALE_NAMES, 'male'), [voices])
  const touVoice = useMemo(() => pickVoice(voices, FEMALE_NAMES, 'female'), [voices])

  return { voices, tomVoice, touVoice, supported: typeof window !== 'undefined' && 'speechSynthesis' in window }
}

export function speak(text, voice, opts = {}) {
  return new Promise((resolve) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window) || !text) {
      resolve()
      return
    }
    const u = new SpeechSynthesisUtterance(text)
    if (voice) u.voice = voice
    u.rate = opts.rate || 1
    u.pitch = opts.pitch || 1
    u.onend = () => resolve()
    u.onerror = () => resolve()
    window.speechSynthesis.speak(u)
  })
}

export function cancelSpeech() {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
}

export async function speakSequence(sentences, voice, controlToken, pauseMs = 300) {
  for (const sentence of sentences) {
    if (controlToken.cancelled) return
    await speak(sentence, voice)
    if (controlToken.cancelled) return
    await new Promise((r) => setTimeout(r, pauseMs))
  }
}
