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
