# Phase 8 — Scoring Fix + Cache-First API

**What I built:** Three things. First, a scoring bug fix: Allen Street Grill was the top pick for 18 of 30 persona pairs when it should have been the top pick for 4. Second, a precomputed cache for all 30 ordered persona pairs, served by a cache-first API pattern in `main.py`. Third, a migration from a `subprocess` Claude CLI call to the official Anthropic Python SDK.

---

## The Allen Street Grill Bug

After generating all 30 precomputed pairs, I noticed Allen Street Grill was winning for 60% of pairings — including many where it was clearly wrong. Riley and Alex, who share cooking and Korean culture interests, were being routed to a generic upscale grill instead of Manna Korean BBQ.

The root cause was two separate issues:

**1. Vibe tags too broad.** Allen Street's tags — `["upscale-casual", "lively", "quality food", "corner spot", "social"]` — were triggering multiple preference types through substring matching. `"casual"` inside `"upscale-casual"` fired for low-pressure personas. `"food"` inside `"quality food"` fired for culinary personas. `"social"` fired for social personas. It was collecting vibe points from personas with completely different date preferences. Fixed: tags narrowed to `["upscale", "lively", "farm-to-table", "food-forward", "corner spot"]`.

**2. Activity scorer missing "cook" keyword.** Manna's activity description says "cooking and building hot pot together at the table." The scorer only triggered on `"food"` in the description — not `"cook"`. So culinary-interest personas got no activity credit at Manna. One-line fix: extend the check to also trigger on `"cook"`.

After the fix: Allen Street wins 4 pairs. Manna wins 12. Elixr wins 6. The Phyrst wins 6. Champs wins 2.

**Why I kept the v1 precomputed files instead of deleting them:** The `v1/` folder shows what the output looked like before the fix. A reviewer can open any v1 file, compare it to the current version, and see exactly what changed and why. Deleting the old files would have been cleaner but less honest about how the system developed. Iteration is the story.

---

## Cache-First API

The 30 persona pairs are fixed. Calling the Anthropic API on every request adds 3–5 seconds of latency and costs money for identical output. Precomputing trades a one-time generation cost for instant, deterministic responses.

The fallback chain in `main.py`:
1. Cache hit → return immediately (always the case for the 30 demo pairs)
2. Cache miss + `ANTHROPIC_API_KEY` set → run the scoring engine and generate fresh cards via the SDK
3. Cache miss + no key → 503 with `"No cached result for this pair and ANTHROPIC_API_KEY is not set."`

The 503 with a clear message is a deliberate product decision. The alternative — a generic 500 or a partial response — hides the actual problem. A specific message tells whoever is running the server exactly what's missing and why.

---

## Anthropic SDK Migration

The original `card_generator.py` used `subprocess.run(["claude", "-p", ...])`. This requires the Claude CLI to be installed and authenticated on the host machine — a hidden system dependency that breaks on any machine without it. The Anthropic Python SDK is a declared dependency in `requirements.txt`: it shows up, it installs with `pip`, it authenticates via an environment variable. That's the correct way to integrate with the API and what a hiring engineer would expect to see.

The swap was transparent to the test suite — `test_card_generator.py` already patches `_call_claude` at the function level, so the subprocess-to-SDK change didn't require a single test update.

**`anthropic>=0.40.0` floor-pinned, not exact.** The rest of the dependencies are pinned exactly. The Anthropic SDK is a fast-moving library and any version above 0.40.0 supports the `client.messages.create()` interface we use. Pinning to an exact version would create unnecessary friction for anyone running this months from now.
