# Phase 7 — Runner-Up Venues + Person Compatibility Score

Two additions that were already half-built by the time I added them.

**Runner-up venues.** `rank_venues_for_pair()` already returned a fully sorted list. I was using position 0 and throwing away positions 1 and 2. Stopping that discard was one line in `main.py`. The UI work was more involved, but the data was already there.

The "Lost on: X (N/25)" display for each runner-up took more thought than the data wiring. My first version showed the runner-up's absolute weakest dimension — which has an edge case. If the winning venue also scored 8/25 on activity, showing "Lost on: activity fit" for the runner-up is misleading. They tied on that dimension. The runner-up lost because the winner scored higher somewhere else.

Fixed it to compute `winner[dim] - runner[dim]` for each dimension and surface the one with the biggest positive gap. That's the actual competitive differentiator, not the runner-up's personal worst. Catching that edge case made the label genuinely accurate instead of just plausible-sounding.

**Person compatibility banner.** The matching engine already told you which *venue* fits the pair. But there was nothing on screen saying whether the *people* fit each other — which is kind of the point of a dating app. I built a separate compatibility engine that scores the pair on four dimensions: energy alignment, interest overlap, values alignment, vibe compatibility.

The interest and values matching uses group-based lookup rather than exact string comparison. "Indie music" and "live music" are different strings but they're the same interest group. Exact matching would score them as non-overlapping. The `INTEREST_GROUPS` table handles this without embeddings or normalization — just sets of semantically related terms.

I put the compatibility banner at the top of the result card, before the venue. In a dating product, "you two are Highly Compatible" is a warmer and more personal opening than "here's a coffee shop." The venue is actionable; the compatibility score is emotional. Leading with the emotional signal felt right.
