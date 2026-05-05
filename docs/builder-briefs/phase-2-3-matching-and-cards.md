# Phase 2–3 — Matching Engine + Date Card Generator

**What I built:** Two modules that form the core intelligence of the app. `matching_engine.py` is a pure algorithmic scorer — it takes two personas and all 12 venues, scores each venue across four dimensions, and returns a sorted ranked list. `card_generator.py` takes the top-ranked venue and both personas, builds a grounded prompt, and calls the Anthropic API to generate two personalized date cards (one per person).

**The two-stage architecture:** This was the most deliberate system design decision in the project. It would have been faster to skip the matching engine and ask an LLM to pick the best venue and write the cards in a single call. I didn't do that, and the reason matters.

The algorithm does what algorithms are good at: **constraint satisfaction with explainability.** 12 venues scored across 4 dimensions, ranked in milliseconds, same result every time, auditable at the dimension level. The LLM does what LLMs are good at: **grounded natural language generation.** Given a venue that's already been chosen deterministically, Claude's job is to write card copy that sounds like it was written specifically for this pair — referencing Maya's love of indie film, Alex's reflective conversation style, the fact that a coffee shop gives them a low-pressure environment to talk.

If you collapse both stages into one LLM call, you get output that sounds plausible but isn't reliably grounded. The LLM might pick the wrong venue, and you have no way to audit why. By anchoring the card generator to a pre-ranked venue, the LLM can only write compelling copy for the right pick — it can't choose a bad one. That constraint is what makes the output trustworthy.

**The four scoring dimensions (each 0–25):**
- `energy_match` — does the venue's noise level fit the pair's average energy?
- `shared_activity` — does the venue give them something to DO together?
- `comfort_alignment` — is the venue's intimacy level appropriate for how comfortable they are with strangers?
- `vibe_alignment` — do the venue's vibe tags match their date preference type?

**Key decisions:**
- **Comfort alignment is one-directional.** The first implementation used `abs(avg_comfort - intimacy)` — symmetric penalty. This was wrong: a high-comfort pair at a low-intimacy venue shouldn't be penalized. They're capable of handling more intimacy than the venue requires. Fixed to `max(0, intimacy - avg_comfort)`: penalty only runs when the venue is more intense than the pair can handle. Over-qualified is fine; under-qualified is not. This one change moved Jordan + Sam's top pick from Allen Street Grill to Champs.
- **Vibe matching uses substring keywords, not exact tag equality.** Exact matching is too brittle; embeddings are over-engineered for V1. Substring matching (`"bar" in "sports bar"`) is the middle ground — flexible, auditable, fast. Critical lesson from a bug: keywords must be *shorter* than the tags, not longer. `"bars"` fails against `"sports bar"`; `"bar"` works.
- **Mock `_call_claude` at the module level, not the Anthropic library.** Tests are testing whether `generate_date_cards` correctly calls `_call_claude` and parses its output — not Anthropic's internal interface. If their library changes its API, tests don't break. The test boundary is our code, not their library.

**What I rejected:**
- **Single LLM call for ranking + card generation.** Expensive (full venue graph on every request), non-deterministic (same pair gets different top venue on different runs), un-auditable. Three reasons to avoid it.
- **Embedding-based vibe matching.** More semantically flexible, but adds an embedding model runtime dependency, 200ms+ latency per request, and is much harder to audit. Keyword matching wins for V1.

**Pivot:** Tests passed immediately. But spot-checking against real personas revealed Jordan + Sam were getting Allen Street Grill (a food-and-drinks spot) when both are high-energy social types who should go to Champs (a sports bar). Root cause: two separate bugs in the vibe alignment logic — substring direction error, and comfort formula directionality. This is the part easy to skip under time pressure: write code, tests pass, ship. The correctness that matters only shows up when you look at the actual numbers.
