# Phase 0 — Venue Data & Persona Research

Before writing a single line of code I spent a day just thinking about what the feature actually needs to be. The brief was "build a first feature for a dating app." The obvious move is to build something about the match — compatibility scoring, conversation starters, icebreaker prompts. I didn't want to do that.

My take: the match is table stakes. What Ditto users actually remember is whether the date was good. The venue is what makes or breaks it — if you send two people to Starbucks, you've built nothing. So I started by building the venue graph before touching any infrastructure.

I chose Penn State because I go here and I've been to these places. That matters more than it sounds. "Local knowledge" in a generic demo usually means someone scraped Google Maps. Mine shows up in actual judgment calls as shown below:

- I cut The Creamery from the venue list even though it's the most iconic PSU spot. It's on campus, it feels like you're still in school mode, it's not a real date. Any LLM would tell you it's a great Penn State date idea. It's not.
- I kept The Basement (a nightclub) as a legitimate recommendation for the right pair type — two people who are both high-energy and comfortable physically. Excluding it would've made the system less honest. The match should be able to recommend a club when a club is actually right.
- Manna Korean BBQ opened in March 2026 — I included it specifically because it's new and buzzy and the shared cooking format kills awkward silence on a first date. That's not something you'd know from a search.

The persona design was intentional too. I made them specific — Morgan has Brent Faiyaz in her profile, Riley lists Korean culture as an interest — because vague data produces vague AI output. When you read the generated date cards later, you can trace every specific detail back to something real in the persona data.

The Penn State angle wasn't just authenticity for its own sake. Ditto just raised $9.2M and is explicitly expanding to new campuses. PSU has 90,000+ students. This demo is literally what a PSU campus launch looks like when someone who knows the campus runs it.
