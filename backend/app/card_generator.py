import json
import subprocess
from app.models import Persona, RankedVenue, PersonaCard, DateCards


def _build_prompt(p_a: Persona, p_b: Persona, ranked_venue: RankedVenue) -> str:
    venue = ranked_venue.venue
    return f"""You are generating personalized date cards for two people who have been matched by an AI dating service.

MATCH DETAILS:
Person A: {p_a.name}
- Energy level: {p_a.energy_level}/5
- Conversation style: {p_a.conversation_style}
- Interests: {', '.join(p_a.interests)}
- Values: {', '.join(p_a.values)}
- Date preference: {p_a.date_preference}

Person B: {p_b.name}
- Energy level: {p_b.energy_level}/5
- Conversation style: {p_b.conversation_style}
- Interests: {', '.join(p_b.interests)}
- Values: {', '.join(p_b.values)}
- Date preference: {p_b.date_preference}

SELECTED VENUE: {venue.name}
Address: {venue.address}
Vibe: {', '.join(venue.vibe_tags)}
Activity: {venue.activity_type or 'conversation'}
Price: {'$' * venue.price_tier}
Why this venue was chosen: {venue.notes}
Compatibility score: {ranked_venue.score}/100

TASK:
Generate a personalized date card for EACH person. Each card must:
1. compatibility_story: 2-3 sentences explaining why THIS person is a good match for them. Be specific to their interests and values. Not generic.
2. venue_rationale: 1-2 sentences on why THIS venue was chosen for THIS specific pair. Reference their actual interests.
3. talking_points: Exactly 3 conversation topics grounded in their real shared or complementary interests. NOT generic icebreakers. Each should be a specific question or prompt.
4. logistics: 2-3 practical sentences. Include: where to meet (venue entrance), suggested arrival time, what to order or do, practical tip.

Return ONLY a raw JSON object (no markdown, no code fences) with keys "{p_a.id}" and "{p_b.id}", each containing the 4 fields above.
Write warmly but concisely. No fluff. Make the person feel like this date was designed specifically for them."""


def _call_claude(prompt: str) -> dict:
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=120,
        stdin=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed: {result.stderr.strip()}")

    text = result.stdout.strip()

    # Strip markdown code fences if the model wraps output in them
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop opening fence (```json or ```) and closing fence (```)
        inner = lines[1:] if lines[-1].strip() == "```" else lines[1:]
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner)

    return json.loads(text)


def generate_date_cards(p_a: Persona, p_b: Persona, ranked_venue: RankedVenue) -> DateCards:
    prompt = _build_prompt(p_a, p_b, ranked_venue)
    raw = _call_claude(prompt)

    def parse_card(data: dict) -> PersonaCard:
        return PersonaCard(
            compatibility_story=data["compatibility_story"],
            venue_rationale=data["venue_rationale"],
            talking_points=data["talking_points"],
            logistics=data["logistics"],
        )

    return DateCards(
        persona_a=parse_card(raw[p_a.id]),
        persona_b=parse_card(raw[p_b.id]),
    )
