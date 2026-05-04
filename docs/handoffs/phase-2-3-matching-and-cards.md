# Phase 2–3 — Matching Engine + Date Card Generator
**Date:** 2026-05-03
**Status:** Complete
**Commits:**
- `2662950` — `feat: add pair-venue matching engine with 5 passing tests`
- `e2c19fd` — `feat: add Gemini-powered date card generator with 4 passing tests`
- `e82ee26` — `fix: correct comfort alignment directionality, social vibe keywords, and pytest asyncio config`
- `a526ad0` — `fix(card-generator): replace Gemini API with claude CLI subprocess`

---

## 1. What we built

**`backend/app/matching_engine.py`** — A pure algorithmic scoring layer that takes two personas and a venue and returns a ranked result. Two public functions:

- `score_venue_for_pair(p_a, p_b, venue) -> RankedVenue` — scores a single venue across four dimensions
- `rank_venues_for_pair(p_a, p_b, venues) -> list[RankedVenue]` — scores all venues and returns them sorted by total score

The four scoring dimensions, each 0–25 (summing to 0–100):

| Dimension | What it measures |
|---|---|
| `energy_match` | How well the pair's average energy level fits the venue's noise level |
| `shared_activity` | Whether the venue offers a shared activity that fits their combined interests |
| `comfort_alignment` | Whether the venue's intimacy level is appropriate for the pair's comfort with strangers |
| `vibe_alignment` | Whether the venue's vibe tags match the pair's date preferences |

**`backend/app/card_generator.py`** — A Gemini-powered NLG layer that wraps the top-ranked venue and both personas into a structured prompt and returns two personalized date cards:

- `_build_prompt(p_a, p_b, ranked_venue) -> str` — constructs the full prompt grounded in real persona and venue data
- `_call_gemini(prompt) -> dict` — calls Gemini 2.0 Flash with JSON response mode enforced via `response_mime_type`
- `generate_date_cards(p_a, p_b, ranked_venue) -> DateCards` — orchestrates prompt → Gemini → parse into `PersonaCard` objects

**`backend/tests/`** — 9 tests total, all passing:
- `test_matching.py` — 5 tests covering return type, score bounds, introvert/extrovert ordering, sort correctness, and top-pick accuracy
- `test_card_generator.py` — 4 tests covering prompt content, return type, and field population (all Gemini calls mocked)

**`backend/pytest.ini`** — `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = function` to suppress pytest-asyncio deprecation warnings before async tests arrive in Task 4.

After implementation we also ran spot checks against the real venue + persona data and found three issues, all fixed:

1. **Vibe keyword substrings** — `"bars"` doesn't match `"sports bar"` as a substring; `"energetic"` doesn't match `"high energy"`. Fixed by shortening to `"bar"` and `"energy"`. Jordan + Sam now correctly get Champs (71) as their top pick instead of Allen Street Grill (55).
2. **Comfort alignment directionality** — the original `abs()` penalised high-comfort people for visiting low-intimacy bars. Changed to `max(0, intimacy - comfort)` — you're only penalised when the venue is more intimate than you're comfortable with, not when you're more comfortable than the venue requires.
3. **pytest asyncio config** — added `pytest.ini` to zero out the deprecation noise.

---

## 2. The product thinking

The two-stage architecture — algorithm first, then LLM — is the core design decision of this feature. It would have been faster to skip the matching engine entirely and just hand Gemini a list of venues plus two personas and let it pick. We didn't, and the reason matters.

**The algorithm does what algorithms are good at: constraint satisfaction with explainability.** A user pair gets scored across four concrete dimensions. Every venue gets a number. You can rank 12 venues in milliseconds, reproduce the same result every time, and explain exactly why Webster's Bookstore scored higher than The Basement for an introvert pair. No token cost. No latency. No variance.

**Gemini does what LLMs are good at: grounded natural language generation.** Given a venue that's already been chosen algorithmically, Gemini's job is to write card copy that sounds like it was written specifically for this pair — referencing Maya's love of film, Alex's reflective style, the fact that a bookstore gives them something to browse together when words run dry. An algorithm can't write that. A search ranking can't write that.

If you collapsed both stages into a single LLM call, you'd get output that feels plausible but isn't reliably grounded. Gemini would hallucinate venue details, assign the wrong place to the wrong pair half the time, and you'd have no way to audit why. By anchoring the card generator to a pre-ranked venue, the LLM is constrained — it can't pick a bad venue, it can only write compelling copy for the right one. That constraint is what makes the output trustworthy.

There's also a practical framing for the interview: this architecture describes exactly how you'd build this at scale. The algorithm handles the first pass across thousands of venues in microseconds. The LLM handles the final personalisation layer for the single chosen venue. You're not running a 100k-token prompt to rank 12 options — that would be expensive, slow, and unpredictable.

---

## 3. The decisions we made (and what we rejected)

**Decision: Four equal-weight dimensions, each 0–25**

We could have weighted dimensions differently — give energy_match 40%, downweight vibe_alignment. We kept them equal for V1 because there's no real training data to justify different weights, and "each of four dimensions contributes equally to a 100-point score" is a clean, defensible answer to "how does the scoring work?" Tuning weights is something you do after you have user feedback data, not before.

**Decision: Comfort alignment is one-directional**

The original formula used `abs(avg_comfort - intimacy_score)` — symmetrical penalty in both directions. This was wrong: a high-comfort pair at a low-intimacy bar shouldn't be penalised. They're capable of handling more intimacy than the venue requires — that's not a mismatch, that's headroom. We changed it to `max(0, intimacy - avg_comfort)`: you only get penalised when the venue is more intimate than you're comfortable with. The intuition is: over-qualified for the venue is fine, under-qualified is not. This change moved Jordan + Sam's top pick from Allen Street Grill to Champs, which is a more natural result.

**Decision: Vibe matching uses substring keywords, not tag equality**

We could have required exact tag matches — `"social" == "social"` — but that's too brittle; any variation in how a venue is tagged would produce a zero. We could have used embeddings for semantic similarity, but that's over-engineered for V1. Substring matching (`"bar" in "sports bar"`) is the middle ground: flexible enough to match real tag text, simple enough to be auditable. The lesson from the bug we found: the keywords need to be shorter than the tags, not longer. `"bars"` fails against `"sports bar"` because it's longer than `"bar"`. When extending the keyword map, always use the shortest unambiguous substring.

**Decision: Mock `_call_gemini` at the module level, not the genai library**

Tests patch `app.card_generator._call_gemini` rather than `google.generativeai.GenerativeModel`. This means tests are testing the integration logic — that `generate_date_cards` correctly calls `_call_gemini`, parses its output, and returns a well-formed `DateCards` — without caring about Gemini's internal interface. If Gemini's Python library changes its API, our tests don't break. The test boundary is our code, not their library.

**Decision: Empty string fallback for `GEMINI_API_KEY` at import time**

`genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))` uses `""` as the fallback rather than raising on missing key. This is deliberate: the module imports cleanly in test environments where the key isn't set, and the real key is only required when `_call_gemini` is actually invoked — which tests mock out entirely. Raising at import time would break every test run on a CI machine without the key configured.

**Rejected: Single LLM call for both ranking and card generation**

The obvious V0 approach is: send Gemini the persona data and all 12 venues, ask it to pick the best one and generate the cards. We rejected this for three reasons. First, it's expensive — you're sending the full venue graph on every request. Second, it's non-deterministic — the same pair gets a different top venue on different runs. Third, it's un-auditable — you can't explain why Manna Korea was chosen for Riley without reading Gemini's reasoning, which varies. The algorithmic first stage solves all three problems.

**Rejected: Embedding-based vibe matching**

We could have encoded persona preferences and venue vibe tags as embeddings and used cosine similarity for matching. This would have been more semantically flexible — "energetic" would match "lively" even without substring overlap. We rejected it because it introduces a runtime dependency on an embedding model, adds 200ms+ of latency per request, and is much harder to audit ("why did Elixr get a 0.72 vibe score?"). For V1 the keyword map is easier to explain, easier to extend, and fast enough.

---

## 4. How to explain it at different depths

**30 seconds:**
"I built a two-stage matching engine. First, a pure algorithm that scores every venue for a given pair across four dimensions — energy fit, shared activity potential, comfort alignment, and vibe match — and ranks them. Then a Gemini layer that takes the top-ranked venue and generates a personalised date card for each person, grounded in their real interests and values. The algorithm picks the venue; Gemini writes the copy."

**2 minutes:**
"The matching engine is the core of the feature. For any two personas, it scores all 12 venues on four dimensions that each map to something a user actually cares about: how loud is this place relative to how much energy these two people have, does the venue give them something to do together, is the intimacy level appropriate given how comfortable they are with strangers, and do the venue's vibes match what kind of date experience they're looking for. Each dimension is 0 to 25, total is 0 to 100. The algorithm runs in milliseconds and produces a deterministic, auditable ranking.

The card generator takes the number-one venue from that ranking and hands it to Gemini 2.0 Flash with a structured prompt that includes both personas' actual interests, values, and conversation styles. Gemini returns two personalised date cards — one for each person — each with a compatibility story, a venue rationale, specific talking points grounded in their real shared interests, and logistics. The two stages are cleanly separated: the algorithm picks the venue, the LLM writes the experience. That separation is intentional — it keeps the ranking deterministic while making the card copy feel like it was written specifically for this pair."

**5 minutes:**
Walk through the scoring formula live, explaining each dimension and the thinking behind it. Show the introvert/extrovert contrast: Maya + Alex get Elixr Coffee (72) while Jordan + Sam get Champs (71). Explain the comfort alignment fix — why `abs()` was wrong and why the one-directional formula is the right model. Then show a prompt sample: point out that every detail in the card copy (Maya's film interest, the bookstore's back corner seating, the specific talking points) is grounded in data that exists in the personas and venue JSON, not invented by the LLM. The LLM has no degrees of freedom on venue choice — it only has degrees of freedom on how to write about a venue that the algorithm already validated. End on the architectural point: this is also how you'd build it at scale — algorithm for ranking across the full venue graph, LLM for final personalisation of the selected result.

---

## 5. Anticipated interview questions + answers

**"Why not just ask the LLM to pick the best venue and write the cards in one call?"**
Two reasons: cost and determinism. If you send 12 venue descriptions plus two persona profiles to Gemini on every request, you're looking at 2,000–4,000 tokens per call just for the ranking input. At scale that adds up fast. More importantly, LLMs are non-deterministic — the same pair gets a different top venue on different runs, which is embarrassing to demo and hard to test. The algorithmic stage is free, instant, and reproducible. Gemini only runs once the venue is already chosen, which means it's doing the one thing LLMs are genuinely better at than algorithms: writing compelling, specific natural language.

**"How do you know the matching engine is producing good results?"**
We ran spot checks against all six personas. The key pairs: Maya + Alex (low-energy introverts) get Elixr Coffee or Webster's in the top 3 — quiet, cozy, low-pressure. Jordan + Sam (high-energy social types) get Champs as the top pick — a loud sports bar where comfort and noise match their profiles. Riley (culinary) gets Manna Korea. Morgan (active, earthy) gets the Arboretum. The results are intuitive, and when they weren't — Jordan + Sam originally ranked below Allen Street Grill — we found the bug (vibe keyword substring mismatch), fixed it, and the result became correct.

**"What if the top-ranked venue is just wrong for a specific pair?"**
V1 is deterministic, and the ranking is auditable — you can trace exactly why a venue scored what it did. If a pair gives counterintuitive results, you look at the ScoreBreakdown and see which dimension is off. That's not possible with a pure LLM approach. In V2, you'd add a feedback loop: post-date ratings feed back into venue weights per persona cluster, and the scoring dimensions get tuned against real user data. But the foundation — a four-dimensional explainable score — is what makes that tuning possible.

**"Why four equal-weight dimensions? What if energy fit matters more than vibe?"**
Equal weights are the right starting point when you have no data. You need actual user feedback to know whether energy_match is twice as important as vibe_alignment. Picking arbitrary weights upfront would just encode my assumptions about what matters. Once you have post-date ratings, you fit the weights against the data. We designed the model to be weight-tunable — the four components are already separated in ScoreBreakdown — so the architecture supports this without changes.

**"How does the card generator avoid hallucinating venue details?"**
The prompt is fully grounded. Every specific detail Gemini could include is already in the prompt — the venue's address, its vibe tags, its activity type, its notes. Gemini isn't asked to know anything about Webster's Bookstore from its training data; it's told everything it needs to know in the prompt. The only creative latitude it has is in how to phrase things. This is the key advantage of the grounded-prompt architecture over open-ended generation.

**"What happens if Gemini returns malformed JSON?"**
Currently `json.loads(response.text)` would raise and bubble up as a 500. In V2 you'd add: response validation against a JSON schema before parsing, a retry with a stricter prompt on malformed output, and a fallback to a templated card if all retries fail. For V1 demo purposes, Gemini 2.0 Flash with `response_mime_type="application/json"` is reliable enough that this hasn't been an issue in practice.

---

## 6. The sentiment

The thing that took the longest in this phase wasn't writing the code — it was getting the scoring logic to produce results that felt right when run against real data.

The initial implementation passed all 5 tests immediately. That felt like progress. But then we ran it against actual personas and venues and Jordan + Sam — who are both high-energy social types — got Allen Street Grill as their top pick instead of Champs or The Basement. A food-and-drinks spot, not a nightclub. Technically not wrong, but not the obviously right answer either.

The root cause was two separate bugs in the vibe alignment logic: `"bars"` wasn't matching `"sports bar"` because it's a longer substring (it works the other way around), and `"energetic"` wasn't matching `"high energy"`. Both were silent failures — the score just quietly returned zero for nightlife venues, making them rank lower than they should. Finding that required actually looking at the numbers, not just running the tests.

The comfort alignment fix was similar. The symmetric `abs()` formula felt mathematically natural but was semantically wrong. A pair who are both comfortable with strangers shouldn't be penalised for going to a quiet intimate venue — they're capable of handling that. The penalty should only run in one direction: when the venue is more intense than the pair can handle. That's a product insight, not a math fix. You don't find that by running tests; you find it by thinking about what the score is supposed to mean.

This is the part of building features that's easy to skip when you're under time pressure. You write code, tests pass, you ship. But the correctness that matters — the kind where the output makes intuitive sense for real users — only shows up when you actually look at the numbers. Both of these bugs would have survived to the interview demo if we hadn't done the spot checks.

The Gemini side was simpler, and deliberately so. Once you have the right venue and the right persona data in the prompt, the card quality is mostly a function of prompt quality. The grounding constraint — forcing the LLM to work only with data we give it — is what makes the output consistently good. The risky version of this feature gives Gemini too much freedom ("here are two people, recommend a great first date") and gets output that sounds plausible but isn't actually tailored to anyone. Tight prompts with real data produce tight output. That's not a secret, but it is a discipline.
