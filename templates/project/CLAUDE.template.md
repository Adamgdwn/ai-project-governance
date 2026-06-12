# Claude project instructions

Read `./START_HERE.md` first, then `./AI_BOOTSTRAP.md`, and follow them as the canonical project rule files. Use `./docs/standards/README.md` as the standards map for coding and release work. Use `./docs/standards/engineering-governance-by-use-case.md` for control guidance only; do not override the selected `risk_tier` or `governance_level`. Review `./docs/policy/durable-development-engineering-policy.md` before meaningful implementation work. Review `./docs/standards/ship-ready-engineering-standard.md` before declaring meaningful work complete. Use `./docs/standards/context-hygiene-standard.md` for long sessions, scoped repository reads, compaction, and handoffs. Build the smallest useful thing in the safest durable way, and do not treat "works locally" as complete.

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

## Context Hygiene

Operate with strict context hygiene. Keep active context minimal, relevant, current, and recoverable.

Work in clear phases. Summarize at phase boundaries. Compact or reset before quality degrades. Re-state critical constraints after compaction.

Narrow file scope before reading. Prefer targeted diffs and specific files over whole-repo exploration.

Treat tokens as a budget, but do not skip required governance, security, architecture, or task-critical reading.

## Graphify Policy

Use the canonical Graphify governance file at `/home/adamgoodwin/code/GRAPHIFY_AGENT_GOVERNANCE.md`.

Before broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, use Graphify first and reference `/home/adamgoodwin/code/graphify-out/graph.json`. Use the workspace graph for cross-repo routing. When a new repo becomes active, set up repo-local Graphify with `graphify-setup-project /path/to/repo`.

For full semantic repo graphs in heavy active repos, run `/graphify /path/to/repo` from Claude Code. Current Graphify skills can use Claude Code subagents when no Gemini key is set, so policy should constrain token burn through per-repo scope, caching, strict ignores, and cheap updates rather than hard-coding a provider or extraction backend.

After code changes, update the relevant graph with `graphify update . --no-cluster --force`, or update the workspace graph for cross-repo work.

Preserve existing secret-handling rules: do not index, print, summarize, or commit secrets or environment files.
