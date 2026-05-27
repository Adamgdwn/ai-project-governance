# Agent Instructions

Before making substantial code or configuration changes in this repository:

1. read `START_HERE.md`
2. review `docs/current-build-pathway.md`
3. run the governance preflight check
4. review `project-control.yaml`
5. note any open exceptions relevant to the work
6. capture a timestamp with `date -Iseconds`
7. proceed only after the project passes preflight or any gaps are explicitly accepted

## Preflight

```bash
bash scripts/governance-preflight.sh
```

## Working Rules

- Follow the repository standards by default.
- Do not silently skip required documentation or controls.
- Record justified deviations as exceptions.
- Reassess governance when risk, autonomy, data sensitivity, or money movement changes.
- Keep work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
- Timestamp material work, decisions, validation, and handoffs.
- Update `docs/current-build-pathway.md` when the active plan, status, or next chunk changes.
