# Phase 6 — Demo Polish

**What I built:** Full README rewrite — architecture ASCII diagram, exact run commands for both servers, a Maya+Alex example output showing the score table and a sample talking point. No source code changes; this phase was about making the project legible to someone cloning it for the first time.

**Why this phase matters:** A project that works but can't be read is half a project. The README is the first thing a hiring engineer sees. It should answer three questions in under 60 seconds: what does this do, how do I run it, and what does the output look like. The previous README didn't.

**Key decisions:**
- **ASCII architecture diagram instead of prose.** A diagram shows the two-stage pipeline (algorithm → LLM) faster than describing it. It also makes the handoff boundary visible — you can see exactly where the matching engine stops and the card generator starts.
- **Example output in the README.** A table showing Maya+Alex → Elixr Coffee (72/100) with the dimension breakdown is more convincing than "the system picks a personalized venue." Show the output, not just the claim.
- **`docs/builder-briefs/` instead of long internal handoffs.** The original development handoffs were written agent-to-agent (exhaustive, procedural). This phase introduced a parallel set of hiring-manager-facing docs that cover what was built, why, what was decided, and what was surprising — without the procedural "here's what the next agent should do" scaffolding.
