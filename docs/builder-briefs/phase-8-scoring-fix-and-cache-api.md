# Phase 8 — Scoring Fix + Cache-First API

Three things in one phase.

## The Allen Street Grill problem

I generated all 30 precomputed pairs and ran a distribution check. Allen Street Grill was the top pick for 18 of 30 pairings — 60% of the time. For a venue that should win for food-forward confident pairs, that's obviously wrong. Riley and Alex, who share Korean culture and cooking interests, were being routed there instead of Manna Korean BBQ.

Two separate bugs caused it.

First: Allen Street's vibe tags included `"quality food"` and `"social"` — broad enough to substring-match culinary *and* social preference types through the scorer. It was collecting vibe points from personas with completely different date preferences. The fix was making the tags semantically accurate: `["upscale", "lively", "farm-to-table", "food-forward", "corner spot"]`. It still wins for culinary/social pairs but stops bleeding into low-pressure preferences.

Second: Manna's activity description says "cooking and building hot pot together at the table." The activity scorer only triggered on `"food"` in the description — not `"cook"`. Riley, who lists cooking as an interest, got zero activity credit at Manna. One-word fix.

After: Allen Street wins 4/30. Manna wins 12/30. The distribution looks like a real algorithm, not a catch-all.

I kept the 14 old files in `app/data/precomputed/v1/` rather than deleting them. You can open any v1 file, compare it to the current version, and see exactly what changed. That's an honest record of how the system developed.

## Cache-first API

The 30 persona pairs are fixed. Calling Claude on every request adds 3–5 seconds of latency for identical output. The API now checks the precomputed cache first — instant response for any demo pair — and only falls through to live generation if there's a cache miss and an API key is set. No cache and no key returns a 503 with a specific message explaining exactly what's missing.

## Anthropic SDK migration

The original card generator used `subprocess.run(["claude", "-p", ...])` — shelling out to the Claude CLI. That's a hidden system dependency: it requires the CLI installed and authenticated on whatever machine runs the server. I replaced it with the Anthropic Python SDK, which is a declared dependency in `requirements.txt`, installs with pip, and authenticates via an environment variable. That's the right way to integrate with an API. The CLI approach was a fast path during development that didn't belong in the final version.

The test suite didn't need changes. `test_card_generator.py` patches `_call_claude` at the function level, so the subprocess-to-SDK swap was invisible to the tests.
