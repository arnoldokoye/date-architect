from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import DateCards, PersonaCard


@pytest.fixture
def mock_cards():
    card = PersonaCard(
        compatibility_story="They share a love of quiet spaces and deep conversation.",
        venue_rationale="Elixr is calm, cozy, and perfect for an unhurried first date.",
        talking_points=["What book changed how you see the world?", "Favourite film from the last year?", "Coffee order as a personality test — what's yours?"],
        logistics="Meet at the front entrance on 15th St. Arrive around 7pm. Order the single origin pour-over.",
    )
    return DateCards(persona_a=card, persona_b=card)


@pytest.fixture
def client(mock_cards):
    with patch("app.main.generate_date_cards", return_value=mock_cards):
        with TestClient(app) as c:
            yield c


def test_generate_date_plan_returns_200(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "maya", "persona_b_id": "alex"})
    assert resp.status_code == 200
    body = resp.json()
    assert "venue" in body
    assert "cards" in body


def test_generate_date_plan_venue_fields(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "maya", "persona_b_id": "alex"})
    venue = resp.json()["venue"]
    assert isinstance(venue["venue"]["name"], str)
    assert len(venue["venue"]["name"]) > 0
    assert 0 <= venue["score"] <= 100


def test_generate_date_plan_cards_fields(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "maya", "persona_b_id": "alex"})
    cards = resp.json()["cards"]
    assert len(cards["persona_a"]["compatibility_story"]) > 0
    assert len(cards["persona_b"]["compatibility_story"]) > 0


def test_generate_date_plan_unknown_persona_returns_404(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "unknown", "persona_b_id": "alex"})
    assert resp.status_code == 404


def test_generate_date_plan_has_runner_up_venues(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "maya", "persona_b_id": "alex"})
    body = resp.json()
    assert "runner_up_venues" in body
    assert len(body["runner_up_venues"]) == 2
    for rv in body["runner_up_venues"]:
        assert "score" in rv
        assert "venue" in rv
        assert "score_breakdown" in rv


def test_generate_date_plan_has_compatibility(client):
    resp = client.post("/generate-date-plan", json={"persona_a_id": "maya", "persona_b_id": "alex"})
    body = resp.json()
    assert "compatibility" in body
    compat = body["compatibility"]
    assert "score" in compat
    assert "label" in compat
    assert "breakdown" in compat
    assert 0 <= compat["score"] <= 100
    assert compat["label"] in {"Highly Compatible", "Complementary", "Interesting Mix", "High Contrast"}


def test_get_personas_returns_all_personas(client):
    resp = client.get("/personas")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 6
    for p in data:
        assert "id" in p
        assert "name" in p
        assert "energy_level" in p
        assert "interests" in p
        assert "values" in p
        assert "date_preference" in p


def test_record_outcome_returns_200(client):
    resp = client.post("/record-outcome", json={
        "persona_a_id": "maya",
        "persona_b_id": "alex",
        "venue_id": "elixr_coffee",
        "outcome": "great_date",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["recorded"] is True
    assert isinstance(body["id"], int)


def test_record_outcome_invalid_outcome_returns_422(client):
    resp = client.post("/record-outcome", json={
        "persona_a_id": "maya",
        "persona_b_id": "alex",
        "venue_id": "elixr_coffee",
        "outcome": "bad_value",
    })
    assert resp.status_code == 422


def test_record_outcome_unknown_persona_returns_404(client):
    resp = client.post("/record-outcome", json={
        "persona_a_id": "unknown",
        "persona_b_id": "alex",
        "venue_id": "elixr_coffee",
        "outcome": "went",
    })
    assert resp.status_code == 404


def test_record_outcome_same_persona_returns_400(client):
    resp = client.post("/record-outcome", json={
        "persona_a_id": "maya",
        "persona_b_id": "maya",
        "venue_id": "elixr_coffee",
        "outcome": "went",
    })
    assert resp.status_code == 400


def test_outcome_stats_returns_200(client):
    resp = client.get("/outcome-stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_outcomes" in body
    assert "by_venue" in body
    assert "by_outcome" in body
