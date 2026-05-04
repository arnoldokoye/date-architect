from pydantic import BaseModel


class Venue(BaseModel):
    id: str
    name: str
    address: str
    maps_url: str
    noise_level: int        # 1-5
    intimacy_score: int     # 1-5
    activity_available: bool
    activity_type: str | None
    vibe_tags: list[str]
    best_for: list[str]
    price_tier: int         # 1-3
    notes: str


class Persona(BaseModel):
    id: str
    name: str
    energy_level: int           # 1-5
    conversation_style: str
    interests: list[str]
    values: list[str]
    comfort_with_strangers: int  # 1-5
    date_preference: str


class ScoreBreakdown(BaseModel):
    energy_match: int
    shared_activity: int
    comfort_alignment: int
    vibe_alignment: int


class CompatibilityBreakdown(BaseModel):
    energy_alignment: int    # 0–25
    interest_overlap: int    # 0–25
    values_alignment: int    # 0–25
    vibe_compatibility: int  # 0–25


class PersonCompatibility(BaseModel):
    score: int   # 0–100
    label: str   # "Highly Compatible" | "Complementary" | "Interesting Mix" | "High Contrast"
    breakdown: CompatibilityBreakdown


class RankedVenue(BaseModel):
    venue: Venue
    score: int
    score_breakdown: ScoreBreakdown


class PersonaCard(BaseModel):
    compatibility_story: str
    venue_rationale: str
    talking_points: list[str]
    logistics: str


class DateCards(BaseModel):
    persona_a: PersonaCard
    persona_b: PersonaCard


class DatePlanResponse(BaseModel):
    venue: RankedVenue
    runner_up_venues: list[RankedVenue]   # always exactly 2 items
    cards: DateCards
    compatibility: PersonCompatibility


class GenerateDateRequest(BaseModel):
    persona_a_id: str
    persona_b_id: str
