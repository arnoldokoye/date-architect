# Design Spec — Demo Polish: Persona Profiles + API Cleanup
**Date:** 2026-05-04
**Status:** Approved
**Scope:** 4 features, 4 files, no new packages, backend tests 24 → 25

---

## Context

Date Architect is a Ditto AI internship submission. Four gaps were identified before submission:

1. Frontend hardcodes the persona list — disconnected from backend
2. Persona profiles are invisible in the UI — compatibility scores feel unverifiable
3. README architecture diagram predates the compatibility engine and runner-up venues
4. Several persona interests fall outside all `INTEREST_GROUPS` clusters — scores silently inaccurate for Riley/Alex/Sam/Morgan pairs

All four fixes are additive or corrective. No architectural changes. No new packages.

---

## Feature 1 — `GET /personas` endpoint

### File: `backend/app/main.py`

Add one route and update CORS to allow GET:

```python
# CORS update — add GET to allowed methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# New route
@app.get("/personas", response_model=list[Persona])
def get_personas() -> list[Persona]:
    return list(_data["personas"].values())
```

`_data["personas"]` is already a `dict[str, Persona]` loaded at startup — this just exposes it. No new models needed. Returns full `Persona` objects so the frontend can use them for both dropdown population and profile card rendering in a single fetch.

### File: `backend/tests/test_api.py`

Add one new test:

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

**Done-when:** `GET /personas` returns 200 with 6 full persona objects. Test passes.

---

## Feature 2 — Persona Profile Panel

### File: `frontend/app/page.tsx`

**Three changes in one file:**

#### 2a — New `Persona` TypeScript interface (top of file)

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

#### 2b — New `PersonaProfileCard` component (above `Home`)

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

Interests use zinc tags (neutral). Values use rose tags (warmer). Visually distinct at a glance.

#### 2c — State + fetch changes inside `Home`

Remove hardcoded `PERSONAS` constant. Replace with:

```typescript
const [personas, setPersonas] = useState<Persona[]>([]);

useEffect(() => {
  fetch("http://localhost:8000/personas")
    .then((r) => r.json())
    .then(setPersonas);
}, []);
```

Dropdown `map` calls change from `PERSONAS.map(...)` to `personas.map(...)` — identical JSX otherwise.

`personaAName` and `personaBName` derivations change from:
```typescript
PERSONAS.find((p) => p.id === personaA)?.name ?? personaA
```
to:
```typescript
personas.find((p) => p.id === personaA)?.name ?? personaA
```

#### 2d — Profile cards render location

Between selector card and result, always visible once personas are loaded. Updates live on every dropdown change:

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

**Final layout order:**
1. Header
2. Selector card
3. Profile cards (live, always visible)
4. Error state
5. Loading spinner
6. DateCard result

**Done-when:** Profile cards render immediately on page load. Changing either dropdown updates the corresponding card live. Values use rose tags, interests use zinc tags. `npx tsc --noEmit` returns zero errors.

---

## Feature 3 — INTEREST_GROUPS + VALUES_GROUPS expansion

### File: `backend/app/compatibility_engine.py`

**Gap audit — interests not in any group:**

| Interest | Persona | Fix |
|---|---|---|
| `craft beer` | Alex | Add to food group |
| `travel` | Riley | Add to outdoor group |
| `fashion` | Sam | Add to art group |
| `astrology` | Morgan | Skip — too niche, no cross-persona overlap |
| `brent faiyaz` | Morgan | Skip — artist name, no pairable equivalent |
| `social media` | Sam | Skip — no meaningful overlap |

**Gap audit — values not in any group:**

| Value | Persona | Fix |
|---|---|---|
| `good food` | Riley | Add to adventure group |
| `loyalty` | Jordan | Skip — no cross-persona overlap |

**Updated tables:**

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

VALUES_GROUPS: list[set[str]] = [
    {"curiosity", "intellectual curiosity", "depth", "authenticity"},
    {"honesty", "low pretense", "authenticity"},
    {"fun", "spontaneity", "energy", "confidence", "living in the moment"},
    {"adventure", "openness", "good food"},                            # + good food
    {"peace", "intentionality", "beauty"},
]
```

**Scoring impact:**
- Riley + Alex: food group now overlaps (`trying new restaurants` + `craft beer`) → score increases
- Sam + Morgan: art group now overlaps (`fashion` + `photography`) → score increases
- Riley + Morgan: outdoor group now overlaps (`travel` + `nature`) → score increases
- Maya + Alex: unchanged (already well-covered)
- Maya + Jordan: unchanged (High Contrast label preserved)

**Existing tests must not break.** `test_maya_alex_highly_compatible` (≥80) and `test_maya_jordan_high_contrast` (<50) must still pass — these pairs are unaffected by the additions.

**Done-when:** All 25 backend tests pass. New additions visible in group membership. No score regressions on Maya+Alex or Maya+Jordan.

---

## Feature 4 — README diagram + example output

### File: `README.md`

**Updated architecture diagram:**

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

**Updated example output section** — replace the old 4-row table:

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

**Done-when:** README accurately describes the current system. Diagram includes both engines, full response shape, and `GET /personas` in the browser layer.

---

## Execution Order

Must be sequential — Feature 2 depends on Feature 1 being live:

1. **Feature 1** — `GET /personas` backend + test → run `pytest tests/ -v` (expect 25 passed)
2. **Feature 3** — INTEREST_GROUPS expansion → run `pytest tests/ -v` (no regressions)
3. **Feature 2** — Frontend persona panel → run `npx tsc --noEmit` (0 errors)
4. **Feature 4** — README → visual review only

## File Index

| File | Change type |
|---|---|
| `backend/app/main.py` | Add `GET /personas` route, update CORS `allow_methods` |
| `backend/tests/test_api.py` | Add `test_get_personas_returns_all_personas` |
| `backend/app/compatibility_engine.py` | Expand `INTEREST_GROUPS` (3 additions) + `VALUES_GROUPS` (1 addition) |
| `frontend/app/page.tsx` | Add `Persona` interface, `PersonaProfileCard` component, `useEffect` fetch, remove hardcoded array, add profile card render |
| `README.md` | Update architecture diagram + example output |
