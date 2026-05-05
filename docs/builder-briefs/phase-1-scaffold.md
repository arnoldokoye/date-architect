# Phase 1 — Project Scaffold

**What I built:** The project skeleton — Pydantic v2 models for the full type contract, a pinned `requirements.txt`, a Next.js 14 frontend scaffold, and Docker Compose wiring both services. Nothing runs yet; this is the skeleton that everything else slots into.

**Why models first:** By defining all Pydantic schemas before writing any logic, every downstream module gets type checking, autocomplete, and validation for free. The alternative — writing models alongside each module — leads to subtle shape mismatches between what the API sends and what the frontend expects. Locking the contract first means a TypeScript error in the frontend will catch any drift from the backend models before it reaches the browser.

**Key decisions:**
- **Pydantic v2 `str | None` syntax.** Modern Python (3.10+) union syntax over `Optional[str]`. It's more readable, it's idiomatic now, and it signals the codebase is current.
- **`activity_type` is nullable, not empty string.** An empty string would silently pass through to prompts as "Activity: " — meaningless noise. `None` is explicit: the card generator checks for it and substitutes `"conversation"`. Prevents a class of silent data bugs.
- **`ScoreBreakdown`: four equal-weight dimensions at 25 points each.** No arbitrary weights. "Four dimensions contribute equally to a 100-point score" is a clean, defensible answer. You tune weights after you have user data, not before.
- **Docker Compose at the root from day one.** Infrastructure added before code means every commit is already deployable. Adding Docker after you've written 300 lines is when you discover path issues and env var gaps. Starting with it means `docker compose up` works for anyone cloning the repo.
- **Pinned dependency versions.** Reproducible installs. For a submission someone else runs, you want identical builds every time.

**What I rejected:**
- **SQLAlchemy / any ORM.** No database. Venues and personas come from JSON files. Adding an ORM for a JSON-backed demo is over-engineering that actively hurts readability.
- **Setting up Next.js manually.** `create-next-app` does the right thing by default (App Router, TypeScript, Tailwind, proper tsconfig). Setting it up manually costs 30 minutes and produces worse defaults.
- **Separate `types.ts` in the frontend scaffold.** TypeScript types mirror the Pydantic models — writing them before the API is built risks drift. Deferred to Phase 5 where types are first consumed.
