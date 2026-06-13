# Agent Instructions

This repository is the source of truth for development and deployment governance.

## Default Working Rule

Before making substantial code or configuration changes in any governed project:

1. read `START_HERE.md`
2. review `docs/current-build-pathway.md`
3. review `docs/standards/README.md`
4. review `docs/standards/engineering-governance-by-use-case.md`
5. review `docs/policy/durable-development-engineering-policy.md`
6. review `docs/standards/ship-ready-engineering-standard.md`
7. run the governance check
8. review the project's `project-control.yaml`
9. check for open exceptions that affect the requested work
10. capture a timestamp with `date -Iseconds`
11. only then begin implementation

## Required Preflight Command

Agents should run:

```bash
bash automation/governance_check.sh /path/to/project
```

If the target project does not yet contain governance files, agents should bootstrap it first:

```bash
bash automation/bootstrap_project.sh /path/to/project <project-type>
```

## Agent Behavior Expectations

- Follow the framework by default.
- Use `docs/standards/README.md` as the standards map for coding and release work.
- Confirm the requested work matches the project's `use_case.primary` classification.
- Apply the durable development standard: build the smallest useful thing in the safest durable way.
- Treat Definition of Shipped as a separate evidence gate before declaring meaningful work complete.
- Use `docs/standards/context-hygiene-standard.md` for long sessions, scoped repository reads, compaction, and handoffs.
- Do not silently ignore missing governance files.
- Record deviations as explicit exceptions.
- Escalate if a request increases risk, autonomy, money handling, or sensitive data exposure.
- Treat machine checks as a baseline, not a substitute for judgment.
- Work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
- Define the target completion state for each meaningful chunk: `Draft complete`, `Task complete`, `Integration complete`, `Release ready`, or `Blocked`.
- Project completion is a human decision. Agents may report only bounded completion states when the documented criteria and verification evidence support that label.
- Stop when the chunk's definition of done is met, when its stop condition is reached, or when repeated attempts stop producing new evidence.
- In `docs/current-build-pathway.md`, label active and planned chunks as second-level headings with spelled-out numbers, such as `## Chunk One - Short Objective`, `## Chunk Two - Short Objective`, and `## Chunk Three - Short Objective`.
- Timestamp material work, decisions, validation, and handoffs.
- Keep `docs/current-build-pathway.md` current when the active plan or next chunk changes.

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

Use the canonical Graphify governance file:

`/home/adamgoodwin/code/Tools/graphify/docs/agent-governance.md`

Before broad source exploration, architecture analysis, dependency tracing, or cross-repo planning, use Graphify first and reference the workspace graph at:

`/home/adamgoodwin/code/Tools/graphify/workspace/out/graph.json`

Use the workspace graph for cross-repo routing. When a new repo becomes active, set up repo-local Graphify with:

```bash
graphify-setup-project /path/to/repo
```

For full semantic repo graphs in heavy active repos, run `/graphify /path/to/repo` from Claude Code. Current Graphify skills can use Claude Code subagents when no Gemini key is set, so policy should constrain token burn through per-repo scope, caching, strict ignores, and cheap updates rather than hard-coding a provider or extraction backend.

Use Graphify to orient, then inspect only the files needed for the actual change. After code changes, update the relevant graph with `graphify update . --no-cluster`, or update the workspace graph for cross-repo work. Preserve existing secret-handling rules: do not index, print, summarize, or commit secrets or environment files.

## Supported Project Types

- application
- website
- service
- internal-tool
- automation
- infrastructure
- documentation
- agent
