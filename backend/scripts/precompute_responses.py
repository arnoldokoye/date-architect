#!/usr/bin/env python3
"""
Run once from the backend/ directory:
    python scripts/precompute_responses.py

Requires: source venv/bin/activate && claude --version (auth must be valid)
Outputs:  app/data/precomputed/{persona_a}__{persona_b}.json  (30 files)
"""
import json
import sys
from itertools import permutations
from pathlib import Path

# Ensure app/ is importable when run from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.card_generator import generate_date_cards
from app.compatibility_engine import score_person_compatibility
from app.matching_engine import rank_venues_for_pair
from app.models import DatePlanResponse, Persona, Venue

DATA_DIR = Path(__file__).parent.parent / "app" / "data"
OUT_DIR = DATA_DIR / "precomputed"
OUT_DIR.mkdir(exist_ok=True)

personas_raw = json.loads((DATA_DIR / "personas.json").read_text())
venues_raw = json.loads((DATA_DIR / "venues.json").read_text())

personas: dict[str, Persona] = {p["id"]: Persona(**p) for p in personas_raw}
venues: list[Venue] = [Venue(**v) for v in venues_raw]

pairs = list(permutations(personas.keys(), 2))  # 30 ordered pairs
print(f"Generating {len(pairs)} pairs...")

for i, (a_id, b_id) in enumerate(pairs, 1):
    out_path = OUT_DIR / f"{a_id}__{b_id}.json"
    if out_path.exists():
        print(f"  [{i:02d}/{len(pairs)}] {a_id} x {b_id} — already exists, skipping")
        continue

    print(f"  [{i:02d}/{len(pairs)}] {a_id} x {b_id} — generating...", end="", flush=True)
    p_a = personas[a_id]
    p_b = personas[b_id]

    ranked = rank_venues_for_pair(p_a, p_b, venues)
    compatibility = score_person_compatibility(p_a, p_b)
    cards = generate_date_cards(p_a, p_b, ranked[0])

    response = DatePlanResponse(
        venue=ranked[0],
        runner_up_venues=ranked[1:3],
        cards=cards,
        compatibility=compatibility,
    )
    out_path.write_text(response.model_dump_json(indent=2))
    print(f" done ({response.compatibility.score}/100, venue: {response.venue.venue.name})")

print(f"\nAll done. Files written to {OUT_DIR}")
