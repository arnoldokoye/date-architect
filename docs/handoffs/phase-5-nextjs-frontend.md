# Phase 5 — Next.js Frontend
**Date:** 2026-05-04
**Status:** Complete
**Commits:** *(committed after this handoff is written)*

---

## 1. What we built

**`frontend/app/page.tsx`** — A single-page client component (`"use client"`) with:

- Two `<select>` dropdowns for Person A and Person B, populated with all 6 hardcoded personas (maya/Maya, alex/Alex, jordan/Jordan, sam/Sam, riley/Riley, morgan/Morgan)
- A "Find Our Date" button that POSTs `{persona_a_id, persona_b_id}` to `http://localhost:8000/generate-date-plan`
- Three distinct UI states: loading (spinner + "~5s" hint), error (red dismissible banner), result (DateCard)
- Same-persona validation: shows an error immediately if both dropdowns select the same person, without hitting the API

**`frontend/components/DateCard.tsx`** — A display component that receives the `DatePlanResponse` and renders:

- **Venue card**: name, address, score badge (`72/100`), vibe tags as pills, notes, and a 4-cell breakdown grid showing each dimension's score out of 25 (`Energy`, `Activity`, `Comfort`, `Vibe`)
- **Two persona cards** side-by-side on sm+, stacked on mobile — each showing: name, compatibility story, venue rationale, talking points as a bulleted list, logistics

TypeScript types for the full API response shape are exported from `DateCard.tsx` and imported into `page.tsx` — no type duplication.

**Stack**: Next.js 16.2.4 (App Router, Turbopack), React 19, TypeScript 5, Tailwind CSS v4. No external component library.

**Build**: `npm run build` produces a clean Turbopack production build in 2.8s. TypeScript passes with `tsc --noEmit` (exit 0). Dev server returns HTTP 200 at `localhost:3000`.

**API smoke test confirmed**: `POST /generate-date-plan {maya, alex}` returns Elixr Coffee Roasters (score=72) with full venue + cards JSON. Both persona card `compatibility_story` fields populated with non-generic copy.

Total frontend: `page.tsx` (105 lines) + `DateCard.tsx` (125 lines).

---

## 2. The product thinking

The frontend has one job: make the backend's output visible. Every design decision flows from that constraint.

**Single page, no routing.** The product is a single interaction loop: pick two people → get a date plan. Adding pages or navigation would imply a multi-step workflow that doesn't exist yet. The UI matches the scope of the feature.

**Client component for everything.** The `"use client"` directive makes the page a browser-rendered interactive component. The alternative — a Server Component that fetches from the FastAPI backend during SSR — would look cleaner but would block the page render on the Claude subprocess (~5s). Client-side fetch with a loading state is the right pattern: the HTML shell renders instantly, and the slow part (card generation) happens after the user clicks a button they chose to click.

**Loading hint matters.** The Claude subprocess takes ~5s. Without a loading indicator, users click the button and assume it's broken. The spinner plus "~5s" text sets the right expectation and keeps them on the page. This is a real UX decision, not decoration.

**Score breakdown grid.** The 4-cell grid (Energy/Activity/Comfort/Vibe, each X/25) makes the matching algorithm legible at a glance. A user can see *why* Elixr was chosen without reading the notes. This also makes for a natural interview demo point: you can point at the numbers and explain the algorithm directly from the UI.

**Responsive layout: side-by-side cards on desktop, stacked on mobile.** The `sm:grid-cols-2` pattern is the minimum viable responsive layout. The personas cards have equivalent weight — neither is primary — so side-by-side is the right default on larger screens.

---

## 3. The decisions we made (and what we rejected)

**Decision: types live in `DateCard.tsx`, imported into `page.tsx`**

We could have put the TypeScript interfaces in a `types.ts` file, or duplicated them in each file. Since there are only two files and the types are tightly coupled to the display component, keeping them in `DateCard.tsx` and exporting what `page.tsx` needs is the minimal-duplication choice. If a third file needed these types, we'd extract to `types.ts` then.

**Decision: hardcode the 6 persona names**

The SPEC said to hardcode them. Fetching `/personas` from the backend would require an additional endpoint that doesn't exist, and the personas are stable configuration, not dynamic data. Hardcoding `PERSONAS` array in `page.tsx` is 6 lines and zero extra complexity.

**Decision: fetch directly to `http://localhost:8000`, no Next.js API route**

The task specified no Next.js API routes. This is correct for a demo: adding a Next.js API route as a proxy would add a round trip and a file with no benefit. The frontend and backend run on the same machine during the demo. For production deployment, you'd add CORS headers to the FastAPI app and optionally proxy via Next.js if you needed to hide the backend URL.

**Decision: error messages from the API response `detail` field**

FastAPI returns `{"detail": "Persona 'unknown' not found"}` on 404. We display that string directly. This means the error message in the UI exactly matches what the API documented — no translation layer, no risk of message drift.

**Decision: Tailwind v4 with `@import "tailwindcss"` syntax**

The scaffold was created with Tailwind v4 (`@tailwindcss/postcss`). We used the v4 `@import "tailwindcss"` syntax in `globals.css` and wrote v4-compatible class names throughout. The build confirmed v4 JIT scanning works correctly with the app router structure.

**Rejected: external component library (shadcn/ui, Radix)**

No external library was needed. The UI has two dropdowns, a button, some cards, and text. Adding a component library would require installation, configuration, and creates dependencies that can fail silently during a demo. Pure Tailwind for a UI this size is the right call.

**Rejected: async Server Component with suspense**

A React Server Component + Suspense boundary would have made the loading state automatic but would require the backend to be reachable at build time and would complicate the deployment model. For a demo, the client-side `useState` + `fetch` pattern is explicit, debuggable, and simple.

---

## 4. How to explain it at different depths

**30 seconds:**
"I built a single-page Next.js frontend that lets you pick two personas from dropdowns, hit 'Find Our Date', and see the full date plan rendered — venue with score and breakdown, and a personalized card for each person. It calls the FastAPI backend directly. Loading and error states are handled. The whole UI is about 230 lines of TypeScript + Tailwind, no external component library."

**2 minutes:**
"The frontend is a client component — `'use client'` — that manages three states: loading, error, and result. The loading state shows a spinner with a '~5s' hint because the Claude subprocess takes that long and without feedback users assume it's broken. The error state displays the API's `detail` field directly, which means error messages in the UI exactly match the API contract.

The DateCard component renders the full `DatePlanResponse` shape: venue name, address, score, vibe tags as pills, the notes text, and a 4-cell score breakdown grid that makes the matching algorithm legible without clicking through to any other page. The two persona cards sit side-by-side on desktop and stack on mobile.

TypeScript types for the response shape are defined once in `DateCard.tsx` and imported into `page.tsx` — no duplication. The build is clean: Turbopack production build in 2.8s, TypeScript type-check passes, dev server returns 200."

**5 minutes:**
Walk through `page.tsx` first: show the `PERSONAS` array, the state variables (personaA, personaB, loading, error, result), the `handleSubmit` function (same-persona validation → fetch → error handling → state update). Point out the `finally` block that always clears loading regardless of outcome.

Then walk through `DateCard.tsx`: show the type exports at the top, the `PersonaCardPanel` subcomponent, the breakdown grid using `Object.keys(ranked.breakdown)` with a human-readable label map. Show that the vibe tags and breakdown cells are driven directly by the API response shape — no transformation, just rendering.

End on the architecture: the frontend is purely a rendering layer. The algorithm is in `matching_engine.py`, the card copy is generated by `card_generator.py`, the HTTP contract is defined by `main.py`. The frontend renders whatever the backend returns. If you changed the scoring algorithm or the card prompt, the frontend automatically shows the updated output — no frontend changes needed.

---

## 5. Anticipated interview questions + answers

**"Why Next.js for a demo? Why not just plain HTML?"**
Three reasons: TypeScript catches type errors at compile time (the API response shape is complex and easy to mistype), Tailwind provides responsive utilities without a CSS file, and the App Router's `"use client"` model gives us a clean mental model for where state lives. The production build is also one command away from being deployable — which matters if the interviewer asks to see it live.

**"How does the loading state work?"**
`loading` is a React state variable set to `true` at the start of `handleSubmit` and `false` in the `finally` block. The spinner and button disabled state are both derived from `loading`. The `finally` ensures loading is cleared whether the request succeeds or fails — no stuck spinner possible.

**"How would you add a third persona to the comparison?"**
Add `{ id: "new_id", name: "New Name" }` to the `PERSONAS` array and add that persona to `personas.json` on the backend. The UI renders dropdowns from the array, so no structural changes needed. The `DateCards` response shape would need a `persona_c` field, which would require updating the backend models and the DateCard component's rendering logic.

**"How would you deploy this?"**
The FastAPI backend can be containerized — there's already a `Dockerfile` in the project. For the frontend, `npm run build` produces a static export that can be served by nginx or deployed to Vercel. The main production concern is CORS: you'd add `CORSMiddleware` to the FastAPI app with the frontend's origin, and update the fetch URL from `localhost:8000` to the production API URL (ideally via an environment variable like `NEXT_PUBLIC_API_URL`).

**"Why not put the API call in a Server Component?"**
The card generation takes ~5s because of the Claude subprocess. A Server Component would block rendering for the full 5s before the page loads — no loading state, no content until the backend responds. The client-side fetch pattern renders the page shell immediately, shows a spinner while the request is in flight, and displays the result when ready. That's a better user experience for a slow backend operation.

---

## 6. The sentiment

This phase had no surprising technical problems — the build worked on the first attempt, TypeScript passed, the dev server came up cleanly. That's because Phases 2–4 did the hard work: the API contract was already designed, the response shapes were already Pydantic models, and the endpoint was already tested. The frontend was just rendering a contract that already existed.

The one design decision worth dwelling on is the `"use client"` choice. It would have been tempting to reach for React Server Components + Suspense here — it's the "modern" Next.js way. But the right tool for "user triggers a slow async operation and waits for the result" is a client-side fetch with explicit state management. Server Components shine when you need to render data that exists at request time; they're the wrong fit for UI that's driven by user-initiated POST requests with ~5s latency. Using the simpler pattern means the code is easier to read, easier to debug, and less likely to surprise a reviewer unfamiliar with React Server Components.

The score breakdown grid is the part I'm most satisfied with from a product perspective. It wasn't strictly required by the spec, but the matching algorithm's four-dimension output deserves to be visible — both for demo clarity and for intellectual honesty. If someone asks "why did the algorithm choose this venue?", the grid answers that question without any further navigation.
