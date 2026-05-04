import pytest
from app.models import Persona, Venue, ScoreBreakdown, RankedVenue
from app.matching_engine import score_venue_for_pair, rank_venues_for_pair

@pytest.fixture
def introvert_pair():
    p_a = Persona(
        id="maya", name="Maya", energy_level=2, conversation_style="thoughtful",
        interests=["film", "philosophy"], values=["depth", "authenticity"],
        comfort_with_strangers=2, date_preference="low_pressure"
    )
    p_b = Persona(
        id="alex", name="Alex", energy_level=2, conversation_style="reflective",
        interests=["reading", "film"], values=["curiosity", "honesty"],
        comfort_with_strangers=2, date_preference="low_pressure"
    )
    return p_a, p_b

@pytest.fixture
def extrovert_pair():
    p_a = Persona(
        id="jordan", name="Jordan", energy_level=5, conversation_style="animated",
        interests=["sports", "going out"], values=["fun", "spontaneity"],
        comfort_with_strangers=5, date_preference="social"
    )
    p_b = Persona(
        id="sam", name="Sam", energy_level=4, conversation_style="outgoing",
        interests=["music", "bars"], values=["energy", "connection"],
        comfort_with_strangers=4, date_preference="social"
    )
    return p_a, p_b

@pytest.fixture
def quiet_venue():
    return Venue(
        id="websters", name="Webster's Bookstore Café", address="133 E Beaver Ave",
        maps_url="https://maps.app.goo.gl/placeholder",
        noise_level=1, intimacy_score=4, activity_available=True,
        activity_type="browsing books together", vibe_tags=["intellectual", "cozy", "quiet"],
        best_for=["introverts", "thoughtful pairs", "low pressure"],
        price_tier=1, notes="Great back corner seating."
    )

@pytest.fixture
def loud_bar_venue():
    return Venue(
        id="ugly_mug", name="The Ugly Mug", address="220 W College Ave",
        maps_url="https://maps.app.goo.gl/placeholder",
        noise_level=4, intimacy_score=2, activity_available=False,
        activity_type=None, vibe_tags=["social", "lively", "bars"],
        best_for=["outgoing pairs", "social", "adventurous"],
        price_tier=2, notes="High energy, good for confident extroverts."
    )

def test_score_venue_returns_ranked_venue(introvert_pair, quiet_venue):
    p_a, p_b = introvert_pair
    result = score_venue_for_pair(p_a, p_b, quiet_venue)
    assert isinstance(result, RankedVenue)
    assert 0 <= result.score <= 100
    assert isinstance(result.score_breakdown, ScoreBreakdown)

def test_quiet_venue_scores_higher_for_introverts(introvert_pair, quiet_venue,
loud_bar_venue):
    p_a, p_b = introvert_pair
    quiet_score = score_venue_for_pair(p_a, p_b, quiet_venue).score
    loud_score = score_venue_for_pair(p_a, p_b, loud_bar_venue).score
    assert quiet_score > loud_score

def test_social_venue_scores_higher_for_extroverts(extrovert_pair, quiet_venue,
loud_bar_venue):
    p_a, p_b = extrovert_pair
    quiet_score = score_venue_for_pair(p_a, p_b, quiet_venue).score
    loud_score = score_venue_for_pair(p_a, p_b, loud_bar_venue).score
    assert loud_score > quiet_score

def test_rank_venues_returns_sorted_list(introvert_pair, quiet_venue, loud_bar_venue):
    p_a, p_b = introvert_pair
    ranked = rank_venues_for_pair(p_a, p_b, [quiet_venue, loud_bar_venue])
    assert len(ranked) == 2
    assert ranked[0].score >= ranked[1].score

def test_rank_venues_top_pick_for_introverts_is_quiet(introvert_pair, quiet_venue,
loud_bar_venue):
    p_a, p_b = introvert_pair
    ranked = rank_venues_for_pair(p_a, p_b, [loud_bar_venue, quiet_venue])
    assert ranked[0].venue.id == "websters"
