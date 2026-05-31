# Agent Instructions

This repository is the source of truth for development and deployment governance.

## Default Working Rule

Before making substantial code or configuration changes in any governed project:

1. read `START_HERE.md`
2. review `docs/current-build-pathway.md`
3. review `docs/standards/engineering-governance-by-use-case.md`
4. review `docs/policy/durable-development-engineering-policy.md`
5. run the governance check
6. review the project's `project-control.yaml`
7. check for open exceptions that affect the requested work
8. capture a timestamp with `date -Iseconds`
9. only then begin implementation

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
- Confirm the requested work matches the project's `use_case.primary` classification.
- Apply the durable development standard: build the smallest useful thing in the safest durable way.
- Do not silently ignore missing governance files.
- Record deviations as explicit exceptions.
- Escalate if a request increases risk, autonomy, money handling, or sensitive data exposure.
- Treat machine checks as a baseline, not a substitute for judgment.
- Work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
- Timestamp material work, decisions, validation, and handoffs.
- Keep `docs/current-build-pathway.md` current when the active plan or next chunk changes.

## Supported Project Types

- application
- website
- service
- internal-tool
- automation
- infrastructure
- documentation
- agent
