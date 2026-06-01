# Claude project instructions

This repository is the governance source for all projects on this machine.
It is not an application project.

Rules:
- Read `START_HERE.md` first, then follow `AI_BOOTSTRAP.md`.
- Use `docs/standards/engineering-governance-by-use-case.md` for control guidance only; do not override the selected `risk_tier` or `governance_level`.
- Review `docs/policy/durable-development-engineering-policy.md` before meaningful implementation work.
- Build the smallest useful thing in the safest durable way, and do not treat "works locally" as complete.
- Do not treat this directory as a build target.
- Use templates in `templates/project/` to scaffold new projects.
- Use scripts in `automation/` to bootstrap and validate governed projects.
- Do not modify standards or templates without explicit instruction.
- The canonical reading order is in README.md.

## Fundamentals-First AI Coding

Build fundamentals-first software. AI speed does not make bad code cheap.

Before meaningful coding, reach shared understanding. Use consistent domain language. Prefer deep modules with simple interfaces over shallow pass-through layers.

Let feedback loops set the pace: types, tests, linting, runtime checks, and user-visible validation.

Design interfaces deliberately, then implement in small vertical slices.

Avoid flimsy pass-through layers, generic helpers, premature abstractions, swallowed errors, untyped blobs, duplicated business rules, hidden production assumptions, and fake validation claims.

When you see weak design, flag it and propose the smallest safe improvement instead of rewriting the project.

Every change should make the next correct change easier.
