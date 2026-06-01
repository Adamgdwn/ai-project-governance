# Deployment Guide

Last reviewed: 2026-05-31T11:06:01-06:00

## Environments

This is primarily a local governance tool.

| Environment | Description |
|---|---|
| dev | Local working checkout of this repository. |
| staging | A branch or copied workspace used to validate scaffold, compliance, and promotion behavior before merging. |
| prod | The trusted local checkout and any published GitHub branch/PR used as the source for future builds. |

## Release Workflow

1. Read `START_HERE.md` and `docs/current-build-pathway.md`.
2. Run `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent`.
3. Run `bash scripts/validate.sh`.
4. Review `git status --short` and confirm the intended file set.
5. Generate a promotion plan if publishing externally: `python3 automation/promotion_plan.py --project .`.
6. Run pre-promotion checks from the plan.
7. Publish through a reviewed GitHub execution step or a manual commit/PR.
8. Record validation and handoff notes in `docs/current-build-pathway.md`.

## Rollback

- For local documentation/script changes, use git revert or a follow-up correction commit.
- For generated project scaffolds, remove newly created files or directories only after confirming they are not user-authored.
- For change-control applies, remove created files or marked managed blocks if rollback is required.
- For GitHub publish execution, use the rollback commands emitted in the execution report.
- For env/Stripe actions, restore previous env values or Stripe configuration from recorded plan/report context.

## Validation

Minimum validation before release:

- governance check
- Python compile checks and tests
- shell syntax checks
- fresh scaffold smoke test for changed templates or bootstrap behavior
- change-control idempotency check for changed compliance manifests
- secret scan by pattern or approved scanner

High-risk changes require explicit review of affected tool permissions, rollback path, and user-facing documentation.
