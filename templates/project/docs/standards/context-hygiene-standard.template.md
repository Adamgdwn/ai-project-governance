# Context Hygiene Standard

Document type: supporting engineering standard
Status: active
Owner: Project owner or human technical lead
Audience: coding agents, human coders, reviewers, and project owners
Applies to: coding sessions, agent workflows, long-running implementation threads, reviews, handoffs, and governed build upgrades.

## Purpose

This standard defines practical context and token hygiene for agent-assisted software work.

Context is a limited working-memory budget. Agents should prefer small, relevant, refreshable context over large, persistent, low-signal transcript history. Good context hygiene improves reliability, reduces drift, lowers token cost, and helps future agents resume work without rereading the entire repository.

Context hygiene must not be used as an excuse to skip required governance, security, architecture, testing, or task-critical reading. The goal is to keep the active working set sharp, not to work blind.

## Relationship To Other Standards

Use this standard alongside:

- `docs/current-build-pathway.md`
- `docs/policy/durable-development-engineering-policy.md`
- `docs/standards/engineering-governance-by-use-case.md`
- `docs/standards/ship-ready-engineering-standard.md`
- `docs/standards/document-control-standard.md` when durable docs or handoffs are being updated

The required engineering standards define what good and ship-ready work means. This standard defines how agents should manage context while doing that work.

## Core Principle

Keep active context minimal, relevant, current, and recoverable.

Prefer:

- scoped file reads over whole-repository scans
- phase summaries over endless transcripts
- exact next objectives over broad intentions
- durable handoff notes over chat memory
- targeted diffs over repeated rereads
- refreshable standards files over copied policy blobs

## Required Agent Behaviors

### Keep Ambient Context Lean

Root instructions should stay compact. Place detailed guidance near the relevant directory, workflow, standard, or task scope.

Disable or avoid unused tools, connectors, MCP servers, and background integrations when they are not helping the current task. Tool metadata and unused integration context can crowd out useful working memory.

### Work In Phases

Divide substantial work into clear phases such as discovery, planning, implementation, testing, cleanup, and handoff.

At phase boundaries, write or update a short durable summary instead of relying on transcript history. For governed builds, `docs/current-build-pathway.md` is the preferred live handoff location.

### Compact Or Reset Before Drift

Do not wait until the context window is nearly exhausted. Summarize or reset when signal quality starts dropping.

Use compaction or a fresh handoff when:

- a major phase completes
- the active objective changes
- the thread starts repeating mistakes
- the agent ignores earlier constraints
- broad exploration is complete and implementation is about to begin
- validation is complete and only handoff remains
- the next step can be stated more clearly than the transcript can preserve it

After compaction, restate critical constraints: architecture decisions, safety limits, acceptance criteria, project risk, validation expectations, and exact next objective.

### Control Repository Scope

Start with the smallest useful file set.

Broad repository exploration is a deliberate cost decision. Use it when ownership, architecture, or impact is unclear, then narrow quickly to the files and symbols needed for the current chunk.

Prefer diffs, targeted excerpts, and focused tests over repeated full-file or full-tree reads.

### Budget Iteration Loops

Every read, reason, edit, and verify loop has a cost.

For routine changes, keep loops short and use fast feedback. For difficult, ambiguous, risky, or security-sensitive work, spend more reasoning budget deliberately and record why.

If a loop stops producing new information, summarize the state, narrow the task, or reset context with a sharper objective.

### Stop Low-Yield Loops

Stopping is part of disciplined agent behavior. A governed agent should stop,
summarize, and hand back control when continued work would mostly consume
context without improving the project state.

Stop or escalate when:

- two or three similar attempts fail without meaningful new insight
- tests keep failing for the same unclear reason
- acceptance criteria conflict or are missing
- architectural uncertainty could create rework
- security, privacy, data integrity, money, deployment, or autonomy risk appears
- the next decision is product judgment rather than coding judgment
- the current chunk's documented stop condition has been reached

When stopping for a blocker, report what failed, what was attempted, likely root
causes, available options, and the recommended next bounded decision.

### Do Not Expand Scope By Momentum

Agents should work from the current build chunk, work packet, or explicit user
request, not from general product ambition.

- Work on one approved task or tightly related sub-task set at a time.
- Record newly discovered useful work as follow-up, not automatic current-scope
  work.
- Do not continue into adjacent backlog items merely because the current task
  went well.
- Do not keep polishing, refactoring, or optimizing after the current definition
  of done is met unless explicitly re-scoped.
- Progress requires changed project state, verification evidence, or a clarified
  blocker; activity alone is not progress.

## Handoff Summary Template

Use this template at phase boundaries, before compaction, or when handing work to another agent:

```md
## Handoff - YYYY-MM-DDTHH:MM:SS-06:00

Objective:

Current state:

Files touched:

Decisions made:

Active constraints:

Validation run:

Known risks or unverified items:

Completion status:

Exact next step:
```

Keep handoffs short enough to be read at the start of the next session.

## Reusable Agent Prompt Block

The following block can be adapted into `AGENTS.md`, `AI_BOOTSTRAP.md`, `CLAUDE.md`, or other agent instruction files:

> Operate with strict context hygiene. Keep active context minimal, relevant, current, and recoverable. Work in clear phases. Summarize at phase boundaries. Compact or reset before quality degrades. Re-state critical constraints after compaction. Narrow file scope before reading. Prefer targeted diffs and specific files over whole-repo exploration. Treat tokens as a budget, but do not skip required governance, security, architecture, or task-critical reading. Stop low-yield loops early and reset with a sharper objective.

> Work from the current approved task, not from general ambition. Do not expand
> scope by momentum. Stop when the task-level definition of done is met, when the
> documented stop condition is reached, or when repeated attempts stop producing
> new evidence. Report `Draft complete`, `Task complete`, `Integration complete`,
> `Release ready`, or `Blocked` only when evidence supports that state. Project
> completion is a human decision.

## User-Facing Guidance

When working with an agent:

- Keep instructions short and specific to the current task.
- Point the agent at the smallest useful files or directories when you know them.
- Break large work into phases.
- Ask for a summary before switching phases or starting a fresh thread.
- Compact or reset before the agent begins drifting.
- Use deep reasoning for hard, ambiguous, risky, or architectural questions.
- Stop low-yield loops and restart with a sharper prompt.

## Review Checklist

Before declaring substantial agent work complete, check:

- required governance files were read for the task
- working scope was narrowed after discovery
- broad scans were justified or avoided
- active plan and next step are durable
- validation evidence is recorded
- open risks and unverified items are stated
- the completion status is honest and evidence-backed
- low-yield loops stopped with a clear blocker or next decision
- handoff notes are short enough for another agent to use
