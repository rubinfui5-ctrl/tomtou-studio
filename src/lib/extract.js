import { askClaude } from './api.js'

export const SEED_QUESTIONS = [
  'What would you say is your primary craft or expertise?',
  'How long have you been doing this, and how did you start?',
  "What's a skill you have that most people in your field don't?",
  "Tell me about a framework or method you've developed.",
  "What's a story from your career that taught you the most?",
  'What would you say is the most monetizable thing you know?',
  'If you were to teach someone your craft, what would the first lesson be?',
  "What's a mistake you see people make in your industry?",
  "What's a product or service you could build from your knowledge?",
  "What's one thing you know that people would pay for?",
]

function transcriptToText(transcript) {
  return transcript.map((t, i) => `Q${i + 1}: ${t.question}\nA${i + 1}: ${t.answer}`).join('\n\n')
}

export async function getNextQuestion(transcript, fallbackQuestion) {
  const result = await askClaude({
    model: 'claude-opus-4-8',
    max_tokens: 200,
    system:
      'You are an expert knowledge extractor conducting a live voice interview. Based on the previous answers, ask ONE deeper, more specific follow-up question that digs into the expert\'s knowledge. Return ONLY the question text — no preamble, no numbering, no quotes.',
    messages: [
      {
        role: 'user',
        content: `Interview so far:\n\n${transcriptToText(transcript)}\n\nAsk the next question.`,
      },
    ],
  })
  if (result.ok && result.text.trim()) {
    return result.text.trim().replace(/^["']|["']$/g, '')
  }
  return fallbackQuestion
}

function parsePackJSON(text) {
  try {
    let cleaned = text.trim()
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/```$/, '').trim()
    const start = cleaned.indexOf('{')
    const end = cleaned.lastIndexOf('}')
    if (start === -1 || end === -1) return null
    return JSON.parse(cleaned.slice(start, end + 1))
  } catch {
    return null
  }
}

function fallbackPack(transcript) {
  const answers = transcript.map((t) => t.answer).filter(Boolean)
  const firstAnswer = answers[0] || 'their craft'
  return {
    title: `${firstAnswer.slice(0, 44)}${firstAnswer.length > 44 ? '…' : ''} — Knowledge Pack`,
    summary:
      answers.slice(0, 3).join(' ').slice(0, 320) ||
      'Interview notes captured. Claude was unavailable to summarize — read the full transcript below.',
    skills: [],
    experience_highlights: answers.slice(0, 5),
    stories: [],
    frameworks: [],
    monetizable_products: [],
    marketing_hook: 'Real expertise, captured straight from the source.',
    full_transcript: transcriptToText(transcript),
  }
}

export async function generatePack(transcript) {
  const prompt = `You are an expert knowledge extractor. Analyze this interview transcript and produce a structured Knowledge Pack as JSON with these fields:
- title: a compelling product title for this person's expertise
- summary: 2-3 sentence overview of their knowledge
- skills: array of {skill, level, description}
- experience_highlights: array of strings
- stories: array of {title, lesson}
- frameworks: array of {name, description}
- monetizable_products: array of {product_name, format, price_range, target_audience}
- marketing_hook: one-line hook for selling
- full_transcript: the complete Q&A as formatted text

Transcript:
${transcriptToText(transcript)}

Respond with ONLY the JSON object — no markdown fences, no commentary.`

  const result = await askClaude({
    model: 'claude-opus-4-8',
    max_tokens: 4096,
    system: 'You produce clean, valid JSON only. No prose, no markdown code fences.',
    messages: [{ role: 'user', content: prompt }],
  })

  if (result.ok) {
    const parsed = parsePackJSON(result.text)
    if (parsed) {
      return { ...parsed, full_transcript: parsed.full_transcript || transcriptToText(transcript) }
    }
  }
  return fallbackPack(transcript)
}

export async function sendToZapier(webhookUrl, pack, transcript) {
  if (!webhookUrl) return { ok: false, skipped: true }
  try {
    const res = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript_text: transcriptToText(transcript),
        pack_json: pack,
        source: 'rawvolt-extract',
        timestamp: new Date().toISOString(),
      }),
    })
    return { ok: res.ok }
  } catch {
    return { ok: false }
  }
}

export { transcriptToText }
