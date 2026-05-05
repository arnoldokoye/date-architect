# Phase 6 Handoff — Demo Polish

**Date:** 2026-05-04
**Phase:** 6 — End-to-end demo polish
**Status:** Complete

---

## 1. What Was Done

- **README.md** — rewrote from stub to full doc: one-sentence description, ASCII architecture diagram, exact run commands for both servers, example output table (Maya+Alex → Elixr Coffee, 72/100).
- **layout.tsx metadata** — confirmed title was already `"Date Architect — Ditto AI"` from Phase 5; no change needed.
- **Demo script** — produced in handoff (below) as a verbatim 5-minute walkthrough for the Ditto interview.

---

## 2. Files Changed

| File | Change |
|------|--------|
| `README.md` | Full rewrite — description, architecture ASCII, run commands, example output |
| `docs/handoffs/phase-6-demo-polish.md` | This file |

No source code changes. All logic was complete from Phase 5.

---

## 3. System State

- Backend: FastAPI on `localhost:8000`, `POST /generate-date-plan`
- Frontend: Next.js on `localhost:3000`
- Claude CLI: used by `card_generator.py` for personalized card generation
- Personas: maya, alex, jordan, sam, riley, morgan
- Venues: 12 State College locations with full scoring metadata
- Tests: backend pytest suite passes

---

## 4. Known Issues / Gotchas

- `card_generator._call_gemini()` is named after Gemini but calls `claude -p` — cosmetic naming artifact from early dev, not a bug.
- First request after cold start takes ~5–10s (Claude CLI subprocess + model load). Expected.
- Jordan+Sam both have `social` date_preference; The Basement and The Phyrst score similarly (~65). Either is a reasonable demo output.

---

## 5. What the Next Agent Should Do

- If demoing: run `uvicorn app.main:app --reload` and `npm run dev` in two terminals, open `localhost:3000`.
- If extending: the clearest next feature would be a "Why this score?" expandable section in the DateCard that surfaces the raw breakdown reasoning.

---

## 6. Demo Day Script

See the **Demo Day Script** section in the parent session output. The verbatim script is reproduced below for completeness.

### 5-Minute Ditto Interview Walkthrough

---

**[0:00 — Opening, 30 seconds]**

"I built Date Architect — a persona-aware date planning engine. The core idea is that Ditto already knows a lot about each user: their energy level, conversation style, interests, comfort with new people. I wanted to see what happens if you use that profile data not just for matching people together, but for deciding *where* they should go and *what* they should say when they get there."

---

**[0:30 — Architecture overview, 60 seconds]**

"The system has two stages and that's intentional. Stage one is a deterministic four-dimension scorer — pure Python, no LLM, runs in milliseconds. It scores every venue against the pair on energy match, shared activity, comfort alignment, and vibe alignment. Each dimension is 0–25 and they sum to 100. This means the venue selection is explainable and reproducible — I can tell you exactly why Elixr Coffee beat Webster's for this pair.

Stage two is Claude. Once we know the top venue, I send both persona profiles and the venue context into Claude CLI and ask it to generate two personalized date cards — one per person, each with a compatibility story, venue rationale, three specific talking points, and practical logistics. The talking points are the interesting part: they're grounded in the pair's *actual* overlapping and complementary interests, not generic icebreakers."

---

**[1:30 — Live demo, 90 seconds]**

*[Click: select Maya and Alex, click "Find Our Date"]*

"Maya is low-energy and thoughtful — reads philosophy, loves indie film. Alex is similar energy, reflective, into craft beer and hiking. The engine scores Elixr Coffee highest: 72 out of 100. Notice the breakdown — energy match is a perfect 25 because both are quiet people and a coffee shop noise level matches their average energy exactly. Comfort alignment is 23 because the venue isn't more intimate than they can handle. Activity score is lower because it's a conversation-forward venue with no structured activity, but for this pair that's actually fine — they'll talk.

Now look at Maya's talking points: these are specific to *her* interests and *his* interests. Not 'what do you do for fun.' Grounded questions about the actual overlap between film philosophy and hiking or history."

*[Click: switch to Jordan and Sam, click "Find Our Date"]*

"Jordan and Sam — both high energy, social, comfortable with strangers. The engine routes them to The Basement: a Latin dance night. Score drops to 65 — the activity bonus is lower because neither listed 'dancing' explicitly in their interests, but the energy match is nearly perfect and comfort is maxed out. Claude generates completely different cards here: the tone is looser, the talking points are about being out in the scene together, the logistics mention arriving after 10pm."

---

**[3:00 — Architecture trade-off, 60 seconds]**

"The reason I separated scoring from generation is cost and reliability. If I sent every persona pair straight to an LLM and asked 'pick a venue and explain why,' I'd get plausible-sounding but unverifiable outputs. Venue selection would drift based on how the prompt was phrased. With the two-stage design, the venue choice is auditable — I can unit test it, I can debug it, I can explain it to a user. The LLM only touches the parts that genuinely need language: narrative, empathy, tone. That's a pattern I'd apply across any feature in a dating product."

---

**[4:00 — Q&A prep, 60 seconds]**

*Three likely interview questions and how to answer them:*

**Q: "How would this scale to real users with real profile data?"**
> "The scoring engine is already parameterized off the persona schema — swap in real Ditto profiles and it works immediately. The venue catalog would grow and we'd want a retrieval step rather than scoring all venues, but the architecture is the same. The Claude prompt is also templated, so richer profile fields (love language, dealbreakers) just become additional context lines."

**Q: "What would you do differently if you had more time?"**
> "The activity overlap signals in the scorer are hand-coded keyword rules. A cleaner version would embed interests and venue activity types and use cosine similarity. I kept it deterministic here so the logic was transparent and testable, but for production I'd replace that dimension with a learned similarity model."

**Q: "Why Claude instead of GPT or Gemini for the cards?"**
> "Honest answer: I use Claude CLI locally and it was the fastest path to working output. The card generation prompt is model-agnostic — any instruction-following model would work. What matters more than the model choice is the prompt structure: I ask for JSON output with exact field names, strip markdown fences, and parse strictly. That's the reliability work, not the model selection."

---

*End of script. Total runtime ~5 minutes at a comfortable speaking pace.*
