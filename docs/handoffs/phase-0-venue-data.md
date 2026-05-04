# Phase 0 — Venue Data & Persona Research
**Date:** May 3, 2026
**Status:** Complete
**Commit:** `feat(data): add 12 PSU venue graph and 6 user personas`

---

## 1. What we built

Two JSON files that form the foundation of everything the app does:

**`backend/app/data/venues.json`** — 12 real Penn State / State College venues, each classified with 8 attributes:
- `noise_level` (1-5) — how loud the place is
- `intimacy_score` (1-5) — how private / cozy vs. open / transactional it feels
- `activity_available` + `activity_type` — does the venue give you something to DO together, not just talk
- `vibe_tags` — descriptive words that capture the atmosphere
- `best_for` — what kind of pair this venue works for
- `price_tier` (1-3) — cheap, mid, or upscale
- `notes` — plain English explanation of why this venue works or doesn't for a first date

**`backend/app/data/personas.json`** — 6 sample user personas, each with:
- `energy_level` (1-5)
- `conversation_style` — thoughtful, animated, warm, reflective, outgoing, curious
- `interests` — real specific interests, not generic ones
- `values` — what they actually care about
- `comfort_with_strangers` (1-5)
- `date_preference` — one of: low_pressure, social, culinary, active

The venues we chose span the full State College spectrum:
- Quiet/low-pressure: Penn State Arboretum, Elixr Coffee, Webster's Bookstore Café
- Food/restaurant: Manna Korea, The Tavern, Allen Street Grill, Field Burger & Tap
- Unique/cocktail: Barrel 21 Distillery
- Dive bar/music: Zeno's Pub, The Phyrst
- High-energy/nightlife: Champs, The Basement

---

## 2. The product thinking

The entire point of Date Architect is that **the date is the product, not the match.** Most dating platforms — and most applicants building this feature — would start with the matching algorithm. We didn't. We started with the venues.

Why? Because no matter how good the matching is, if you send two people to Starbucks, you've built nothing. The date experience is what people remember. It's what makes them tell their friends. It's what makes them show up next time.

By building the venue graph first, we're saying: the date IS the product, and the venue is the first building block of a good date. This is founder-level sequencing — you build what the user actually experiences before you build the infrastructure that powers it.

There's also a practical reason: the venue data is what makes the demo compelling. When someone watches a 5-minute video of this feature, they don't see the matching algorithm. They see "Webster's Bookstore Café — browse vintage vinyl together" paired with a specific compatibility story. That's the moment that lands. The algorithm is just what gets you to that moment.

**The Penn State choice specifically:**
Every other applicant will demo with fake data, generic cities, or Berkeley (since that's Ditto's home campus). We built for Penn State because that's the campus you know. You've been to these bars. You know which coffee shops are quiet and which are loud. You know The Creamery is too on-campus to feel like a real date. That local knowledge is impossible to fake, and it's exactly what "customer research" means on the evaluation rubric.

There's also a strategic framing: Ditto just raised $9.2M and has explicitly said they're expanding to new campuses. By building this for Penn State, you're not just showing off a feature — you're showing them what their next campus launch looks like when someone with real local knowledge runs it. That's a much stronger story than "here's a generic demo."

---

## 3. The decisions we made (and what we rejected)

**Decision: Use a JSON file, not a database**

We could have set up PostgreSQL from the start and stored venues in a proper table. We didn't, and here's why: the venue data doesn't change during a demo. There are no writes, no transactions, no concurrency. A JSON file loaded into memory at startup is simpler, faster to build, and completely sufficient for what V1 needs. When an interviewer asks "why not a database?" the answer is: "YAGNI — you ain't gonna need it. V1 reads static local data. V2 would integrate Google Places API and a real venue graph at scale — that's when a database makes sense."

**Decision: 12 venues across wildly different vibe profiles**

We specifically chose venues that sit at opposite ends of the spectrum on noise, intimacy, and energy. The reason: the demo only works if switching between persona pairs produces visibly different venue recommendations. If all 12 venues scored similarly, the matching engine would look random. By having The Basement (noise=5, intimacy=2) sitting next to the Arboretum (noise=1, intimacy=4), the scoring differences are obvious and explainable.

**Decision: Remove The Creamery**

The original plan included The Creamery. We cut it after thinking through the user experience: it's on campus, it signals "still in school mode," and older students in particular wouldn't find it a compelling date choice. This is the kind of judgment call that only works if you actually know the campus — it's not something you could derive from a Google search.

**Decision: Include The Basement despite it being a nightclub**

The Basement breaks the mold of "first date venue" — it's a nightclub with Latin nights. We kept it because it represents a real pair type: two people who both score high on energy and comfort with strangers and share an interest in dancing. For that pair, The Basement is actually a better venue than a quiet coffee shop. Showing that the system can recommend a nightclub for the right pair and a bookstore for a different pair is what proves the matching logic is actually working.

**Decision: 6 personas with specific, real interests**

We could have made generic personas — "Person A: likes music. Person B: likes outdoor activities." We didn't, because vague data produces vague output. Maya has "Brent Faiyaz" in her interests. Morgan has "astrology." Riley has "korean culture." These details make two things happen: the Gemini-generated date cards become specific and compelling instead of generic, and the demo feels real. When you watch Maya get matched with the Arboretum and her card says something that references her specific vibe, that's the moment the audience believes the product works.

---

## 4. How to explain it at different depths

**30 seconds:**
"Before writing any code, I built the venue graph — 12 real State College spots I know from being a PSU student, each classified by noise level, intimacy, whether the venue gives you something to do together, and what kind of pair it works for. I also built 6 sample user personas with real specific interests. This is the data the whole feature runs on."

**2 minutes:**
"Phase 0 was about getting the data right before touching code. I built two things: a venue graph of 12 real Penn State locations, and a set of user personas. For the venues, I classified each one on attributes that actually matter for a first date — not just 'good restaurant' but things like: how loud is it, does it give you something to do together so there's no awkward silence, what kind of pair does it work for. I used State College specifically because I'm a PSU student — I know firsthand which spots work and which don't. The Creamery, for example, is iconic but it's on campus and feels like you're still in school mode, so I cut it. For the personas, I made them specific — real interests, real values — because generic personas produce generic output from the AI. You want Maya to have Brent Faiyaz in her profile so her date card actually sounds like it was written for her."

**5 minutes:**
Start with the product rationale — the date is the product, not the match, so we built what the user actually experiences before building the infrastructure. Then explain the Penn State angle as both authentic customer research and a strategic demo choice (Ditto is expanding to new campuses). Walk through 2-3 venue decisions that show judgment: why we cut The Creamery, why we kept The Basement, why the spectrum of venues matters for the demo. Then explain the persona design philosophy: specific interests produce specific AI output, and the demo pairs were chosen to produce maximally different results so the matching logic is obviously working.

---

## 5. Anticipated interview questions + answers

**"Why did you start with venue data before writing any code?"**
Because the venue is what the user experiences. The algorithm is invisible — the date card is what they see. Starting with venue data meant I could immediately visualize what the output would look like for different pairs, which let me validate the product idea before building infrastructure. It's the same reason a product designer builds wireframes before writing backend code — you want to know the end state before you build the path to get there.

**"How did you decide which attributes to classify venues on?"**
I thought about what actually makes a first date good or bad. Noise level matters because conversation is the whole point. Intimacy score matters because meeting a stranger at a crowded bar feels different than a quiet corner booth. Whether there's a shared activity matters because something to do together kills awkward silence — that's why Korean BBQ hotpot works so well for nervous first-daters. I could have added more attributes but I wanted to keep V1 clean and explainable. V2 would pull real venue data from Google Places and use an LLM to classify attributes from review text at scale.

**"Why Penn State specifically? Wouldn't Berkeley be more relevant for Ditto?"**
Two reasons. First, authentic customer research: I actually know these venues. That local knowledge shows up in the data — I can explain why The Creamery got cut, why The Basement works for a specific pair type, why Barrel 21 is worth the trip off campus. You can't fake that from a search engine. Second, strategic framing: Ditto just raised $9.2M and is expanding to new campuses. Penn State is one of the biggest college campuses in the country. This demo is literally showing them what a PSU campus launch would look like.

**"Your venue data is hardcoded in a JSON file. How would this scale?"**
V2 replaces the static JSON with a Google Places API integration. You'd pull venues near a campus centroid, classify their attributes using an LLM analyzing review text, and store them in a PostgreSQL venue table. You'd also add a feedback loop where post-date ratings update venue scores over time. The JSON approach for V1 was deliberate — it's a demo, not production, and the goal was to validate the matching logic and demo quality before building the data pipeline.

**"How did you decide on 6 personas? Why these specific ones?"**
I designed them to produce interesting and obviously different results when paired. Maya and Alex are both quiet and introverted — they should get Webster's or the Arboretum. Jordan and Sam are both high-energy social types — they should get The Basement or a sports bar. Riley is a foodie — she should get Manna Korea. Morgan is earthy and listens to Brent Faiyaz — she should get the Arboretum. The goal was that when you switch pairs in the demo, the output changes noticeably — that's how you prove the matching logic is doing real work, not just randomly assigning venues.

---

## 6. The sentiment

Going into this phase, the biggest risk was building a demo that felt generic — 5 fake personas with fake venues and AI-generated text that sounds like every other AI demo. We made a deliberate choice to ground everything in real, specific, local data before writing a single line of code.

The Penn State angle felt right immediately. Not because it was convenient, but because it genuinely strengthens the submission — it turns "I built a demo" into "I built this for my campus because I'm the target user." That's a different conversation in an interview.

We were also thinking about the evaluation rubric the whole time. "Customer research" is one of their five criteria, and it's the one most applicants will phone in. By doing Phase 0 first — before any scaffolding, before any code — we made customer research the foundation of the project, not an afterthought we bolt on in the video.

The decision to cut The Creamery is a small thing but worth noting: it's the kind of judgment that only comes from real knowledge. Any LLM would tell you The Creamery is a great Penn State date spot. It's technically true. But anyone who's actually been to State College knows it's too on-campus to feel like you're intentionally planning something. That's the difference between desk research and actual customer knowledge, and it's the kind of thing that shows up in interviews when someone pushes you on your decisions.

One thing we were intentional about: making The Basement a legitimate option for the right pair. It would have been easy to only include "safe" date venues — coffee shops, restaurants, nice bars. But real people go on real dates at real nightclubs. Excluding The Basement would have made the system less honest about how people actually date in college. The matching engine should be able to recommend a club for a pair that would genuinely love it. That's not a bug — that's the product working.
