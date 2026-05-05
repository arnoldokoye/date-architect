# Phase 2–3 — Matching Engine + Card Generator

The core of the system. Two modules that do completely different things and intentionally don't know about each other.

`matching_engine.py` is pure Python with no LLM anywhere near it. It takes two personas and all 12 venues, scores each venue across four dimensions — energy fit, shared activity potential, comfort alignment, vibe match — and returns a ranked list. The whole thing runs in milliseconds. Same input always produces the same output.

`card_generator.py` takes the top-ranked venue and both personas, builds a prompt grounded in their actual interests and values, and calls Claude to generate two personalized date cards.

I kept these completely separate because the alternative — one LLM call that both picks the venue and writes the cards — has problems I don't want. You can't unit test it. Same pair can get a different venue on different runs. When something's wrong you can't tell if the venue pick was bad or the card was bad. The algorithm does constraint satisfaction; the LLM does language. That division is load-bearing.

The tests passed on the first run. I thought I was done, then actually ran the system against real personas. Jordan and Sam — both high-energy social types — were getting Allen Street Grill (a farm-to-table dinner spot) instead of Champs (a sports bar). The score difference wasn't close.

Turned out to be two bugs. First: I was checking for `"bars"` as a vibe keyword but the venue tag was `"sports bar"` — the substring was backwards. `"bars"` doesn't appear in `"sports bar"` but `"bar"` does. Second: the comfort alignment formula used `abs()`, which meant a high-comfort pair visiting a low-intimacy bar got penalized the same as the reverse. That's wrong — over-qualified for a venue is fine. Under-qualified is a problem. Switched to `max(0, intimacy - avg_comfort)`.

Both bugs would have survived to the demo if I hadn't looked at the actual numbers. Tests passing is not the same as the output making sense.

The prompt design for the card generator is deliberately tight. Every specific detail Claude could include is already in the prompt — venue address, vibe tags, activity type, notes. Claude isn't asked to know anything about Elixr Coffee from training data; it's told everything it needs. The only creative latitude is in phrasing. That's what keeps the cards grounded instead of plausible-sounding but wrong.
