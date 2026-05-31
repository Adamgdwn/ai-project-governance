# Start Here

Last Updated: YYYY-MM-DD
Status: draft
Owner: Project Owner

## Current Plan

This is the first file an agent should read when starting work in this project. Keep it short, current, and pointed at the active build path.

Current priorities:

- confirm project scope and governance level
- confirm use-case classification in `project-control.yaml`
- apply `docs/policy/durable-development-engineering-policy.md` during implementation
- fill in project commands in `AI_BOOTSTRAP.md`
- keep work in context-window-friendly chunks
- timestamp material work, decisions, validation, and handoffs

## Current Build Pathway

Use [docs/current-build-pathway.md](docs/current-build-pathway.md) as the live build route.

Before making substantial changes:

1. Run `bash scripts/governance-preflight.sh`.
2. Review `docs/standards/engineering-governance-by-use-case.md`.
3. Review `docs/policy/durable-development-engineering-policy.md`.
4. Review `project-control.yaml`.
5. Check `exceptions` in `project-control.yaml` and any exception records.
6. Capture the work timestamp with `date -Iseconds`.
7. Work in the smallest complete chunk that can be reviewed safely.

## Agent Handoff

Update this file only when the top-level plan or handoff point changes. Put detailed step-by-step progress in `docs/current-build-pathway.md`.
