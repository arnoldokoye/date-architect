from app.models import Persona, Venue, ScoreBreakdown, RankedVenue


def _energy_match_score(p_a: Persona, p_b: Persona, venue: Venue) -> int:
    avg_energy = (p_a.energy_level + p_b.energy_level) / 2
    mismatch = abs(avg_energy - venue.noise_level)
    return max(0, 25 - int(mismatch * 6))


def _shared_activity_score(p_a: Persona, p_b: Persona, venue: Venue) -> int:
    if not venue.activity_available:
        return 8
    activity_keywords = (venue.activity_type or "").lower()
    interest_pool = set(i.lower() for i in p_a.interests + p_b.interests)
    overlap_signals = [
        "book" in activity_keywords and any("read" in i or "book" in i for i in interest_pool),
        "food" in activity_keywords and any("food" in i or "cook" in i or "culinary" in i for i in interest_pool),
        "ice cream" in activity_keywords,
        "art" in activity_keywords and any("art" in i or "film" in i or "design" in i for i in interest_pool),
        "walk" in activity_keywords and any("hike" in i or "outdoor" in i or "nature" in i for i in interest_pool),
    ]
    bonus = sum(8 for signal in overlap_signals if signal)
    return min(25, 10 + bonus)


def _comfort_alignment_score(p_a: Persona, p_b: Persona, venue: Venue) -> int:
    # Only penalise when the venue is MORE intimate than the pair is comfortable with.
    # A high-comfort pair at a low-intimacy bar shouldn't be penalised.
    avg_comfort = (p_a.comfort_with_strangers + p_b.comfort_with_strangers) / 2
    excess_intimacy = max(0.0, venue.intimacy_score - avg_comfort)
    return max(0, 25 - int(excess_intimacy * 5))


def _vibe_alignment_score(p_a: Persona, p_b: Persona, venue: Venue) -> int:
    preference_to_vibes: dict[str, list[str]] = {
        "low_pressure": ["casual", "quiet", "low pressure", "iconic", "lighthearted", "cozy"],
        "adventurous": ["adventurous", "unique", "lively", "spontaneous"],
        "active": ["outdoor", "active", "walk"],
        "culinary": ["food", "culinary", "foodie", "upscale"],
        "social": ["social", "lively", "bar", "energy"],
    }

    def pref_score(pref: str) -> int:
        desired = preference_to_vibes.get(pref, [])
        matches = sum(1 for tag in venue.vibe_tags if any(d in tag.lower() for d in desired))
        return min(12, matches * 4)

    return min(25, pref_score(p_a.date_preference) + pref_score(p_b.date_preference))


def score_venue_for_pair(p_a: Persona, p_b: Persona, venue: Venue) -> RankedVenue:
    breakdown = ScoreBreakdown(
        energy_match=_energy_match_score(p_a, p_b, venue),
        shared_activity=_shared_activity_score(p_a, p_b, venue),
        comfort_alignment=_comfort_alignment_score(p_a, p_b, venue),
        vibe_alignment=_vibe_alignment_score(p_a, p_b, venue),
    )
    total = (
        breakdown.energy_match
        + breakdown.shared_activity
        + breakdown.comfort_alignment
        + breakdown.vibe_alignment
    )
    return RankedVenue(venue=venue, score=total, score_breakdown=breakdown)


def rank_venues_for_pair(p_a: Persona, p_b: Persona, venues: list[Venue]) -> list[RankedVenue]:
    scored = [score_venue_for_pair(p_a, p_b, v) for v in venues]
    return sorted(scored, key=lambda r: r.score, reverse=True)
