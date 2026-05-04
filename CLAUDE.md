# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Persistent Build Plan (`steps.md`)

**Every non-trivial project gets a `steps.md` at the root. Maintain it across sessions.**

The plan is the durable memory of the project. A fresh LLM with zero context should be able to read `steps.md` and continue the work without asking what we're building, why, or how.

**Structure of `steps.md`:**

1. **Context block at the top** — short paragraph(s) covering:
   - *What we're building* (the product, the user, the workflow).
   - *Design philosophy* (the non-negotiables — stack constraints, what's deliberately excluded, style rules).
   - *Stack* (languages, deps allowed/forbidden, build tooling — or lack thereof).
   - *Current state* (what's done, where the entry point lives, where examples live).
   - *Working agreement* (the loop: small step → verify → pass or fix).

2. **Phased step list** — flat checkboxes, grouped by phase. Each step is:
   - Small enough to finish in one sitting (~30 min). If bigger, split it.
   - Ends with a concrete verify command or visual check.
   - Phrased as one outcome, not a bundle. "Add edge labels" is a step; "Add edge labels and improve layout" is two.

3. **Definition of done** — one sentence describing the v1 end state, so the trajectory is obvious.

**Working the plan:**
- Before starting work, re-read the context block. Don't drift from the philosophy.
- Do one step at a time. Implement → tell the user how to test → wait for pass/fail → fix or move on.
- Mark steps `[x]` as they pass. Update the context block's "current state" line when a phase completes.
- New ideas mid-project go *into the plan as new steps*, not into the current step. Don't bundle scope.
- If the plan becomes wrong (architectural pivot, scrapped feature), edit the plan first — then code.

**The plan file is part of the deliverable.** Treat edits to it with the same care as code: surgical, intentional, no speculative steps.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, clarifying questions come before implementation rather than after mistakes, and a new contributor (human or LLM) can pick up the project from `steps.md` alone.


Glossary:
- lg = looks good, go to next step