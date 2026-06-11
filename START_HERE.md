# Start Here

Last Updated: 2026-05-31
Status: active
Owner: Adam Goodwin

## Current Plan

This repository maintains the governance framework used to create and upgrade governed projects. Start each work session by reading this file, then follow the current build pathway.

Current priorities:

- keep the project scaffold safe to apply to new and existing builds
- classify projects by use case before development begins
- make the durable development policy part of every governed build
- make ship-readiness evidence part of every governed build
- make context hygiene, scoped reads, compaction, and handoff practices available to every governed build
- make Graphify the first orientation tool before broad source exploration or architecture analysis
- make agent work traceable with timestamps
- keep planning and implementation in context-window-friendly chunks
- preserve copy-if-missing behavior for existing projects

## Current Build Pathway

Use [docs/current-build-pathway.md](docs/current-build-pathway.md) as the live build route.

Before making substantial changes:

1. Run `bash automation/governance_check.sh /path/to/project`.
2. Review `docs/standards/README.md`.
3. Review `docs/standards/engineering-governance-by-use-case.md`.
4. Review `docs/policy/durable-development-engineering-policy.md`.
5. Review `docs/standards/ship-ready-engineering-standard.md`.
6. Review `project-control.yaml`.
7. Check `exceptions` in `project-control.yaml` and any exception records.
8. For broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, use the Graphify policy at `/home/adamgoodwin/code/GRAPHIFY_AGENT_GOVERNANCE.md` before reading raw source broadly. Reference `/home/adamgoodwin/code/graphify-out/graph.json`, set up repo-local Graphify when a new repo becomes active, and update the relevant graph after code changes.
9. Capture the work timestamp with `date -Iseconds`.
10. Work in the smallest complete chunk that can be reviewed safely.

## Agent Handoff

Agents should leave enough context for the next session to resume without rereading the entire repo. Update the current build pathway when the active plan, status, risks, or next chunk changes.
