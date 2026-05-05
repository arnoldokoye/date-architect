# Phase 0 — Venue Data & Persona Research

**What I built:** Two JSON files — 12 real Penn State / State College venues and 6 sample user personas — that the entire app runs on. Every venue is classified on 8 attributes: noise level, intimacy score, whether there's a shared activity, vibe tags, what kind of pair it suits, price tier, and a plain-English explanation of why it works or doesn't for a first date. Every persona has energy level, conversation style, specific interests (not generic ones), values, comfort with strangers, and a date preference type.

**Why I started here:** The date is the product, not the match. Most applicants building a date-planning feature start with the algorithm. I didn't — I started with what the user actually experiences. If the venue is wrong, nothing else matters. Starting here also meant I could immediately visualize what the output would look like for different pairs, which validated the product idea before writing infrastructure. Building a demo on real, specific, local data you know firsthand is also just better customer research than feeding an LLM a city name.

**Penn State specifically:** I'm a PSU student. I've been to these places. That local knowledge is in the data — I know The Creamery is too on-campus to feel like you're intentionally planning something, and I know The Basement's Latin nights work for high-energy pairs even though it's technically a nightclub. You can't fake that from a Google search. It also made the demo strategically useful: Ditto is expanding to new campuses, and Penn State is one of the biggest in the country. This demo is what a PSU campus launch looks like when someone with real local knowledge runs it.

**Key decisions:**
- **JSON over database.** No writes, no transactions, no concurrency. A JSON file loaded at startup is simpler, faster, and completely sufficient. The first question is always "how does the demo work?" not "how does it scale?" Adding PostgreSQL to a venue-data demo is over-engineering that hurts readability.
- **12 venues spanning the full spectrum.** Quiet/low-pressure, restaurant, cocktail bar, dive bar, nightlife. The demo only works if switching persona pairs produces visibly different results. That requires venues that score differently enough to make the algorithm obviously meaningful.
- **Specific persona interests.** Maya has Brent Faiyaz in her profile. Riley has Korean culture. Vague interests produce vague AI output. Specificity is what makes the generated date cards feel real.

**What I rejected:**
- **The Creamery** — iconic Penn State spot, too on-campus, feels like you're still in school mode. Cut.
- **Generic/hypothetical city** — would have been faster to set up but would have lost the authentic customer research angle entirely.

**Surprise:** The Basement (a nightclub) ended up being the correct recommendation for the right pair type. It would have been tempting to only include "safe" date venues — coffee shops, restaurants, quiet bars. Including a nightclub and making it legitimately the best pick for high-energy social pairs made the system more honest about how people actually date in college.
