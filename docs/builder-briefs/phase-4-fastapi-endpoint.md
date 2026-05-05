# Phase 4 — FastAPI Endpoint

**What I built:** `POST /generate-date-plan` — a thin integration layer that accepts two persona IDs, runs them through the matching engine to get the top venue, calls the card generator for personalized copy, and returns a `DatePlanResponse` as JSON. With 4 integration tests covering the happy path, venue fields, card fields, and 404 behavior.

**Design goal:** Keep this layer as thin as possible. No business logic in `main.py` — it translates HTTP to domain types, delegates to the domain layer, translates back. All the intelligence is in the two domain modules. The endpoint is the HTTP adapter.

**Key decisions:**
- **Lifespan context manager for data loading.** Loading `personas.json` and `venues.json` at startup (not per-request) means the first request isn't penalized with file I/O. The lifespan pattern is the FastAPI-idiomatic way since v0.93 — `@app.on_event("startup")` is deprecated. `TestClient` respects the lifespan when used as a context manager, so tests see the fully loaded data without special setup.
- **404, not 422, for unknown persona IDs.** 422 means the request is structurally malformed. 404 means the resource doesn't exist. These are different errors and the wrong status code misleads anyone reading logs or building clients.
- **Mock `app.main.generate_date_cards`, not `app.card_generator._call_claude`.** API tests verify that the endpoint correctly wires things together — not the card generator's internals, which are already covered by `test_card_generator.py`. Patching at the right boundary means you can change the card generator's internals without touching API tests. Standard Python mock gotcha: patch where the name is looked up (`app.main`), not where it's defined (`app.card_generator`).
- **No CORS, no auth, no middleware.** This is a demo API. Adding middleware creates surface area that can fail without contributing to the demo. Frontend and backend run on the same machine.

**What I rejected:**
- **Loading data inside the endpoint handler.** Wasteful — these files never change during a server run. Per-request file I/O for static configuration is just wrong.
- **Async endpoint.** The handler is synchronous — file loading happens in lifespan, ranking is pure CPU, card generation is mocked in tests. Using `TestClient` over async test boilerplate is simpler for no downside.
