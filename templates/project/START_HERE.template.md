# Start Here

Last Updated: YYYY-MM-DD
Status: draft
Owner: Project Owner

## Current Plan

This is the first file an agent should read when starting work in this project. Keep it short, current, and pointed at the active build path.

Current priorities:

- confirm project scope and governance level
- fill in project commands in `AI_BOOTSTRAP.md`
- keep work in context-window-friendly chunks
- timestamp material work, decisions, validation, and handoffs

## Current Build Pathway

Use [docs/current-build-pathway.md](docs/current-build-pathway.md) as the live build route.

Before making substantial changes:

1. Run `bash scripts/governance-preflight.sh`.
2. Review `project-control.yaml`.
3. Check `exceptions` in `project-control.yaml` and any exception records.
4. Capture the work timestamp with `date -Iseconds`.
5. Work in the smallest complete chunk that can be reviewed safely.

## Agent Handoff

Update this file only when the top-level plan or handoff point changes. Put detailed step-by-step progress in `docs/current-build-pathway.md`.
