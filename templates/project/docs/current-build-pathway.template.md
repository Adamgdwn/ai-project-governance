# Current Build Pathway

Last Updated: YYYY-MM-DD
Status: draft
Owner: Technical Lead

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume.

## Required Work Pattern

For each substantial work session:

1. Start from `START_HERE.md`.
2. Run `bash scripts/governance-preflight.sh`.
3. Review `docs/standards/README.md`.
4. Review `docs/standards/engineering-governance-by-use-case.md`.
5. Review `docs/policy/durable-development-engineering-policy.md`.
6. Review `docs/standards/ship-ready-engineering-standard.md`.
7. Review `project-control.yaml` and open exceptions.
8. Capture a timestamp with `date -Iseconds`.
9. Define the next build chunk in this document.
10. Complete and validate that chunk before expanding scope.
11. Update this document with status, validation, and the next chunk.

## Chunking Standard

Each build chunk should be small enough to fit comfortably in an agent context window.

A good chunk has:

- one objective
- a target completion state
- clear acceptance criteria
- clear input files or documents
- clear output files or behavior
- explicit validation steps
- an explicit stop condition or escalation trigger
- a timestamped status note

Use second-level Markdown headings for active and planned chunks so they are easy to scan. Spell out the chunk number in the heading:

```md
## Chunk One - Short Objective
## Chunk Two - Short Objective
```

Continue the pattern for later chunks: `## Chunk Three - ...`, `## Chunk Four - ...`, and so on.

Avoid mixing unrelated code, governance, deployment, and product decisions in one chunk unless the change cannot be validated any other way.

## Active Path

| Step | Status | Timestamp | Owner | Notes |
|------|--------|-----------|-------|-------|
| Define current chunk | active | YYYY-MM-DD | Technical Lead | Replace this row with the current project-specific build step, target completion state, acceptance criteria, and stop condition. |
| Validate chunk | pending | YYYY-MM-DD | Technical Lead | Record commands run and results. |
| Handoff next chunk | pending | YYYY-MM-DD | Technical Lead | Leave the next agent a narrow, actionable start point. |

## Chunk One - Current Objective

Status: planned

Completion target: Draft complete / Task complete / Integration complete / Release ready / Blocked

Objective:

Acceptance criteria:

- [ ] Criterion one
- [ ] Criterion two

Inputs:

- `START_HERE.md`
- `docs/current-build-pathway.md`

Outputs:

- Replace with the files, behavior, evidence, or decision this chunk should produce.

Validation:

- Replace with the commands, tests, reviews, or manual checks required for this chunk.

Stop condition:

- Stop when the completion target is reached, when acceptance criteria are unclear, or when repeated attempts stop producing new evidence.

Known gaps:

- Replace with unverified items, deferred hardening, or risks.

Next action:

- Replace with the next bounded step.

## Timestamp Rule

Use ISO-style timestamps for work notes, handoffs, decisions, exceptions, release notes, and validation records. Prefer the local command:

```bash
date -Iseconds
```

## Validation Log

| Timestamp | Command | Result | Notes |
|-----------|---------|--------|-------|
| YYYY-MM-DD | `bash scripts/governance-preflight.sh` | pending | Replace with the real validation result. |

## Next Handoff

Next agent should begin at `START_HERE.md`, then use this file to identify the current chunk, target completion state, acceptance criteria, stop condition, validation status, known gaps, and next bounded action.
