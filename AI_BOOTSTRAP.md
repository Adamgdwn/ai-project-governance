# AI Bootstrap Rules

## Purpose
This repository must be workable by Claude, Codex, and local coding agents
using the same operating rules.

## Change rules
- Prefer editing existing files over creating duplicate replacements.
- Keep changes small and reversible.
- Do not rename or move core files unless explicitly instructed.
- Explain new dependencies before adding them.
- Update docs when behavior, interfaces, or architecture change.

## Governance
- Read `START_HERE.md` first, then follow `docs/current-build-pathway.md`.
- Run the governance preflight before making substantial changes:
  `bash scripts/governance-preflight.sh`
- Review `project-control.yaml` for risk tier and required controls.
- Record deviations as exceptions rather than ignoring them.
- Capture the work timestamp with `date -Iseconds` and use it in material work notes, decisions, validation, and handoffs.

## Work chunking
- Work in context-window-friendly chunks.
- Each chunk should have one objective, clear input files, clear output files or behavior, and explicit validation.
- Update `docs/current-build-pathway.md` when the active chunk or next handoff changes.

## Commands
<!-- Replace these with the actual commands for this project -->
- Install: `<fill in>`
- Dev:     `<fill in>`
- Lint:    `<fill in>`
- Build:   `<fill in>`
- Test:    `<fill in>`

## Document control
- Architecture decisions go in `docs/`
- If code behavior changes, update the nearest controlled document in the same task

## Completion standard
A task is not complete until relevant validation is run or a blocker is clearly stated.
