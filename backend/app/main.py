import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.card_generator import generate_date_cards
from app.matching_engine import rank_venues_for_pair
from app.models import (
    DatePlanResponse,
    GenerateDateRequest,
    Persona,
    Venue,
)

_data: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = Path(__file__).parent / "data"
    personas_raw = json.loads((data_dir / "personas.json").read_text())
    venues_raw = json.loads((data_dir / "venues.json").read_text())
    _data["personas"] = {p["id"]: Persona(**p) for p in personas_raw}
    _data["venues"] = [Venue(**v) for v in venues_raw]
    yield
    _data.clear()


app = FastAPI(lifespan=lifespan)


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

    ranked = rank_venues_for_pair(p_a, p_b, venues)
    cards = generate_date_cards(p_a, p_b, ranked[0])

    return DatePlanResponse(venue=ranked[0], cards=cards)
