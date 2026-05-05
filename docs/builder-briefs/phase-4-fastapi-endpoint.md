# Phase 4 — FastAPI Endpoint

`POST /generate-date-plan`. Takes two persona IDs, returns a complete date plan. That's the whole thing.

`main.py` is 110 lines because the interesting work was already done in the two domain modules (it grew from 88 to 110 in Phase 9 when the outcomes endpoints were added). The endpoint's job is to translate HTTP into domain types, delegate to the scoring engine and card generator, and translate back. No business logic lives here.

A few things worth explaining:

**Data loading.** Personas and venues load once at startup via FastAPI's lifespan context manager, not on every request. File I/O for static data that never changes during a server run is just waste. The lifespan pattern also has a nice property for tests: `TestClient` respects the lifespan, so tests see the fully loaded data without any special setup.

**Why 404, not 422.** If you send an unknown persona ID, you get a 404 with a clear message. 422 would mean the request body is structurally malformed — it's not, it's a valid JSON object with a real-looking string. The resource just doesn't exist. These are different errors and the wrong status code makes debugging harder.

**Mock boundary in tests.** The API tests mock at `app.main.generate_date_cards`, not at `app.card_generator._call_claude`. The API tests are checking that the endpoint wires things together correctly and returns the right shape — they're not testing the card generator's internals, which are already covered by `test_card_generator.py`. This is the standard Python mock gotcha: patch where the name is looked up, not where it's defined. If you patch `app.card_generator.generate_date_cards`, the call in `main.py` doesn't get intercepted because it already has a direct reference to the original.

The endpoint has CORS middleware configured to allow the frontend on port 3000 to reach the backend on port 8000 — without it, the browser blocks the request. No auth or additional middleware beyond that. It's a demo API. Adding more middleware creates surface area that can fail without contributing anything.
