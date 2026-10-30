---
name: phase-learning-doc
description: After finishing any phase of the wind forecast portal (P0 to P8), write or update the beginner-friendly learning doc in docs/ explaining everything built, every calculation and every flow. Use when a phase is completed, or when the user asks to document, explain or update the learning notes.
---

# Phase learning doc

The user is a junior developer (SWE1) who wants to learn from this project. After every completed phase, write a learning doc in `docs/`.

## When
- At the end of each phase, before saying the phase is done.
- Whenever code or decisions change in a way that makes an earlier learning doc wrong: update it in the same turn.

## File
- Name: `docs/Learn - Phase <N> <Short Title>.md` (e.g. `Learn - Phase 3 Forecast Selection and Metrics.md`). Phases 0 and 1 share one file.
- Tick the phase's items in `docs/Wind Forecast Portal Phased To-Do List.md` and link the learning doc if useful.

## Style rules
- No jargon. Define every term the first time (MW, UTC, DataFrame, pure function...). Add new words to the doc's glossary.
- Short sentences. Explain why, not only what.
- Use real numbers from the real data and real runs. Never invent numbers; only quote results that were actually computed and tested.

## Required sections
1. Goal of the phase in plain words.
2. Files created or changed, and what each does.
3. The flow: step by step, what happens from input to output (diagram or numbered steps).
4. Every calculation: formula in words, then a tiny worked example with real values, then why it matters.
5. Edge cases and how they are handled.
6. Tests: what each proves.
7. Decisions and trade-offs.
8. Glossary additions.
9. "Try it yourself" exercises (2 to 3).

Keep code excerpts short and explained line by line where tricky. Verify each claim in the doc against the code or data before writing it.
