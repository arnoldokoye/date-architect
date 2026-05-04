import pytest
from app.models import Persona, PersonCompatibility, CompatibilityBreakdown
from app.compatibility_engine import (
    score_person_compatibility,
    _energy_alignment,
    _interest_overlap,
    _values_alignment,
    _vibe_compatibility,
)


@pytest.fixture
def maya():
    return Persona(
        id="maya", name="Maya", energy_level=2, conversation_style="thoughtful",
        interests=["film", "philosophy", "reading", "indie music"],
        values=["depth", "authenticity", "intellectual curiosity"],
        comfort_with_strangers=2, date_preference="low_pressure",
    )


@pytest.fixture
def alex():
    return Persona(
        id="alex", name="Alex", energy_level=2, conversation_style="reflective",
        interests=["craft beer", "live music", "history", "hiking"],
        values=["honesty", "low pretense", "curiosity"],
        comfort_with_strangers=3, date_preference="low_pressure",
    )


@pytest.fixture
def jordan():
    return Persona(
        id="jordan", name="Jordan", energy_level=5, conversation_style="animated",
        interests=["sports", "going out", "rap music", "basketball"],
        values=["fun", "spontaneity", "loyalty"],
        comfort_with_strangers=5, date_preference="social",
    )


def test_energy_alignment_identical_energy():
    p_a = Persona(id="a", name="A", energy_level=3, conversation_style="x",
                  interests=[], values=[], comfort_with_strangers=3, date_preference="social")
    p_b = Persona(id="b", name="B", energy_level=3, conversation_style="x",
                  interests=[], values=[], comfort_with_strangers=3, date_preference="social")
    assert _energy_alignment(p_a, p_b) == 25


def test_energy_alignment_max_diff():
    p_a = Persona(id="a", name="A", energy_level=1, conversation_style="x",
                  interests=[], values=[], comfort_with_strangers=3, date_preference="social")
    p_b = Persona(id="b", name="B", energy_level=5, conversation_style="x",
                  interests=[], values=[], comfort_with_strangers=3, date_preference="social")
    assert _energy_alignment(p_a, p_b) == max(0, 25 - 4 * 6)  # 1


def test_interest_overlap_no_shared_groups(maya, jordan):
    # maya: film/philosophy/reading/indie music  jordan: sports/going out/rap/basketball
    # Only overlap: music group (indie music + rap music)
    score = _interest_overlap(maya, jordan)
    assert score == 13  # 5 base + 1 group * 8


def test_interest_overlap_shared_music_and_reading(maya, alex):
    # music group: indie music + live music ✓
    # reading group: reading/philosophy + history ✓
    score = _interest_overlap(maya, alex)
    assert score == 21  # 5 + 2*8


def test_vibe_compatibility_identical_preference(maya, alex):
    # both low_pressure
    assert _vibe_compatibility(maya, alex) == 25


def test_vibe_compatibility_high_contrast(maya, jordan):
    # low_pressure + social → 8
    assert _vibe_compatibility(maya, jordan) == 8


def test_score_person_compatibility_returns_model(maya, alex):
    result = score_person_compatibility(maya, alex)
    assert isinstance(result, PersonCompatibility)
    assert isinstance(result.breakdown, CompatibilityBreakdown)
    assert 0 <= result.score <= 100


def test_maya_alex_highly_compatible(maya, alex):
    result = score_person_compatibility(maya, alex)
    assert result.score >= 80
    assert result.label == "Highly Compatible"


def test_maya_jordan_high_contrast(maya, jordan):
    result = score_person_compatibility(maya, jordan)
    assert result.score < 50
    assert result.label == "High Contrast"
