# Claude project instructions

Read `./START_HERE.md` first, then `./AI_BOOTSTRAP.md`, and follow them as the canonical project rule files. Use `./docs/standards/README.md` as the standards map for coding and release work. Use `./docs/standards/engineering-governance-by-use-case.md` for control guidance only; do not override the selected `risk_tier` or `governance_level`. Review `./docs/policy/durable-development-engineering-policy.md` before meaningful implementation work. Review `./docs/standards/ship-ready-engineering-standard.md` before declaring meaningful work complete. Build the smallest useful thing in the safest durable way, and do not treat "works locally" as complete.

Additional rules:
- Do not move or rename core files unless explicitly asked.
- Prefer small diffs over large rewrites.
- When changing behavior, update docs in the same task.

## Fundamentals-First AI Coding

Build fundamentals-first software. AI speed does not make bad code cheap.

Before meaningful coding, reach shared understanding. Use consistent domain language. Prefer deep modules with simple interfaces over shallow pass-through layers.

Let feedback loops set the pace: types, tests, linting, runtime checks, and user-visible validation.

Design interfaces deliberately, then implement in small vertical slices.

Avoid flimsy pass-through layers, generic helpers, premature abstractions, swallowed errors, untyped blobs, duplicated business rules, hidden production assumptions, and fake validation claims.

When you see weak design, flag it and propose the smallest safe improvement instead of rewriting the project.

Every change should make the next correct change easier.
