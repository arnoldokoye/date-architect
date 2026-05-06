import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.card_generator import generate_date_cards
from app.compatibility_engine import score_person_compatibility
from app.db import get_outcome_stats, init_db, record_outcome
from app.matching_engine import rank_venues_for_pair
from app.models import (
    DatePlanResponse,
    GenerateDateRequest,
    Persona,
    RecordOutcomeRequest,
    RecordOutcomeResponse,
    Venue,
)

load_dotenv()

_data: dict = {}
_PRECOMPUTED_DIR = Path(__file__).parent / "data" / "precomputed"


def _load_from_cache(a_id: str, b_id: str) -> DatePlanResponse | None:
    path = _PRECOMPUTED_DIR / f"{a_id}__{b_id}.json"
    if path.exists():
        return DatePlanResponse.model_validate_json(path.read_text())
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = Path(__file__).parent / "data"
    personas_raw = json.loads((data_dir / "personas.json").read_text())
    venues_raw = json.loads((data_dir / "venues.json").read_text())
    _data["personas"] = {p["id"]: Persona(**p) for p in personas_raw}
    _data["venues"] = [Venue(**v) for v in venues_raw]
    init_db()
    yield
    _data.clear()


app = FastAPI(lifespan=lifespan)

_allowed_origins = ["http://localhost:3000"]
_frontend_url = os.environ.get("FRONTEND_URL")
if _frontend_url:
    _allowed_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.post("/generate-date-plan", response_model=DatePlanResponse)
def generate_date_plan(req: GenerateDateRequest) -> DatePlanResponse:
    personas = _data["personas"]
    venues = _data["venues"]

    p_a = personas.get(req.persona_a_id)
    if p_a is None:
        raise HTTPException(status_code=404, detail=f"Persona '{req.persona_a_id}' not found")

    p_b = personas.get(req.persona_b_id)
    if p_b is None:
        raise HTTPException(status_code=404, detail=f"Persona '{req.persona_b_id}' not found")

    cached = _load_from_cache(req.persona_a_id, req.persona_b_id)
    if cached:
        return cached

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="No cached result for this pair and ANTHROPIC_API_KEY is not set.")

    ranked = rank_venues_for_pair(p_a, p_b, venues)
    compatibility = score_person_compatibility(p_a, p_b)
    cards = generate_date_cards(p_a, p_b, ranked[0])

    return DatePlanResponse(
        venue=ranked[0],
        runner_up_venues=ranked[1:3],
        cards=cards,
        compatibility=compatibility,
    )


@app.get("/personas", response_model=list[Persona])
def get_personas() -> list[Persona]:
    return list(_data["personas"].values())


@app.post("/record-outcome", response_model=RecordOutcomeResponse)
def record_outcome_endpoint(req: RecordOutcomeRequest) -> RecordOutcomeResponse:
    personas = _data["personas"]
    if req.persona_a_id == req.persona_b_id:
        raise HTTPException(status_code=400, detail="persona_a_id and persona_b_id must be different")
    if req.persona_a_id not in personas:
        raise HTTPException(status_code=404, detail=f"Persona '{req.persona_a_id}' not found")
    if req.persona_b_id not in personas:
        raise HTTPException(status_code=404, detail=f"Persona '{req.persona_b_id}' not found")
    row_id = record_outcome(req.persona_a_id, req.persona_b_id, req.venue_id, req.outcome)
    return RecordOutcomeResponse(recorded=True, id=row_id)


@app.get("/outcome-stats")
def outcome_stats() -> dict:
    return get_outcome_stats()
