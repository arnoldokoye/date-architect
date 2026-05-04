# Demo Polish Implementation Plan
> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans

**Goal:** Add GET /personas endpoint, expand INTEREST_GROUPS coverage, add persona profile panel to frontend, and update README diagram.

**Architecture:** All changes are additive or corrective. Feature 1 (GET /personas) is a prerequisite for Feature 3 (frontend panel). Feature 2 (INTEREST_GROUPS) is independent. Feature 4 (README) is documentation-only.

**Tech Stack:** Python 3.13 / FastAPI / Pydantic v2 (backend), Next.js / TypeScript / Tailwind CSS v4 (frontend), pytest + TestClient (tests)

---

## Execution Order

**Feature 1 → Feature 2 → Feature 3 → Feature 4** (Feature 3 depends on Feature 1 being live)

---

## Feature 1 — GET /personas endpoint

**Files:** `backend/app/main.py`, `backend/tests/test_api.py`

**Verification:** `cd /Users/arnoldokoye/date-architect/backend && ./venv/bin/pytest tests/ -v` — expect 25 passed

### Task 1a — Update CORS + add route in `main.py`

- [ ] In `backend/app/main.py`, change `allow_methods=["POST"]` to `allow_methods=["GET", "POST"]`
- [ ] Add new route after the existing `generate_date_plan` route:

```python
@app.get("/personas", response_model=list[Persona])
def get_personas() -> list[Persona]:
    return list(_data["personas"].values())
```

### Task 1b — Add test in `test_api.py`

- [ ] Add at the bottom of `backend/tests/test_api.py`:

```python
def test_get_personas_returns_all_personas(client):
    resp = client.get("/personas")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 6
    for p in data:
        assert "id" in p
        assert "name" in p
        assert "energy_level" in p
        assert "interests" in p
        assert "values" in p
        assert "date_preference" in p
```

### Task 1c — Verify

- [ ] Run `cd /Users/arnoldokoye/date-architect/backend && ./venv/bin/pytest tests/ -v`
- [ ] Confirm 25 tests pass
- [ ] Commit: `feat: add GET /personas endpoint and CORS update`

---

## Feature 2 — INTEREST_GROUPS + VALUES_GROUPS expansion

**File:** `backend/app/compatibility_engine.py`

**Verification:** `cd /Users/arnoldokoye/date-architect/backend && ./venv/bin/pytest tests/ -v` — no regressions (still 25 passed)

### Task 2a — Expand INTEREST_GROUPS

- [ ] In `backend/app/compatibility_engine.py`, replace `INTEREST_GROUPS` with:

```python
INTEREST_GROUPS: list[set[str]] = [
    {"music", "indie music", "live music", "rap music", "latin music"},
    {"outdoor", "hiking", "nature", "travel"},                          # + travel
    {"art", "film", "photography", "design", "fashion"},               # + fashion
    {"food", "cooking", "culinary", "korean culture",
     "trying new restaurants", "craft beer"},                          # + craft beer
    {"reading", "book", "philosophy", "history"},
    {"social", "going out", "dancing", "sports", "basketball"},
]
```

### Task 2b — Expand VALUES_GROUPS

- [ ] In `backend/app/compatibility_engine.py`, replace `VALUES_GROUPS` with:

```python
VALUES_GROUPS: list[set[str]] = [
    {"curiosity", "intellectual curiosity", "depth", "authenticity"},
    {"honesty", "low pretense", "authenticity"},
    {"fun", "spontaneity", "energy", "confidence", "living in the moment"},
    {"adventure", "openness", "good food"},                            # + good food
    {"peace", "intentionality", "beauty"},
]
```

### Task 2c — Verify

- [ ] Run `cd /Users/arnoldokoye/date-architect/backend && ./venv/bin/pytest tests/ -v`
- [ ] Confirm 25 tests pass (no regressions — Maya+Alex ≥80, Maya+Jordan <50)
- [ ] Commit: `feat: expand INTEREST_GROUPS and VALUES_GROUPS coverage`

---

## Feature 3 — Persona Profile Panel (frontend)

**File:** `frontend/app/page.tsx`

**Verification:** `cd /Users/arnoldokoye/date-architect/frontend && npx tsc --noEmit` — 0 errors

### Task 3a — Add Persona TypeScript interface (top of file, after `"use client"` directive)

- [ ] Add after the imports:

```typescript
interface Persona {
  id: string;
  name: string;
  energy_level: number;
  conversation_style: string;
  interests: string[];
  values: string[];
  comfort_with_strangers: number;
  date_preference: string;
}
```

### Task 3b — Add PersonaProfileCard component (above `Home`)

- [ ] Add before `export default function Home()`:

```tsx
function PersonaProfileCard({ persona, label }: { persona: Persona; label: string }) {
  const DATE_PREF_LABELS: Record<string, string> = {
    low_pressure: "Low pressure",
    social: "Social",
    culinary: "Culinary",
    active: "Active",
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-rose-100 p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">{label}</div>
          <div className="text-base font-bold text-zinc-900">{persona.name}</div>
        </div>
        <span className="text-xs bg-rose-100 text-rose-700 font-semibold px-2.5 py-1 rounded-full">
          {DATE_PREF_LABELS[persona.date_preference] ?? persona.date_preference}
        </span>
      </div>

      <div className="flex items-center gap-1.5 mb-3">
        <span className="text-xs text-zinc-400">Energy</span>
        <div className="flex gap-0.5">
          {[1, 2, 3, 4, 5].map((n) => (
            <div
              key={n}
              className={`w-2.5 h-2.5 rounded-full ${
                n <= persona.energy_level ? "bg-rose-400" : "bg-zinc-100"
              }`}
            />
          ))}
        </div>
        <span className="text-xs text-zinc-400 ml-1">{persona.conversation_style}</span>
      </div>

      <div className="mb-2">
        <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-1">Interests</div>
        <div className="flex flex-wrap gap-1">
          {persona.interests.map((i) => (
            <span key={i} className="bg-zinc-100 text-zinc-600 text-xs px-2 py-0.5 rounded-full">{i}</span>
          ))}
        </div>
      </div>

      <div>
        <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-1">Values</div>
        <div className="flex flex-wrap gap-1">
          {persona.values.map((v) => (
            <span key={v} className="bg-rose-50 text-rose-600 text-xs px-2 py-0.5 rounded-full">{v}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Task 3c — Replace hardcoded PERSONAS + add state/fetch inside Home

- [ ] Remove the `const PERSONAS = [...]` array at the top of the file
- [ ] Add `useEffect` to the import: `import { useState, useEffect } from "react";`
- [ ] Replace all `useState` declarations in `Home` — add `personas` state:

```typescript
const [personas, setPersonas] = useState<Persona[]>([]);

useEffect(() => {
  fetch("http://localhost:8000/personas")
    .then((r) => r.json())
    .then(setPersonas);
}, []);
```

- [ ] Replace `PERSONAS.find(...)` with `personas.find(...)` in both name derivations:

```typescript
const personaAName = personas.find((p) => p.id === personaA)?.name ?? personaA;
const personaBName = personas.find((p) => p.id === personaB)?.name ?? personaB;
```

- [ ] Replace `PERSONAS.map(...)` with `personas.map(...)` in both dropdowns

### Task 3d — Add profile cards render between selector and result

- [ ] After the closing `</div>` of the selector card (before `{/* Error */}`), add:

```tsx
{/* Profile cards */}
{personas.length > 0 && (
  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
    <PersonaProfileCard
      persona={personas.find((p) => p.id === personaA)!}
      label="Person A"
    />
    <PersonaProfileCard
      persona={personas.find((p) => p.id === personaB)!}
      label="Person B"
    />
  </div>
)}
```

### Task 3e — Verify

- [ ] Run `cd /Users/arnoldokoye/date-architect/frontend && npx tsc --noEmit`
- [ ] Confirm 0 errors
- [ ] Commit: `feat: add persona profile panel with live API fetch`

---

## Feature 4 — README diagram + example output

**File:** `README.md`

### Task 4a — Replace architecture diagram

- [ ] Replace the existing `## Architecture` code block with:

```
┌──────────────────────────────────────────────────────────┐
│                    Browser (Next.js)                     │
│                                                          │
│   GET /personas ──► Persona A dropdown                   │
│                     Persona B dropdown                   │
│                          │                               │
│                    "Find Our Date"                       │
└──────────────────────────┼───────────────────────────────┘
                           │ POST /generate-date-plan
                           ▼
┌──────────────────────────────────────────────────────────┐
│                    FastAPI backend                        │
│                                                          │
│         ┌────────────────┴─────────────────┐            │
│         ▼                                  ▼            │
│   Matching Engine                  Compatibility Engine  │
│  (venue × pair scorer)             (person × person)     │
│                                                          │
│  energy_match   ──┐               energy_alignment       │
│  shared_activity──┼► RankedVenue  interest_overlap       │
│  comfort_align ───┘  × 12 venues  values_alignment       │
│  vibe_alignment                   vibe_compatibility     │
│         │                                  │            │
│         ▼                                  │            │
│   top venue ──► Claude CLI                 │            │
│                (card_generator.py)         │            │
│                                            │            │
│  compatibility_story                       │            │
│  venue_rationale                           │            │
│  talking_points                            │            │
│  logistics                                 │            │
└──────────────────────────────────────────────────────────┘
               │ DatePlanResponse
               │  ├─ venue (RankedVenue)
               │  ├─ runner_up_venues (2 × RankedVenue)
               │  ├─ cards (DateCards)
               │  └─ compatibility (PersonCompatibility)
               ▼
        DateCard component (React)
  CompatibilityBanner · Venue card · Persona cards
  Also Considered (runner-up venues)
```

### Task 4b — Replace example output section

- [ ] Replace the `## Example Output — Maya + Alex` section with:

```markdown
## Example Output — Maya + Alex

**Compatibility: Highly Compatible — 92/100**

| Dimension | Score |
|-----------|-------|
| Energy alignment | 25/25 |
| Interest overlap | 21/25 |
| Values alignment | 21/25 |
| Vibe compatibility | 25/25 |

**Top venue: Elixr Coffee Roasters** · Score: **72/100**

| Dimension | Score |
|-----------|-------|
| Energy match | 25/25 |
| Shared activity | 8/25 |
| Comfort alignment | 23/25 |
| Vibe alignment | 16/25 |

**Also Considered:**
- The Tavern Restaurant — 67/100 · Lost on: comfort fit (18/25)
- Webster's Bookstore Café — 63/100 · Lost on: vibe match (8/25)

**Maya's talking point (Claude-generated):**
> "You mentioned hiking — do you go to find the view at the end, or is it more about
> the time to think on the way up? I always wonder what people are actually chasing out there."
```

### Task 4c — Commit

- [ ] Commit: `docs: update README diagram and example output`

---

## File Index

| File | Change |
|------|--------|
| `backend/app/main.py` | Add `GET /personas` route, update CORS `allow_methods` to include GET |
| `backend/tests/test_api.py` | Add `test_get_personas_returns_all_personas` |
| `backend/app/compatibility_engine.py` | Add `travel` to outdoor group, `fashion` to art group, `craft beer` to food group, `good food` to adventure values group |
| `frontend/app/page.tsx` | Add `Persona` interface, `PersonaProfileCard` component, `useEffect` fetch, remove hardcoded array, add profile card render |
| `README.md` | Update architecture diagram + example output section |
