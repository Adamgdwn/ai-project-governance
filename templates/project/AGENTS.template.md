# Agent Instructions

Before making substantial code or configuration changes in this repository:

1. read `START_HERE.md`
2. review `docs/current-build-pathway.md`
3. review `docs/standards/engineering-governance-by-use-case.md`
4. review `docs/policy/durable-development-engineering-policy.md`
5. run the governance preflight check
6. review `project-control.yaml`
7. note any open exceptions relevant to the work
8. capture a timestamp with `date -Iseconds`
9. proceed only after the project passes preflight or any gaps are explicitly accepted

## Preflight

```bash
bash scripts/governance-preflight.sh
```

## Working Rules

- Follow the repository standards by default.
- Confirm the requested work matches the project's `use_case.primary` classification.
- Apply the durable development standard: build the smallest useful thing in the safest durable way.
- Do not silently skip required documentation or controls.
- Record justified deviations as exceptions.
- Reassess governance when risk, autonomy, data sensitivity, or money movement changes.
- Keep work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
- In `docs/current-build-pathway.md`, label active and planned chunks as second-level headings with spelled-out numbers, such as `## Chunk One - Short Objective`, `## Chunk Two - Short Objective`, and `## Chunk Three - Short Objective`.
- Timestamp material work, decisions, validation, and handoffs.
- Update `docs/current-build-pathway.md` when the active plan, status, or next chunk changes.

## Fundamentals-First AI Coding

Build fundamentals-first software. AI speed does not make bad code cheap.

Before meaningful coding, reach shared understanding. Use consistent domain language. Prefer deep modules with simple interfaces over shallow pass-through layers.

Let feedback loops set the pace: types, tests, linting, runtime checks, and user-visible validation.

Design interfaces deliberately, then implement in small vertical slices.

Avoid flimsy pass-through layers, generic helpers, premature abstractions, swallowed errors, untyped blobs, duplicated business rules, hidden production assumptions, and fake validation claims.

When you see weak design, flag it and propose the smallest safe improvement instead of rewriting the project.

Every change should make the next correct change easier.
