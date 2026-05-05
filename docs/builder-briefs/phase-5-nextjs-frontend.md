# Phase 5 — Next.js Frontend

**What I built:** A single-page client component — two dropdowns, a button, three UI states (loading / error / result), and a `DateCard` component that renders the full API response. Score breakdown grid showing each of the four dimensions per-venue. Responsive layout (side-by-side persona cards on desktop, stacked on mobile). 230 total lines of TypeScript + Tailwind, no external component library.

**The frontend has one job: make the backend's output visible.** Every design decision flows from that constraint.

**Key decisions:**
- **`"use client"` — client-side fetch, not Server Component.** A Server Component fetching from the FastAPI backend during SSR would block the page render on the Claude subprocess (~5s). Client-side fetch with a loading state renders the HTML shell instantly and shows a spinner while the slow part happens after the user clicks a button they chose to click.
- **Loading hint with "~5s" text.** Without it, users click and assume it's broken. Setting the right expectation keeps them on the page. Not decoration — it's UX.
- **Score breakdown grid.** The 4-cell grid (Energy/Activity/Comfort/Vibe, each X/25) makes the matching algorithm legible without clicking anywhere. You can point at the numbers during a demo and explain the algorithm directly from the UI.
- **TypeScript types live in `DateCard.tsx`, imported into `page.tsx`.** Two files, tightly coupled to the display component. No duplication without introducing a third file that would only exist to hold shared types. YAGNI.
- **Hardcode the 6 persona names.** The spec said to hardcode them, and the personas are stable configuration. Fetching a `/personas` endpoint would require an additional backend endpoint that doesn't exist and adds complexity for zero user benefit.
- **Error message from API `detail` field.** FastAPI returns `{"detail": "Persona 'unknown' not found"}`. Display that string directly — error messages in the UI exactly match the API contract, no translation layer, no risk of message drift.

**What I rejected:**
- **External component library (shadcn/ui, Radix).** Two dropdowns, a button, some cards, and text. A component library would add install friction, configuration, and dependencies that can fail silently during a demo. Pure Tailwind is the right call for a UI this size.
- **React Server Components + Suspense.** Cleaner looking but requires the backend to be reachable at build time, complicates the deployment model, and is the wrong pattern for "user triggers a slow async operation and waits for the result."

**No surprises.** The build worked first attempt, TypeScript passed, dev server came up cleanly. That's because Phases 2–4 did the hard work — the API contract was already designed, the response shapes were already Pydantic models, the endpoint was already tested. The frontend just rendered a contract that already existed.
