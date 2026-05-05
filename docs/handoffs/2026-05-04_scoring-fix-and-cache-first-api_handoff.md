# Phase 8 Handoff — Scoring Fix + Cache-First API

**Date:** 2026-05-04
**Phase:** 8 — Scoring engine fix, precomputed cache, Anthropic SDK migration
**Status:** Complete
**Commits:**
- `TBD` — `fix: correct allen street grill vibe tags and add cook activity signal`
- `TBD` — `feat: cache-first api with anthropic sdk, drop claude cli dependency`

---

## 1. What Was Done

Three things shipped in this phase:

**Allen Street Grill scoring fix**
After generating all 30 precomputed pairs, we noticed Allen Street Grill was winning for 18 of 30 pairings — including many where it was clearly the wrong pick (e.g., Riley + Alex, who share cooking and Korean culture interests, routing to a generic upscale grill instead of Manna Korean BBQ). Root cause was two separate issues: (1) Allen Street's vibe tags (`"upscale-casual"`, `"quality food"`, `"social"`) were broad enough to substring-match the `low_pressure`, `culinary`, and `social` preference keywords simultaneously, making it a default catch-all. (2) The activity scorer only fired on `"food"` in the activity description — Manna's description says "cooking and building hot pot together at the table," which contains "cook" but not "food", so culinary-interest personas got no activity credit there.

Fix: two targeted changes. In `venues.json`, Allen Street's vibe tags narrowed from `["upscale-casual", "lively", "quality food", "corner spot", "social"]` to `["upscale", "lively", "farm-to-table", "food-forward", "corner spot"]` — it still correctly scores for culinary and social pairs, but no longer bleeds into low_pressure. In `matching_engine.py`, the food activity signal extended from `"food" in activity_keywords` to `("food" in activity_keywords or "cook" in activity_keywords)`. After the fix: Allen Street wins 4 pairs (down from 18), Manna wins 12, Elixr wins 6, The Phyrst wins 6, Champs wins 2.

**Precomputed cache + archival**
The 14 pairs whose top venue changed were not deleted — they were moved to `app/data/precomputed/v1/` before regeneration. The v1 folder shows the before state of the scoring engine and documents the iteration. The 14 corrected files were regenerated using `claude sonnet --effort low` via the existing `scripts/precompute_responses.py` script. All 30 ordered pairs are now current.

**Cache-first API + Anthropic SDK migration**
`card_generator.py` replaced `subprocess.run(["claude", "-p", ...])` with the official `anthropic` Python SDK. `main.py` gained a `_load_from_cache()` function that checks `app/data/precomputed/{a_id}__{b_id}.json` before doing any computation. If the file exists, it deserializes and returns it immediately — no scoring, no LLM call. If no cache hit and `ANTHROPIC_API_KEY` is set, it falls back to live generation. If neither, it returns a 503 with a clear message. For the 6 demo personas (30 pairs), the cache always hits. `python-dotenv` is now called at startup so `.env` is loaded automatically. `requirements.txt` gained `anthropic>=0.40.0`. `.env.example` updated from `GEMINI_API_KEY` to `ANTHROPIC_API_KEY`.

**Tests**
All 25 tests pass. No test changes required — `test_card_generator.py` already patches `_call_claude` at the function level, so the subprocess-to-SDK swap was transparent to the test suite.

---

## 2. The Product Thinking

**Why fix the scoring at all?** The Allen Street Grill dominance wasn't a subtle edge case — it was winning for 60% of pairs. For a demo built around the idea that the engine makes *specific, reasoned picks*, routing Riley (who cooks Korean food at home and loves trying new restaurants) to a generic upscale grill is the wrong signal. The whole point of the compatibility story in the date card is that the venue feels *chosen*. That story falls apart if the venue is a default.

**Why archive v1 instead of deleting?** The v1 folder is a paper trail of a real product decision: we noticed the scoring was wrong, diagnosed it, fixed it, and kept the evidence. That's a more honest representation of how software actually gets built than a clean git history that pretends the first version was correct. A hiring engineer looking at the repo can see the iteration, not just the outcome.

**Why cache-first instead of API-first?** The demo runs the same 30 pairs every time. Calling the API on each request adds 3–5 seconds of latency and costs money for identical output. Precomputing trades a one-time generation cost for instant, deterministic responses. It also makes the app runnable with zero configuration — clone, install, run. The Anthropic SDK is still in the codebase so the architecture is legible: this is how live generation would work if you wired up an API key.

**Why drop the subprocess entirely?** `subprocess.run(["claude", "-p", ...])` requires the Claude CLI to be installed and authenticated on the machine running the server. That's a hidden system dependency that breaks on any machine without it. The Anthropic SDK is a declared Python dependency — it shows up in `requirements.txt`, installs with `pip install`, and authenticates via an environment variable. It's the correct way to integrate with the API and it's what a hiring engineer would expect to see.

---

## 3. The Decisions We Made (and What We Rejected)

**Decision: fix both the data and the algorithm, not just one**

Option A (data-only): tighten Allen Street's tags without touching the algorithm. Would fix the symptom but leave the scorer vulnerable to the same problem with any future venue that has broad tags.

Option B (algorithm-only): tighten the substring matching in `_vibe_alignment_score`. Would fix the structural issue but leave Allen Street's tags semantically inaccurate (it really isn't a "social" bar or a venue for people seeking "casual" low-pressure energy — it's a farm-to-table upscale grill).

Option C (both): fix the tags to be accurate AND extend the activity keyword to recognize "cook". Each change is independently justified. This is what we shipped.

**Decision: cache-first, not API-first-with-cache-fallback**

The alternative was: always try the API first, fall back to cache on failure. Rejected because (1) it would require an API key for the demo to work at all, (2) it adds latency to every request, and (3) the fallback-on-error pattern hides the fact that the cache is the intended path. Cache-first makes the architecture honest: precomputed results are the primary data source, live generation is the extension path.

**Decision: 503 with a clear message when no cache and no key**

The alternative was to silently return a partial response (just the scoring, no cards) or raise a generic 500. The 503 with `"No cached result for this pair and ANTHROPIC_API_KEY is not set."` is more honest — it tells whoever is running the server exactly what's missing and why, without pretending something partially succeeded.

**Decision: `anthropic>=0.40.0` as a floor, not a pinned version**

The rest of the dependencies are pinned exactly (FastAPI, uvicorn, pydantic). The Anthropic SDK is floor-pinned because it's a fast-moving library and any version above 0.40.0 supports the `client.messages.create()` interface we use. Pinning to an exact version would create unnecessary friction for anyone running this months from now.

---

## 4. How to Explain It at Different Depths

**30 seconds:**
"I noticed the matching engine was routing 18 of 30 persona pairs to the same venue — Allen Street Grill was acting as a catch-all because its tags were too broad and the activity scorer had a keyword gap. I fixed the tags and extended the activity keyword, re-ran the affected precomputed pairs, and archived the old results in a v1 folder so the iteration is visible. I also swapped the Claude CLI subprocess out for the official Anthropic Python SDK and made the API serve from the precomputed cache, so the app runs with no external dependencies."

**2 minutes:**
"The scoring fix was two changes. First, Allen Street's vibe tags included 'social', 'upscale-casual', and 'quality food' — the substring matching in the vibe scorer was finding 'social' for social-preference personas, 'casual' inside 'upscale-casual' for low-pressure personas, and 'food' inside 'quality food' for culinary personas. It was picking up three preference types when it should pick up one. I narrowed the tags to 'upscale', 'lively', 'farm-to-table', 'food-forward', 'corner spot'. Second, Manna's activity description says 'cooking and building hot pot together' — the activity scorer only fired on 'food' in the description, so Riley (who lists 'cooking' as an interest) got no credit for the cooking activity at Manna. One-line fix: extend the check to also trigger on 'cook'.

For the API: the subprocess approach required Claude CLI installed and authenticated on the host machine. That's a hidden system dependency. The Anthropic SDK is declared in requirements.txt, installs with pip, and reads ANTHROPIC_API_KEY from the environment. The API now checks the precomputed cache first — instant response for any of the 30 demo pairs — and only falls through to the SDK if there's a cache miss and an API key is set."

**5 minutes:**
Walk through `matching_engine.py` — show the `_shared_activity_score` function and the `overlap_signals` list. Explain the food/cook keyword gap. Show `_vibe_alignment_score` and the substring matching loop — explain why `"casual" in "upscale-casual"` fires for a venue that isn't low-pressure. Show the old vs new vibe tags for Allen Street. Open `app/data/precomputed/v1/` — explain why the old files are there. Show `main.py`'s `_load_from_cache()` function and the fallback chain. Show `card_generator.py`'s `_call_claude()` — the SDK call, the JSON extraction. End on the architecture point: the precomputed cache is not a hack, it's the right design for a fixed persona set. The SDK integration shows what live generation looks like. The 503 message shows what happens when neither path is available.

---

## 5. Anticipated Interview Questions + Answers

**"Why was Allen Street Grill winning so often?"**
Two reasons. Its vibe tags were broad enough to match multiple preference types through substring matching — 'upscale-casual' contains 'casual' (low_pressure signal), 'quality food' contains 'food' (culinary signal), 'social' directly matches social preference. It was getting vibe points from personas with completely different date preferences. Separately, its `noise_level=3` and `intimacy_score=3` put it dead center on both scoring dimensions, so it almost never got penalized on energy or comfort while more intimate or quieter venues did. The fix was to make its tags semantically accurate and extend the activity scorer to recognize the cooking keyword at Manna, which made Manna the correct pick for culinary-interest pairs.

**"Why precompute instead of calling the API at runtime?"**
The persona set is fixed — 6 personas, 30 ordered pairs, same output every time. Calling Claude on each request adds 3–5 seconds of latency and API cost for identical results. Precomputing trades a one-time generation cost for instant, zero-dependency responses. The `scripts/precompute_responses.py` script makes the process repeatable — if the persona data changes or the scoring logic changes, you delete the affected files and re-run. The architecture is also honest about what's happening: the precomputed files are the primary data source, they're in version control, and they're human-readable JSON.

**"How does the fallback chain work?"**
Cache hit → return immediately. Cache miss + `ANTHROPIC_API_KEY` set → run the scoring engine and generate fresh cards via the SDK. Cache miss + no key → 503 with a descriptive message. For the 30 demo pairs, you always hit the cache. The SDK path is there so the code reads correctly and so the system extends naturally if you add new personas.

**"Why keep the v1 precomputed files?"**
They document a real iteration. The first version of the scoring engine had a bias problem — one venue dominated. The v1 folder shows what the output looked like before the fix. A reviewer can open any v1 file, compare it to the current version, and see exactly what changed and why. Deleting the old files would have been cleaner but less honest about how the system developed.

---

## 6. The Sentiment

The Allen Street Grill bug was satisfying to find and fix because it was a structural issue masquerading as a data quirk. The substring matching in the vibe scorer is genuinely useful — it avoids having to maintain an exact vocabulary mapping — but it's also the kind of thing that creates surprising behavior when venue tags are phrased loosely. The fix didn't require changing the architecture, just making the tags accurate and extending one keyword check. Two lines of code changed, 14 precomputed pairs updated.

The SDK migration was overdue. The subprocess approach was a pragmatic early shortcut — Claude CLI was the fastest path to working output during development — but it was always a system dependency that didn't belong in production code. The Anthropic SDK is what a real integration looks like, and switching to it also meant the cache-first design fell out naturally: once you're not shelling out to a CLI tool, it's obvious that you'd want to serve precomputed results for a fixed persona set rather than make an API call on every request.
