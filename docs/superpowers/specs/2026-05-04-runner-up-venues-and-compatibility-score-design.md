# Design Spec — Runner-Up Venues + Person-to-Person Compatibility Score

**Date:** 2026-05-04
**Repo:** `/Users/arnoldokoye/date-architect`
**Status:** Approved for implementation

---

## 1. Goals

Add two features to the existing Date Architect demo before the Ditto AI internship submission:

- **Option B — Runner-Up Venues:** Surface the #2 and #3 scored venues below the main result, showing the score and the single weakest dimension ("why it lost"), so the AI's reasoning is transparent rather than a black box.
- **Option C — Person-to-Person Compatibility Score:** Add a banner above the venue card showing how compatible the two selected personas are across four dimensions, scored deterministically. This directly addresses the core Ditto product insight — matching people — which is currently absent from the demo.

Both are purely additive. Zero breaking changes to existing behavior.

---

## 2. Execution Order

Phases must be completed in this sequence to avoid double-editing the shared `DatePlanResponse` contract:

1. **Phase 0 — Rename cleanup** (`_call_gemini` → `_call_claude`, remove dead `google-generativeai` import)
2. **Phase 1 — Backend** (all model changes + new engine + wiring in one pass)
3. **Phase 2 — Frontend Option B** (runner-up UI)
4. **Phase 3 — Frontend Option C** (compatibility banner)
5. **Phase 4 — Smoke test** (manual end-to-end verification)

---

## 3. Phase 0 — Rename Cleanup

**File:** `backend/app/card_generator.py`

- Rename `_call_gemini` → `_call_claude` throughout the file
- Remove the `google-generativeai==0.8.3` line from `requirements.txt` (unused, misleading)
- No behavioral change

---

## 4. Phase 1 — Backend

### 4a. New Pydantic Models (`models.py`)

Add two new models for Option C. Add one new field to `DatePlanResponse` for each option.

**New models:**

```python
class CompatibilityBreakdown(BaseModel):
    energy_alignment: int      # 0–25
    interest_overlap: int      # 0–25
    values_alignment: int      # 0–25
    vibe_compatibility: int    # 0–25

class PersonCompatibility(BaseModel):
    score: int                 # 0–100 (sum of breakdown)
    label: str                 # "Highly Compatible" | "Complementary" | "Interesting Mix" | "High Contrast"
    breakdown: CompatibilityBreakdown
```

**Updated `DatePlanResponse`:**

```python
class DatePlanResponse(BaseModel):
    venue: RankedVenue
    runner_up_venues: list[RankedVenue]   # NEW — always exactly 2 items
    cards: DateCards
    compatibility: PersonCompatibility    # NEW
```

`runner_up_venues` is always length 2. With 12 venues in the catalog, `ranked[1]` and `ranked[2]` always exist — no bounds check needed.

---

### 4b. New File: `app/compatibility_engine.py`

Four deterministic scoring functions + label lookup. No LLM calls.

#### `_energy_alignment(p_a, p_b) -> int`

```
diff = abs(p_a.energy_level - p_b.energy_level)
score = max(0, 25 - diff * 6)
```

Rationale: mirrors the energy_match logic already in `matching_engine.py`. Energy diff of 0 → 25 (perfect), diff of 4 → 1 (opposite ends of scale).

#### `_interest_overlap(p_a, p_b) -> int`

Keyword adjacency mapping. Exact string match would give zero overlap even for clearly related interests (e.g. "indie music" ↔ "live music"). Use adjacency groups:

```python
INTEREST_GROUPS = [
    {"music", "indie music", "live music", "rap music", "latin music"},
    {"outdoor", "hiking", "nature", "walk"},
    {"art", "film", "photography", "design"},
    {"food", "cooking", "culinary", "korean culture", "trying new restaurants"},
    {"reading", "book", "philosophy", "history"},
    {"social", "going out", "dancing", "sports"},
]
```

Logic:
- For each group, count how many interests from p_a AND p_b both appear in that group
- Each group with representation from both personas contributes +8 points
- Base: 5. Cap: 25.
- Score = min(25, 5 + 8 * groups_with_both_sides)

#### `_values_alignment(p_a, p_b) -> int`

Same adjacency approach for values:

```python
VALUES_GROUPS = [
    {"curiosity", "intellectual curiosity", "depth", "authenticity"},
    {"honesty", "low pretense", "authenticity"},
    {"fun", "spontaneity", "energy", "confidence", "living in the moment"},
    {"adventure", "openness"},
    {"peace", "intentionality", "beauty"},
    {"loyalty"},
]
```

Logic:
- Each group with representation from both sides contributes +8 points
- Base: 5. Cap: 25.

#### `_vibe_compatibility(p_a, p_b) -> int`

Lookup table for `date_preference` pairs. Symmetric (order doesn't matter).

```python
VIBE_SCORES = {
    ("low_pressure", "low_pressure"): 25,
    ("social",       "social"):       25,
    ("culinary",     "culinary"):      25,
    ("active",       "active"):        25,
    ("low_pressure", "culinary"):      18,  # quiet dinner works
    ("low_pressure", "active"):        15,  # outdoor walk is low pressure
    ("culinary",     "active"):        15,  # food + outdoors can overlap
    ("social",       "active"):        12,
    ("social",       "culinary"):      10,
    ("social",       "low_pressure"):   8,  # highest contrast
}
```

Lookup is symmetric: normalize by sorting the two keys alphabetically before lookup. Default 8 for any unlisted pair.

#### `_label(score: int) -> str`

```python
if score >= 80: return "Highly Compatible"
if score >= 65: return "Complementary"
if score >= 50: return "Interesting Mix"
return "High Contrast"
```

#### Public function

```python
def score_person_compatibility(p_a: Persona, p_b: Persona) -> PersonCompatibility:
    breakdown = CompatibilityBreakdown(
        energy_alignment=_energy_alignment(p_a, p_b),
        interest_overlap=_interest_overlap(p_a, p_b),
        values_alignment=_values_alignment(p_a, p_b),
        vibe_compatibility=_vibe_compatibility(p_a, p_b),
    )
    total = sum([
        breakdown.energy_alignment,
        breakdown.interest_overlap,
        breakdown.values_alignment,
        breakdown.vibe_compatibility,
    ])
    return PersonCompatibility(score=total, label=_label(total), breakdown=breakdown)
```

---

### 4c. Wiring in `main.py`

```python
from app.compatibility_engine import score_person_compatibility

# inside generate_date_plan():
ranked = rank_venues_for_pair(p_a, p_b, venues)
compatibility = score_person_compatibility(p_a, p_b)
cards = generate_date_cards(p_a, p_b, ranked[0])

return DatePlanResponse(
    venue=ranked[0],
    runner_up_venues=ranked[1:3],
    cards=cards,
    compatibility=compatibility,
)
```

No other changes to `main.py`.

---

### 4d. "Why It Lost" Logic

The runner-up display needs to identify the weakest scoring dimension for each runner-up venue. This is computed **in the frontend** from the existing `score_breakdown` data already present on each `RankedVenue`. No backend change needed.

Frontend logic:
```typescript
const weakest = Object.entries(breakdown)
  .sort(([, a], [, b]) => a - b)[0]; // sort ascending, take first
// weakest[0] = dimension key, weakest[1] = score
```

Dimension label map (same as existing `breakdownLabels` in `DateCard.tsx`):
```
energy_match → "energy match"
shared_activity → "activity fit"
comfort_alignment → "comfort fit"
vibe_alignment → "vibe match"
```

Display format: `"Lost on: {label} ({score}/25)"`

---

## 5. Phase 2 — Frontend Option B (Runner-Up Venues)

**File:** `frontend/components/DateCard.tsx`

### TypeScript interface update

Add to `DatePlanResponse`:
```typescript
runner_up_venues: RankedVenue[];
```

### New inline section

Rendered at the bottom of the `DateCard` component, after the persona card grid.

**Visual design:**
- Section header: "Also Considered" in the same `text-xs font-semibold text-zinc-400 uppercase tracking-wide` style used throughout
- Two venue rows, each in a compact single-line layout:
  - Left: venue name (bold, sm) + address (text-zinc-500 xs)
  - Right: score badge (rose-100/rose-700, same pill style) + "Lost on: X (N/25)" in text-zinc-400 xs
- Background: `bg-white rounded-2xl border border-rose-100 p-4`
- Divider between the two rows: `border-t border-zinc-100`

No new component file needed — inline inside `DateCard.tsx`.

---

## 6. Phase 3 — Frontend Option C (Compatibility Banner)

**File:** `frontend/components/DateCard.tsx`

### New TypeScript interfaces

```typescript
interface CompatibilityBreakdown {
  energy_alignment: number;
  interest_overlap: number;
  values_alignment: number;
  vibe_compatibility: number;
}

interface PersonCompatibility {
  score: number;
  label: string;
  breakdown: CompatibilityBreakdown;
}
```

Add to `DatePlanResponse`:
```typescript
compatibility: PersonCompatibility;
```

### New `CompatibilityBanner` component (inline in DateCard.tsx)

Rendered as the **first element** inside the `DateCard` return — above the venue card. This is intentional: the story is "here's how compatible they are → here's where they should go."

**Visual design:**
- Background: `bg-white rounded-2xl shadow-sm border border-rose-100 p-6`
- Top row: label text left-aligned in `text-lg font-bold text-zinc-900`, score badge right-aligned `bg-rose-100 text-rose-700 font-semibold px-3 py-1 rounded-full`
- Sub-label: `"{personaAName} × {personaBName}"` in `text-sm text-zinc-500`
- Bottom: 4-column grid, same visual pattern as the venue score breakdown grid
  - Labels: "Energy" | "Interests" | "Values" | "Vibe"
  - Values: `{score}/25` in `text-sm font-semibold text-rose-700`
  - Background: `bg-rose-50 rounded-lg p-2`

**Props:** `{ compatibility: PersonCompatibility, personaAName: string, personaBName: string }`

---

## 7. Verification Checklist (Phase 4)

After all phases complete, verify manually:

- [ ] `curl POST /generate-date-plan` for Maya+Alex returns `runner_up_venues` array of length 2
- [ ] `curl POST /generate-date-plan` for Maya+Alex returns `compatibility` object with `score`, `label`, `breakdown`
- [ ] UI renders CompatibilityBanner above venue card
- [ ] CompatibilityBanner shows 4 sub-scores and a label
- [ ] "Also Considered" section shows 2 runner-up venues
- [ ] Each runner-up shows "Lost on: X (N/25)"
- [ ] Jordan+Sam produces a different compatibility label than Maya+Alex
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] No regressions to existing venue card, score breakdown, or persona cards

---

## 8. Scope Boundary — What Is Explicitly Out of Scope

- No second Claude/LLM call for any new feature
- No changes to the venue scoring logic in `matching_engine.py`
- No changes to the card generation prompt or `PersonaCard` fields
- No new API endpoints
- No database or persistence
- No deployment changes
- No new npm packages or Python packages

---

## 9. Expected Scoring for Key Pairs (Sanity Check)

| Pair | Energy | Interests | Values | Vibe | Total | Label |
|------|--------|-----------|--------|------|-------|-------|
| Maya + Alex | 25 | 13 (music group) | 21 (curiosity group) | 25 | ~84 | Highly Compatible |
| Jordan + Sam | 19 | 13 (social/music) | 13 (energy group) | 25 | ~70 | Complementary |
| Maya + Jordan | 1 | 5 | 5 | 8 | ~19 | High Contrast |
| Riley + Morgan | 13 | 13 (food+art) | 13 (openness+peace) | 15 | ~54 | Interesting Mix |

These are pre-implementation estimates. Exact values will depend on adjacency group resolution. Maya+Jordan should always produce the lowest score — that's the validation case.
