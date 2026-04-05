# User Guide

## Purpose

This guide explains how to apply the framework without turning it into unnecessary process overhead.

## Who This Is For

- project owners
- technical leads
- developers
- operators
- agent builders

## How To Start A New Project

1. Choose the project boundary.
2. Assign the owner and technical lead.
3. Set the project type and initial risk tier.
4. Copy the templates needed for the project.
5. Fill in `project-control.yaml`.
6. Create the required core documents.
7. Add any project-type-specific documents.
8. Record startup exceptions if the project is intentionally incomplete.
9. Add baseline enforcement in CI or local validation.

## Minimum Starter Set

For most projects, start with:

- `README.md`
- `project-control.yaml`
- `docs/architecture.md`
- `docs/risks/risk-register.md`
- `docs/deployment-guide.md` if deployable
- `docs/runbook.md` if operable

For agent projects, also add:

- `docs/agent-inventory.md`
- `docs/model-registry.md`
- `docs/prompt-register.md`
- `docs/tool-permission-matrix.md`

## How To Stay Nimble

Use the smallest document that still creates clarity.

Examples:

- a lightweight architecture overview is acceptable for a small script
- a short runbook is acceptable for a simple internal tool
- a full release and rollback guide is expected for high-risk production systems

## When To Record An Exception

Create an exception record when:

- a required document is intentionally omitted
- a required environment does not exist
- a security or testing control is delayed
- a project structure deviates materially from the standard
- an agent is given broader autonomy than the default control set assumes

## Recommended Adoption Sequence For Existing Projects

1. Create `project-control.yaml`.
2. Add the required core documents.
3. Classify risk.
4. Record known gaps as exceptions.
5. Add machine checks for file presence and tests.
6. Strengthen release and security controls next.

## How To Use The Checklists

- Use the setup checklist during project creation.
- Use the release checklist before production changes.
- Use the agent checklist before enabling or expanding agent autonomy.

## Future Maturity Path

This framework is designed to mature in layers:

1. policy and templates
2. project adoption
3. CI enforcement
4. metrics and drift monitoring
5. governing-agent assistance

