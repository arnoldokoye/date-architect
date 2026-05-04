# Phase 4 — FastAPI Endpoint
**Date:** 2026-05-04
**Status:** Complete
**Commits:**
- `0e413e2` — `feat(api): add FastAPI endpoint POST /generate-date-plan with 4 integration tests`

---

## 1. What we built

**`backend/app/main.py`** — A minimal FastAPI app with a single endpoint:

- `POST /generate-date-plan` — accepts `GenerateDateRequest(persona_a_id, persona_b_id)`, returns `DatePlanResponse(venue: RankedVenue, cards: DateCards)`

Three responsibilities:
1. **Startup** — loads `personas.json` and `venues.json` once via lifespan context manager into a module-level `_data` dict; no per-request I/O
2. **Validation** — returns 404 with a clear detail message if either persona ID is not found
3. **Orchestration** — calls `rank_venues_for_pair` to get the ranked list, then `generate_date_cards` with the top-ranked venue, returns the pair as `DatePlanResponse`

**`backend/tests/test_api.py`** — 4 tests using FastAPI's `TestClient` (synchronous, no async needed):

| Test | What it covers |
|---|---|
| `test_generate_date_plan_returns_200` | Valid pair returns 200 and response has `venue` + `cards` keys |
| `test_generate_date_plan_venue_fields` | `venue.venue.name` is a non-empty string; `venue.score` is 0–100 |
| `test_generate_date_plan_cards_fields` | Both `persona_a` and `persona_b` have a non-empty `compatibility_story` |
| `test_generate_date_plan_unknown_persona_returns_404` | Unknown `persona_a_id` returns 404 |

`generate_date_cards` is mocked at `app.main.generate_date_cards` in all tests — no subprocess calls, no Claude invocations. The mock returns a populated `DateCards` with two real `PersonaCard` objects.

Total test suite: **13 tests, all passing**.

Live smoke test confirmed: `POST /generate-date-plan` with `{maya, alex}` returns Elixr Coffee Roasters (score=72) with full JSON response in ~2s.

---

## 2. The product thinking

The endpoint is the integration seam — it's where the two internal systems (scoring algorithm, LLM card generator) become a single API call from the outside world. The design goal was to keep this layer as thin as possible: it translates HTTP → domain types, delegates to the domain layer, and translates back. No business logic lives in `main.py`.

The lifespan pattern for data loading is the right choice here for a few reasons. Loading `personas.json` and `venues.json` at startup means the first request isn't penalised with file I/O. More importantly, it makes the boundary clear: the data is stable configuration, not dynamic state. If those files needed to change at runtime (e.g., venues were coming from a database), you'd update the lifespan — not touch the endpoint handler.

The 404 behavior is also a product decision, not just a technical one. If a persona ID isn't found, the service can't proceed — there's no degraded fallback to offer. A 404 is the right signal: "the resource you're asking about doesn't exist in this system." A 422 (validation error) would be wrong because the request body is structurally valid — the issue is a missing entity. A 500 would be wrong because this is a known failure mode. 404 is precise.

---

## 3. The decisions we made (and what we rejected)

**Decision: lifespan context manager for data loading, not module-level globals**

We could have loaded `personas.json` and `venues.json` as module-level globals when `main.py` is imported. This works fine in production but creates subtle test coupling — the data gets loaded at import time, before the test harness has a chance to override anything. The lifespan pattern is the FastAPI-idiomatic way to initialize app state: it runs exactly once at startup, is visible in the `_data` dict for the duration of the app, and clears on shutdown. It also makes the data loading path explicit and testable.

**Decision: mock `app.main.generate_date_cards`, not `app.card_generator._call_gemini`**

In `test_card_generator.py`, we mock `_call_gemini` — the lowest-level boundary that makes the subprocess call. In `test_api.py`, we mock at a higher level: `app.main.generate_date_cards`. This is intentional. The API tests are integration tests for the endpoint layer — they're testing that the endpoint correctly calls `generate_date_cards` and returns its output. They're not testing the card generator's internal logic (that's already covered by `test_card_generator.py`). Mocking at the right boundary keeps each test file focused on exactly one layer.

**Decision: synchronous TestClient, not async test functions**

FastAPI supports async endpoints and async tests via `pytest-asyncio`. We didn't use async here because the endpoint itself is synchronous (`def generate_date_plan`, not `async def`). There's no I/O happening inside the handler that would benefit from async — file loading is in lifespan, ranking is pure CPU, and `generate_date_cards` is mocked. Using `TestClient` (which runs the ASGI app synchronously via `httpx`) is simpler, faster to run, and avoids async test boilerplate for no gain.

**Decision: no CORS, no auth, no middleware**

The prompt specified "minimal." This is a demo API for an interview project — adding CORS headers or auth would create surface area that can fail without contributing anything to the demo. The Next.js frontend will run on the same machine during the demo, so CORS isn't needed. If this were a real production service, you'd add CORS for the browser client and an API key at minimum.

**Rejected: loading data inside the endpoint handler**

Loading `personas.json` and `venues.json` on every request would work but is wasteful — these files never change during a server run. It also makes tests that don't mock the file loading dependent on the presence of the real data files. Lifespan loading is the right pattern.

**Rejected: `@app.on_event("startup")` (deprecated)**

FastAPI deprecated `@app.on_event("startup")` in favor of lifespan context managers. The lifespan pattern is the current idiomatic approach and avoids deprecation warnings in the test output.

---

## 4. How to explain it at different depths

**30 seconds:**
"I added a FastAPI endpoint — `POST /generate-date-plan` — that takes two persona IDs, runs them through the matching engine to get the top venue, generates personalized date cards for both people via the Claude CLI, and returns everything as a single JSON response. It validates persona IDs and returns 404 if they're not found. Four integration tests cover the happy path and the 404 case, all mocking the card generator so tests don't shell out to Claude."

**2 minutes:**
"The endpoint is the integration layer that connects the two internal systems I built earlier. On startup, it loads the personas and venues from JSON into memory using FastAPI's lifespan context manager — so file I/O happens once, not per request. When a request comes in, it validates both persona IDs, returns 404 if either isn't found, then calls `rank_venues_for_pair` to get the scored and sorted venue list, passes the top-ranked venue to `generate_date_cards`, and returns the combined result as `DatePlanResponse`.

The test design was intentional: I mock `generate_date_cards` at the `app.main` module level rather than going deeper to `_call_gemini`. The API tests are integration tests for the endpoint layer — they verify that the endpoint wires things together correctly and returns the right shape. The card generator's internal logic is already covered by `test_card_generator.py`. Each test file has a clear boundary and tests exactly one layer."

**5 minutes:**
Walk through `main.py` line by line — lifespan pattern, dict lookup for 404, the two domain calls, the return type. Show the test file: explain why `patch("app.main.generate_date_cards")` not `patch("app.card_generator._call_gemini")`, and how the fixture wires through TestClient's lifespan. Show the live smoke test output — Elixr Coffee (score=72) returned for Maya+Alex with full venue + cards structure. End on the architectural point: this endpoint is stateless and thin by design. All the intelligence is in the two domain modules. The endpoint is just the HTTP adapter.

---

## 5. Anticipated interview questions + answers

**"Why FastAPI and not Flask or Django?"**
FastAPI gives you automatic request validation and response serialization via Pydantic — the same models I'm already using for domain types. The `GenerateDateRequest` and `DatePlanResponse` models defined in `models.py` double as the API contract: FastAPI validates incoming JSON against `GenerateDateRequest` automatically and serializes the response via `DatePlanResponse`. In Flask, you'd write that validation manually. Django is heavier than this use case needs. FastAPI also generates an OpenAPI spec at `/docs` for free, which is useful for demoing.

**"What happens if `generate_date_cards` raises an exception?"**
Currently it bubbles up as a 500. In production you'd catch `RuntimeError` (the exception `_call_gemini` raises on subprocess failure) and return a 503 with a retry hint. You'd also want a timeout at the endpoint level — the subprocess call already has a 120s timeout, but you'd want the HTTP layer to enforce its own SLA, typically shorter. For the interview demo, the Claude CLI is reliable enough that this hasn't been an issue.

**"How does the lifespan pattern work?"**
The lifespan function is an async context manager passed to `FastAPI()`. The code before `yield` runs at startup; the code after `yield` runs at shutdown. FastAPI guarantees this runs before any requests are served. `TestClient` respects the lifespan — it runs the startup phase when you enter the `with TestClient(app)` block, so tests see the fully loaded `_data` dict without any special setup.

**"Why mock `generate_date_cards` at the `app.main` level instead of at `card_generator`?"**
When Python imports `app.main`, it binds the name `generate_date_cards` in the `app.main` namespace. When the endpoint calls `generate_date_cards(...)`, it's looking up that name in `app.main`'s namespace. If you patched `app.card_generator.generate_date_cards`, you'd be replacing the function in the `card_generator` module — but `app.main` already has a direct reference to the original. The mock wouldn't intercept the call. This is the standard Python mock gotcha: patch where the name is looked up, not where it's defined.

**"How would you add authentication?"**
Add a FastAPI dependency: `api_key: str = Header(...)`, validate it against an environment variable, raise `HTTPException(401)` if it doesn't match. Since it's a dependency, it applies to any route that injects it — you can add it globally via `app.include_router(router, dependencies=[Depends(verify_api_key)])` without touching individual endpoint handlers.

---

## 6. The sentiment

This phase was the shortest in wall-clock time and the most satisfying in terms of visible output. The two domain modules — matching engine and card generator — were already complete and tested. `main.py` is 45 lines because all the interesting work was already done.

The lifespan pattern took a minute to get right. The old `@app.on_event("startup")` API is still what most tutorials show, and it's deprecated. Using the context manager form is cleaner but requires knowing that FastAPI 0.93+ prefers it. The `TestClient` lifespan handling was also a small discovery — you need to use `TestClient` as a context manager (`with TestClient(app) as c`) for the lifespan to run, not just instantiate it directly. Both of these are the kind of thing you learn by reading the FastAPI docs carefully rather than copying old Stack Overflow answers.

The mock boundary decision — patching `app.main.generate_date_cards` not `app.card_generator._call_gemini` — is worth highlighting because it's a real design choice that matters for test maintainability. The card generator tests already cover the subprocess call. The API tests don't need to go that deep. Keeping each test file focused on one layer means you can change the card generator's internals (swap Claude for a different backend, change the retry logic) without touching the API tests at all. The tests stay coupled to the interfaces, not the implementation details.
