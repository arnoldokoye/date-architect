from app.models import CompatibilityBreakdown, Persona, PersonCompatibility

INTEREST_GROUPS: list[set[str]] = [
    {"music", "indie music", "live music", "rap music", "latin music"},
    {"outdoor", "hiking", "nature"},
    {"art", "film", "photography", "design"},
    {"food", "cooking", "culinary", "korean culture", "trying new restaurants"},
    {"reading", "book", "philosophy", "history"},
    {"social", "going out", "dancing", "sports", "basketball"},
]

VALUES_GROUPS: list[set[str]] = [
    {"curiosity", "intellectual curiosity", "depth", "authenticity"},
    {"honesty", "low pretense", "authenticity"},
    {"fun", "spontaneity", "energy", "confidence", "living in the moment"},
    {"adventure", "openness"},
    {"peace", "intentionality", "beauty"},
]

# Asymmetric pairs only — identical pairs return 25 via early return
VIBE_SCORES: dict[tuple[str, str], int] = {
    ("culinary",     "low_pressure"): 18,
    ("active",       "low_pressure"): 15,
    ("active",       "culinary"):     15,
    ("active",       "social"):       12,
    ("culinary",     "social"):       10,
    ("low_pressure", "social"):        8,
}


def _energy_alignment(p_a: Persona, p_b: Persona) -> int:
    diff = abs(p_a.energy_level - p_b.energy_level)
    return max(0, 25 - diff * 6)


def _interest_overlap(p_a: Persona, p_b: Persona) -> int:
    a = {i.lower() for i in p_a.interests}
    b = {i.lower() for i in p_b.interests}
    groups_with_both = sum(1 for g in INTEREST_GROUPS if a & g and b & g)
    return min(25, 5 + groups_with_both * 8)


def _values_alignment(p_a: Persona, p_b: Persona) -> int:
    a = {v.lower() for v in p_a.values}
    b = {v.lower() for v in p_b.values}
    groups_with_both = sum(1 for g in VALUES_GROUPS if a & g and b & g)
    return min(25, 5 + groups_with_both * 8)


def _vibe_compatibility(p_a: Persona, p_b: Persona) -> int:
    if p_a.date_preference == p_b.date_preference:
        return 25
    key = tuple(sorted([p_a.date_preference, p_b.date_preference]))
    return VIBE_SCORES.get(key, 8)  # type: ignore[arg-type]


def _label(score: int) -> str:
    if score >= 80:
        return "Highly Compatible"
    if score >= 65:
        return "Complementary"
    if score >= 50:
        return "Interesting Mix"
    return "High Contrast"


def score_person_compatibility(p_a: Persona, p_b: Persona) -> PersonCompatibility:
    breakdown = CompatibilityBreakdown(
        energy_alignment=_energy_alignment(p_a, p_b),
        interest_overlap=_interest_overlap(p_a, p_b),
        values_alignment=_values_alignment(p_a, p_b),
        vibe_compatibility=_vibe_compatibility(p_a, p_b),
    )
    total = (
        breakdown.energy_alignment
        + breakdown.interest_overlap
        + breakdown.values_alignment
        + breakdown.vibe_compatibility
    )
    return PersonCompatibility(score=total, label=_label(total), breakdown=breakdown)
