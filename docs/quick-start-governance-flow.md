# Quick-Start Governance Flow

## Purpose

This is the shortest practical path for bringing a new project under governance.

## One-Page Flow

```text
Project idea
   |
   v
Define boundary
   |
   v
Assign owner + technical lead
   |
   v
Set project type + risk tier
   |
   v
Create core docs and project-control.yaml
   |
   v
Apply relevant standards
   |
   v
Record any exceptions
   |
   v
Add machine enforcement
   |
   v
Run readiness checklist
   |
   v
Deploy and operate
   |
   v
Review changes, risks, and exceptions over time
```

## Daily Procedure

1. Start by classifying the project.
   Decide the project type, whether it is single-repo or monorepo-based, and its initial risk tier.

2. Create the minimum control set.
   Add `README.md`, `project-control.yaml`, architecture notes, and a risk register. Add deployment and runbook docs if the project will be deployed or operated.

3. Apply type-specific requirements.
   Add extra controls for applications, infrastructure, automations, or agents as needed.

4. Document deviations early.
   If anything important is missing or intentionally different, create an exception record instead of leaving the gap implicit.

5. Enforce what can be checked automatically.
   Add file checks, tests, linting, secret scanning, and release checks to CI as soon as practical.

6. Use checklists before change or release.
   The checklists are the operational checkpoint that turns standards into repeatable behavior.

## Minimum Starter Pack

Copy or create these first:

- `README.md`
- `project-control.yaml`
- `docs/architecture.md`
- `docs/risks/risk-register.md`

Add these when applicable:

- `docs/deployment-guide.md`
- `docs/runbook.md`
- `docs/CHANGELOG.md`
- `docs/agent-inventory.md`
- `docs/model-registry.md`
- `docs/prompt-register.md`
- `docs/tool-permission-matrix.md`

## Decision Rules

- Prefer consistency unless there is a strong reason not to.
- Raise controls when risk rises.
- Record exceptions instead of silently deviating.
- Automate enforcement before relying on memory.
- Keep documents lean, but never absent.

## Who Approves What

- Default standard adoption: project owner and technical lead execute it.
- Exceptions: project owner and technical lead approve them.
- Higher-risk production release: owner and technical lead review before release.

## When To Revisit Governance

Reassess the project when:

- money movement is added
- sensitive data scope increases
- external users are introduced
- agent autonomy increases
- operational criticality grows

## Related Documents

- [User Guide](./user-guide.md)
- [Visual Governance Flow](./assets/governance-flow.svg)
- [Engineering Governance Policy](./policy/engineering-governance-policy.md)
- [Document Control Standard](./standards/document-control-standard.md)
- [Project Intake Process](./processes/project-intake-process.md)
- [Exception Management Process](./processes/exception-management-process.md)
