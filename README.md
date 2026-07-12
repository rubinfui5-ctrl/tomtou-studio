# The Standard — RAWVOLT

A PWA for the RAWVOLT brand: "Locked like your word."

## Modules

1. **STANDARD** — daily non-negotiables tracker. Set up to 7 standards, tap them done, watch the voltage bar fill. At 100% the day locks — no un-ticking. Tracks streak, best streak, and 7-day history.
2. **GUIDE** — voice layer built on the browser's `speechSynthesis`. Two personas, TOM and TOU. Spoken app tour, voice-led box breathwork (4-4-4-4), and a voice-encouragement toggle.
3. **EXTRACT** — voice interviewer. Consent screen → 10 adaptive questions (mic input via `webkitSpeechRecognition`, text fallback) → Claude-generated structured Knowledge Pack (skills, stories, frameworks, monetizable products) → saved locally and optionally POSTed to a Zapier webhook.

## Stack

- Vite + React 18, no CSS framework — brand tokens and layout live in `src/styles.css`.
- `netlify/functions/claude.js` proxies Claude API calls so the API key never reaches the browser.
- `public/manifest.json` + `public/sw.js` make it installable and usable offline.
- All state persists to `localStorage` — no backend.

## Local development

```bash
npm install
npm run dev
```

The Claude proxy only works when deployed to Netlify (or run via `netlify dev`) with `ANTHROPIC_API_KEY` set — outside of that, EXTRACT gracefully falls back to the scripted seed questions and a locally-assembled Knowledge Pack.

## Deploy

1. Connect the repo to Netlify (build command `npm run build`, publish directory `dist`).
2. Set the `ANTHROPIC_API_KEY` environment variable in Netlify.
3. Paste your Zapier Catch Hook URL into `ZAPIER_WEBHOOK_URL` in `src/lib/config.js` to enable auto-send of Knowledge Packs.
