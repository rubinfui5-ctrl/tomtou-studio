export async function askClaude({ messages, system, model, max_tokens }) {
  try {
    const res = await fetch('/.netlify/functions/claude', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, system, model, max_tokens }),
    })
    const data = await res.json()
    if (!res.ok || data?.error === 'fallback') {
      return { ok: false, text: '', raw: data }
    }
    const text = (data?.content || []).map((b) => b.text || '').join('\n')
    return { ok: true, text, raw: data }
  } catch (err) {
    return { ok: false, text: '', error: err.message }
  }
}
