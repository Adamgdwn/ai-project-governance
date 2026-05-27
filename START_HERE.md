# Start Here

Last Updated: 2026-05-27
Status: active
Owner: Adam Goodwin

## Current Plan

This repository maintains the governance framework used to create and upgrade governed projects. Start each work session by reading this file, then follow the current build pathway.

Current priorities:

- keep the project scaffold safe to apply to new and existing builds
- make agent work traceable with timestamps
- keep planning and implementation in context-window-friendly chunks
- preserve copy-if-missing behavior for existing projects

## Current Build Pathway

Use [docs/current-build-pathway.md](docs/current-build-pathway.md) as the live build route.

Before making substantial changes:

1. Run `bash automation/governance_check.sh /path/to/project`.
2. Review `project-control.yaml`.
3. Check `exceptions` in `project-control.yaml` and any exception records.
4. Capture the work timestamp with `date -Iseconds`.
5. Work in the smallest complete chunk that can be reviewed safely.

## Agent Handoff

Agents should leave enough context for the next session to resume without rereading the entire repo. Update the current build pathway when the active plan, status, risks, or next chunk changes.
