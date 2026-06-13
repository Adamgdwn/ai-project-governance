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
- apply `docs/standards/ship-ready-engineering-standard.md` before declaring meaningful work complete
- use Graphify before broad source exploration or architecture analysis, using workspace routing plus repo-local semantic graphs for heavy active repos
- fill in project commands in `AI_BOOTSTRAP.md`
- keep work in context-window-friendly chunks
- timestamp material work, decisions, validation, and handoffs

## Current Build Pathway

Use [docs/current-build-pathway.md](docs/current-build-pathway.md) as the live build route.

Before making substantial changes:

1. Run `bash scripts/governance-preflight.sh`.
2. Review `docs/standards/README.md`.
3. Review `docs/standards/engineering-governance-by-use-case.md`.
4. Review `docs/policy/durable-development-engineering-policy.md`.
5. Review `docs/standards/ship-ready-engineering-standard.md`.
6. Review `project-control.yaml`.
7. Check `exceptions` in `project-control.yaml` and any exception records.
8. For broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, use the Graphify policy at `/home/adamgoodwin/code/Tools/graphify/docs/agent-governance.md` before reading raw source broadly. Reference `/home/adamgoodwin/code/Tools/graphify/workspace/out/graph.json` for cross-repo routing, set up repo-local Graphify when a new repo becomes active, run `/graphify /path/to/repo` from Claude Code for full semantic repo graphs on heavy active repos, and update the relevant graph after code changes.
9. Capture the work timestamp with `date -Iseconds`.
10. Work in the smallest complete chunk that can be reviewed safely.

## Agent Handoff

Update this file only when the top-level plan or handoff point changes. Put detailed step-by-step progress in `docs/current-build-pathway.md`.
