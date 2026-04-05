# Documentation Standard

## Purpose

This standard defines the minimum document set required for governed projects.

## Documentation Principles

- Documentation must support delivery, operation, and handover.
- Documents should be concise, current, and owned.
- Required documents may be lightweight, but they may not be absent.

## Core Required Documents

Every project must provide:

- `README.md`
- `project-control.yaml`
- architecture overview
- deployment guide for deployable systems
- runbook for operable systems
- change log or release history
- risk register

## Type-Specific Additions

### Applications, Services, and Websites

Must also include:

- environment and configuration notes
- dependency and integration notes
- user-facing availability or support assumptions

### Internal Tools and Automations

Must also include:

- execution and scheduling model
- operational owner
- failure handling notes

### Infrastructure Repositories

Must also include:

- environment topology
- state handling notes
- change approval expectations

### AI Agents

Must also include:

- model registry
- prompt or instruction record
- tool permission matrix
- evaluation strategy
- human oversight rules
- rollback or kill-switch guidance

## Change Documentation

Major architectural or governance decisions should be captured in ADR form.

At minimum, capture decisions that affect:

- security posture
- production architecture
- deployment model
- data handling
- agent autonomy
- external dependencies with high lock-in risk

## Quality Rules

Required documents must:

- state owner and last review date where practical
- be written for maintainers and operators, not just authors
- avoid stale promises or future plans that are no longer accurate

