# Phase 9 — Outcome Recording + Feedback Loop Instrumentation

The matching algorithm tells you which venue to pick. It has no idea whether that pick led to a good date.

That gap was always there, but it became obvious when I ran `eval.py` and looked at the distribution: Manna Korean BBQ wins 40% of pairings, The Phyrst wins 20%. Those are algorithm opinions. There was nothing on the other side — no record of what actually happened when people showed up. Without that, the scoring weights are permanent guesses. You can't improve what you can't measure.

## What I built

Two endpoints and a SQLite layer:

- `POST /record-outcome` — takes a pair of persona IDs, a venue ID, and an outcome (`went`, `skipped`, or `great_date`). Validates that both personas exist, rejects same-persona pairs, and writes an append-only row.
- `GET /outcome-stats` — returns total outcomes, breakdown by venue, and breakdown by outcome type.

All SQLite logic lives in `app/db.py`. `main.py` imports functions and calls them — it never touches `sqlite3` directly. The boundary was intentional: if I wanted to swap SQLite for Postgres later, the change would be entirely contained in one file.

`init_db()` is called once at server startup inside the existing lifespan context manager. The table schema uses a `CHECK` constraint to enforce valid outcome values at the database level, not just the API level.

## Why append-only

I deliberately didn't add UPDATE or DELETE routes. Outcome data is an event log, not a mutable state. Allowing edits would mean you'd never know whether the data reflects what actually happened or what someone wished had happened. Append-only is the right primitive for a feedback signal you're eventually going to train on.

## The eval.py integration

The most useful surface for this data isn't an API response — it's the eval script. I added an outcomes section at the end that only renders if `outcomes.db` exists. It shows per-venue outcome counts alongside the algorithm's pick rate, and flags the gap with a directional indicator:

- `↑ under-recommended` — venue has a high great_date rate but the algorithm isn't picking it enough
- `↓ over-recommended` — algorithm picks it often but dates there don't go well
- `~` — no significant gap

After seeding 8 plausible outcomes, the output shows Manna Korean BBQ at 40% algorithm picks vs 67% great_date rate — under-recommended. The Phyrst at 20% picks vs 0% great_date rate — over-recommended. That's a real signal. The algorithm is biased toward a venue that underperforms and away from one that doesn't.

In production, closing that loop is how you build a system that gets better over time rather than one that's frozen at whatever the initial weights happened to be.

## Test isolation

The DB path is a function (`_db_path()`) rather than a module-level constant specifically so tests can patch it. A `conftest.py` fixture redirects every test to a `tmp_path` instance — no test touches the real `outcomes.db`, no test leaves state that bleeds into the next one. The 7 new `test_db.py` tests run against an isolated temp DB; the 5 new API tests run through the full FastAPI lifespan with the same isolation.
