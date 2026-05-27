# Current Build Pathway

Last Updated: 2026-05-27
Status: active
Owner: Technical Lead

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume.

## Required Work Pattern

For each substantial work session:

1. Start from `START_HERE.md`.
2. Run the governance preflight for the target project.
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
| Add start/pathway governance baseline | complete | 2026-05-27T08:59:36-06:00 | Codex session | Added `START_HERE.md`, `docs/current-build-pathway.md`, timestamp rules, and context-friendly chunk guidance to scaffold and checks. |
| Validate governance framework | complete | 2026-05-27T08:59:36-06:00 | Codex session | Repo governance, shell syntax, Python syntax, fresh scaffold, and safe upgrade checks passed. |
| Handoff existing-build upgrade path | complete | 2026-05-27T08:59:36-06:00 | Codex session | Existing builds can receive missing files through `automation/change_control.py` copy-if-missing manifests. |

## Timestamp Rule

Use ISO-style timestamps for work notes, handoffs, decisions, exceptions, release notes, and validation records. Prefer the local command:

```bash
date -Iseconds
```

## Validation Log

| Timestamp | Command | Result | Notes |
|-----------|---------|--------|-------|
| 2026-05-27T08:59:36-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| 2026-05-27T08:59:36-06:00 | `bash -n ...` | pass | Shell syntax passed for scaffold, governance, launcher, and template scripts. |
| 2026-05-27T08:59:36-06:00 | `python3 -m py_compile ...` | pass | Python syntax passed for changed automation entry points. |
| 2026-05-27T08:59:36-06:00 | temporary scaffold and preflight | pass | Fresh application scaffold included the new baseline files and passed preflight. |
| 2026-05-27T08:59:36-06:00 | temporary change-control propose/apply | pass | Existing file was preserved; missing start/pathway files were created through manifest apply. |

## Next Handoff

Next agent should begin at `START_HERE.md`. A useful next chunk would be auditing real existing governed projects and applying reviewed manifests where `START_HERE.md` or `docs/current-build-pathway.md` are missing.
