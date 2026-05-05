# Phase 1 — Project Scaffold

The scaffold phase is boring to explain but the decisions here shape everything downstream.

The main call was writing Pydantic models before any logic. Before there was a matching engine or a card generator or an API, I defined what every object in the system looks like: `Venue`, `Persona`, `ScoreBreakdown`, `RankedVenue`, `PersonaCard`, `DatePlanResponse`. The full type contract, locked in before a single algorithm was written.

This isn't premature — it's sequencing. If the matching engine returns a `RankedVenue` and the API expects something slightly different, you find out at demo time in the worst case, or through confusing bugs in the best case. Models first means any mismatch is caught by Pydantic at startup, not while you're screen-recording.

One specific call worth noting: `activity_type` is nullable (`str | None`) rather than defaulting to an empty string. Some venues don't have a shared activity — you just talk. An empty string would silently slip through into the Claude prompt as "Activity: " which is meaningless. `None` is explicit; the card generator checks for it and substitutes `"conversation"`. Small thing, but it's the kind of thing that bites you later if you don't think about it early.

I added Docker Compose at this stage rather than the end. The usual pattern is to dockerize as a final step, which is painful — you discover path issues and env var gaps after the code is all written. Starting with Docker means every commit is already deployable and you're forced to think about configuration injection before you've accidentally hardcoded anything.

The scoring model uses four equal-weight dimensions at 25 points each summing to 100. I could've weighted them differently — give energy_match 40%, downweight vibe. I kept them equal because there's no real data to justify any particular weighting. When someone asks why energy match and vibe match are weighted the same, "I don't have user data to justify any other choice" is the right answer. You tune weights after you have feedback, not before.
