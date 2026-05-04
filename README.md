# Date Architect

A persona-aware date experience engine that matches two people to the ideal State College venue using a four-dimension compatibility scorer and generates personalized date cards via Claude AI.

---

## Architecture

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

---

## How to Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- `claude` CLI authenticated (`claude --version` should work)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# API running at http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# UI running at http://localhost:3000
```

Open **http://localhost:3000**, select two personas, and click **Find Our Date**.

---

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

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```
