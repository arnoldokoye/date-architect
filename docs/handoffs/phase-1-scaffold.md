# Phase 1 — Project Scaffold
**Date:** May 3, 2026
**Status:** Complete
**Commits:** `feat(scaffold): add Pydantic models, requirements, and .env.example` · `feat(scaffold): add Next.js frontend, Dockerfiles, and docker-compose`

---

## 1. What we built

Five deliverables that turn Phase 0's data files into a runnable project:

**`backend/app/models.py`** — All Pydantic v2 schemas that define the type contract for the entire pipeline:
- `Venue` — mirrors the venues.json schema with full type annotations
- `Persona` — mirrors personas.json
- `ScoreBreakdown` — four scoring dimensions (energy_match, shared_activity, comfort_alignment, vibe_alignment), each 0-25, summing to 0-100
- `RankedVenue` — a Venue plus its score and breakdown
- `PersonaCard` — the four fields each user sees (compatibility_story, venue_rationale, talking_points, logistics)
- `DateCards` — wraps both persona cards
- `DatePlanResponse` — the full API response: top venue + both cards
- `GenerateDateRequest` — the two persona IDs the caller sends

**`backend/requirements.txt`** — Pinned dependencies: FastAPI 0.115, uvicorn 0.30.6, Pydantic 2.8.2, google-generativeai 0.8.3, python-dotenv 1.0.1, pytest 8.3.3, httpx 0.27.2, pytest-asyncio 0.24.0.

**`backend/.env.example`** — Single variable: `GEMINI_API_KEY`. Committed so anyone cloning knows what's needed without exposing a real key.

**`frontend/`** — Full Next.js 14 scaffold via `create-next-app` with TypeScript, Tailwind CSS, and App Router (`--app --no-src-dir --import-alias "@/*"`). The scaffold includes the default boilerplate pages that will be replaced in Task 5.

**`backend/Dockerfile`** + **`frontend/Dockerfile`** + **`docker-compose.yml`** — Backend on port 8000, frontend on port 3000. The compose file passes `GEMINI_API_KEY` as an environment variable and mounts `backend/app/data` as a volume so venue/persona JSON files don't need to be baked into the image.

---

## 2. The product thinking

The scaffold phase is invisible to the end user — it doesn't produce anything you can demo. But it's where you establish two things that save hours later: the type contract and the infrastructure boundaries.

**Models before code:**
By writing all Pydantic models before the matching engine or card generator, every downstream module gets autocomplete, type checking, and validation for free. The alternative — writing models alongside each module — leads to inconsistencies between what the API sends and what the frontend expects. Doing models first means the API response shape is locked before a single endpoint is written. Any mismatch between `ScoreBreakdown` and the frontend `VenueScore` component is caught by TypeScript before it reaches the browser.

**Docker from day one:**
Adding Docker in the scaffold (not as a final polish step) means the whole project can be demonstrated from a fresh clone with one command. For an interview submission specifically, this matters: the reviewer shouldn't have to debug your local Python version or Node version. It also forces you to think about configuration injection (env vars) at the right point — before you've accidentally hardcoded anything.

**`create-next-app` vs. manual scaffold:**
We used `create-next-app` rather than setting up Next.js manually because it does the right thing by default (App Router, TypeScript, Tailwind, the correct tsconfig paths). The time saved is better spent on the matching engine.

---

## 3. The decisions we made (and what we rejected)

**Decision: Pydantic v2 `str | None` union syntax instead of `Optional[str]`**

Python 3.10+ supports `X | Y` syntax natively. We use it throughout because it's more readable, it's idiomatic in 2025, and it signals to any reviewer that the codebase is modern. `Optional[str]` from `typing` still works but it's the old way.

**Decision: `activity_type: str | None` (nullable) in Venue model**

Some venues have no specific activity (e.g., a bar where you just talk). The field is nullable rather than defaulting to an empty string, because an empty string would slip through prompts silently ("Activity: "). `None` is explicit — the card generator handles it with `venue.activity_type or 'conversation'`.

**Decision: ScoreBreakdown uses four equal-weight dimensions (each 0-25)**

We could have weighted the dimensions differently — e.g., give energy_match 40% and vibe_alignment 10%. We kept them equal for V1 because: (a) there's no real training data to justify different weights, (b) explaining "each of four dimensions contributes equally" is simpler in an interview than defending arbitrary weights, and (c) you can always tune weights once the matching engine is tested and you see where scores feel wrong.

**Decision: Pinned dependency versions in requirements.txt**

Unpinned requirements (`google-generativeai>=0.8`) are acceptable in personal projects but produce non-reproducible installs. For a demo where someone else is running `docker compose up`, you want the exact same build every time. Everything is pinned.

**Decision: `docker-compose.yml` at project root, not in `backend/`**

The compose file orchestrates both services together. Placing it at the root makes `docker compose up` work from the repo root without arguments. Nesting it inside `backend/` would require `docker compose -f backend/docker-compose.yml`, which is a friction point for reviewers.

**Rejected: SQLAlchemy or any ORM**

There's no database. Venues and personas are loaded from JSON at request time. Adding an ORM for a JSON-backed demo would be over-engineering that actively hurts readability. V2 adds PostgreSQL and a proper schema — the JSON layer is an explicit architectural trade-off, not an oversight.

**Rejected: Separate `frontend/types.ts` in scaffold**

The TypeScript types file (`frontend/types/index.ts`) is deferred to Task 5 because it mirrors the Pydantic models — writing it now before the API is built risks drift. We'll write it alongside the frontend components where the types are first consumed.

---

## 4. How to explain it at different depths

**30 seconds:**
"Phase 1 was the project scaffold: Pydantic models that define the full type contract for the API, a pinned requirements file, a Next.js 14 frontend, and Docker Compose that brings up both services with one command. Nothing runs yet — this is the skeleton that everything else slots into."

**2 minutes:**
"Before writing any logic, I locked down the data contracts. The Pydantic models define every type the system touches — venues, personas, scores, cards, the API request and response. Doing this before writing the matching engine or card generator means I'm never guessing what fields exist or whether a score is a float or an int. It's the same reason you define an API spec before writing client code. I also wired up Docker Compose at this stage so the infrastructure is never an afterthought — the whole thing runs from a fresh clone with `docker compose up`. The frontend is `create-next-app` for now — just the scaffold. The real components come in Task 5."

**5 minutes:**
Open `backend/app/models.py` and walk through each model, explaining the type decisions (nullable `activity_type`, `str | None` syntax, ScoreBreakdown being four 25-point dimensions). Then explain the Docker setup: why the compose file is at the root, why we mount the data directory as a volume instead of baking it into the image (data files can change between venues without a rebuild), why the Gemini key is an env var injected at runtime. End with the trade-off discussion: why no database, why pinned deps, why create-next-app.

---

## 5. Anticipated interview questions + answers

**"Why write models before writing any logic?"**
Because the models are the contract between every layer of the system. If the matching engine returns a `RankedVenue` and the API expects a `DatePlanResponse`, those need to agree before either is written. Defining models first also means Pydantic validation catches shape mismatches at startup, not at demo time.

**"Why pin all dependency versions?"**
Reproducibility. For a submission someone else is running, you want identical builds every time. Pinned versions mean `docker compose up` works the same on the reviewer's machine as on mine. Unpinned versions risk hitting a breaking change in a library the night before submission.

**"Why Docker Compose this early?"**
Because infrastructure is easier to add before you have code than after. If you write 300 lines of FastAPI and then try to Dockerize it, you discover path issues, env var gaps, and port conflicts. Starting with Docker means every commit is already deployable.

**"Why use `create-next-app` instead of setting it up manually?"**
Time. `create-next-app` does the right thing: App Router, TypeScript, Tailwind, the correct import alias, proper tsconfig. Setting it up manually costs 30 minutes and produces worse defaults. For a demo built in one sitting, that time matters.

**"The Pydantic models look like they just mirror your JSON files. Is there any real logic there?"**
The models add three things the JSON files don't have: validation (Pydantic raises on missing fields or wrong types), documentation (the type hints are self-explaining), and serialization (FastAPI uses the models to generate OpenAPI docs and handle request/response parsing automatically). They're also the single source of truth — if I change a field name in the model, TypeScript errors in the frontend catch the drift immediately.

**"Why is `activity_type` nullable instead of defaulting to an empty string?"**
An empty string would silently pass through to the Gemini prompt as "Activity: " — which is meaningless. `None` is explicit: the card generator checks for it and substitutes "conversation" in the prompt. It's a small thing, but it prevents a class of silent data bugs.

---

## 6. The sentiment

The scaffold phase is easy to dismiss — it doesn't produce anything visible and there's no clever algorithm to show. But it's where you make decisions that shape every phase after it.

The key call here was writing models before logic. It's a discipline most developers skip because it feels like overhead. But in a project with three distinct layers (matching engine, card generator, API) and a frontend that also needs types, having a locked schema from the start is what prevents "wait, does the frontend get `score` or `total_score`?" conversations at 2am.

The Docker-first approach also felt right for the same reason: it forces you to think about the operational reality of the project (how does someone run this?) before you're deep in implementation. Adding Docker at the end of a project is painful. Adding it at the start is a 30-minute investment that pays off every time someone else runs your code.

One small thing worth noting: we kept the Dockerfile dead simple — no multi-stage build, no layer caching optimization, no non-root user. For V1 that's correct. The goal is a working demo, not a production-hardened container. A reviewer who sees a 40-line Dockerfile with HEALTHCHECK and USER directives for a 48-hour demo project is probably going to think "this person over-engineers things." Know when simple is right.
