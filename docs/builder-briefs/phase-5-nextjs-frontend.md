# Phase 5 — Next.js Frontend

Single page. Two dropdowns, a button, three states (loading / error / result). The frontend has one job: make the backend's output visible.

The main design decision was using a client component (`"use client"`) with a standard fetch, not a React Server Component. The card generation takes a few seconds. A Server Component would block the entire page render on that wait — you'd see nothing until the backend responds. Client-side fetch renders the shell instantly and shows a spinner while the slow part happens. That's the right pattern when the user triggers the slow operation.

I added "~5s" to the loading text. Without it, users click and assume the app is broken. It's not decoration.

The score breakdown grid — four cells showing Energy/Activity/Comfort/Vibe, each X/25 — was worth adding even though the spec didn't require it. The venue score means more when you can see why it got that score. During a demo you can point at the cells and explain the algorithm directly from the UI, which is useful.

TypeScript types are defined in `DateCard.tsx` and imported into `page.tsx`. There are only two files and the types are tightly coupled to the display component — no reason to create a third file just to hold shared types. When a third file actually needs them, that's when you extract.

The fetch hits `http://localhost:8000` directly. No Next.js API route proxy. The spec said no API routes, and the frontend and backend run on the same machine during the demo. Adding a proxy layer just for the sake of it would be complexity with no benefit.

The `PersonaProfileCard` component in `page.tsx` shows each persona's energy level, interests, and values before you generate the plan. I added this because it makes the demo tell a story — you can see the two people, understand who they are, and then watch the system make a decision about them. Without it the page is just two dropdowns. With it you actually understand what the algorithm is working with.
