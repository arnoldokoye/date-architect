import pytest
from unittest.mock import patch
from app.models import Persona, Venue, RankedVenue, ScoreBreakdown, DateCards, PersonaCard
from app.card_generator import generate_date_cards, _build_prompt


@pytest.fixture
def sample_pair():
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
def sample_ranked_venue():
    venue = Venue(
        id="websters", name="Webster's Bookstore Café", address="133 E Beaver Ave",
        maps_url="https://maps.app.goo.gl/placeholder",
        noise_level=1, intimacy_score=4, activity_available=True,
        activity_type="browsing books together",
        vibe_tags=["intellectual", "cozy", "quiet"],
        best_for=["introverts", "thoughtful pairs"],
        price_tier=1, notes="Great back corner seating."
    )
    return RankedVenue(
        venue=venue, score=82,
        score_breakdown=ScoreBreakdown(
            energy_match=22, shared_activity=22, comfort_alignment=20, vibe_alignment=18
        )
    )


def test_build_prompt_contains_persona_names(sample_pair, sample_ranked_venue):
    p_a, p_b = sample_pair
    prompt = _build_prompt(p_a, p_b, sample_ranked_venue)
    assert "Maya" in prompt
    assert "Alex" in prompt


def test_build_prompt_contains_venue_name(sample_pair, sample_ranked_venue):
    p_a, p_b = sample_pair
    prompt = _build_prompt(p_a, p_b, sample_ranked_venue)
    assert "Webster's Bookstore Café" in prompt


def test_generate_date_cards_returns_date_cards(sample_pair, sample_ranked_venue):
    p_a, p_b = sample_pair
    mock_response = {
        "maya": {
            "compatibility_story": "You both love film and bring different lenses to it.",
            "venue_rationale": "Webster's lets you browse together — low pressure, high potential.",
            "talking_points": ["Ask about the last film that changed how they think.", "What book would they reread?", "Favorite director and why."],
            "logistics": "Meet at the front entrance at 7pm. Back corner is quietest. Coffee is $3-5."
        },
        "alex": {
            "compatibility_story": "Maya thinks deeply about stories the same way you do.",
            "venue_rationale": "A bookstore is a rare first-date choice — it signals you're not basic.",
            "talking_points": ["Ask what genre they'd live in.", "Last film that surprised them.", "Philosophy they actually live by."],
            "logistics": "Meet at the front entrance at 7pm. Order a pour-over, take your time."
        }
    }

    with patch("app.card_generator._call_gemini", return_value=mock_response):
        result = generate_date_cards(p_a, p_b, sample_ranked_venue)

    assert isinstance(result, DateCards)
    assert isinstance(result.persona_a, PersonaCard)
    assert isinstance(result.persona_b, PersonaCard)


def test_generate_date_cards_card_fields_populated(sample_pair, sample_ranked_venue):
    p_a, p_b = sample_pair
    mock_response = {
        "maya": {
            "compatibility_story": "Story here.",
            "venue_rationale": "Rationale here.",
            "talking_points": ["Point 1", "Point 2", "Point 3"],
            "logistics": "Logistics here."
        },
        "alex": {
            "compatibility_story": "Story here.",
            "venue_rationale": "Rationale here.",
            "talking_points": ["Point 1", "Point 2"],
            "logistics": "Logistics here."
        }
    }

    with patch("app.card_generator._call_gemini", return_value=mock_response):
        result = generate_date_cards(p_a, p_b, sample_ranked_venue)

    assert len(result.persona_a.compatibility_story) > 0
    assert len(result.persona_a.talking_points) >= 2
    assert len(result.persona_b.logistics) > 0
