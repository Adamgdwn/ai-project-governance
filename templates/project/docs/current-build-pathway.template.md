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
3. Review `project-control.yaml` and open exceptions.
4. Capture a timestamp with `date -Iseconds`.
5. Define the next build chunk in this document.
6. Complete and validate that chunk before expanding scope.
7. Update this document with status, validation, and the next chunk.

## Chunking Standard

Each build chunk should be small enough to fit comfortably in an agent context window.

A good chunk has:

- one objective
- clear input files or documents
- clear output files or behavior
- explicit validation steps
- a timestamped status note

Avoid mixing unrelated code, governance, deployment, and product decisions in one chunk unless the change cannot be validated any other way.

## Active Path

| Step | Status | Timestamp | Owner | Notes |
|------|--------|-----------|-------|-------|
| Define current chunk | active | YYYY-MM-DD | Technical Lead | Replace this row with the current project-specific build step. |
| Validate chunk | pending | YYYY-MM-DD | Technical Lead | Record commands run and results. |
| Handoff next chunk | pending | YYYY-MM-DD | Technical Lead | Leave the next agent a narrow, actionable start point. |

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

Next agent should begin at `START_HERE.md`, then use this file to identify the current chunk and validation status.
