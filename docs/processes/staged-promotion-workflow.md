# Staged Promotion Workflow

## Purpose

This workflow separates local compliance work from any external push or deployment action.

The intent is:

- make local structure and governance compliant first
- prepare target-specific rollout plans second
- require explicit approval for GitHub, Vercel, Supabase, Stripe, Resend, or other external systems

## Stages

1. Local compliance

- repair or add required docs and governance files
- review manifests before applying local structure changes
- confirm the repo is in a stable local state

2. Prepare external sync

- inspect project signals for GitHub, Vercel, Supabase, Stripe, and Resend relevance
- generate a reviewable promotion plan with pre-checks, post-checks, and rollback notes
- list the target-specific checks, environment needs, and rollback expectations

3. Approve and execute per target

- run the pre-promotion checks before approval

- approve GitHub separately
- approve Vercel separately
- approve Supabase separately
- approve Stripe separately
- approve Resend separately
- keep rollback notes attached to each target before execution

4. Post-promotion verification and rollback readiness

- re-run local checks after an approved promotion
- confirm target-specific health or smoke checks
- review rollback notes before any external change is considered safe

## Safety Rules

- local structural changes can be more autonomous than external actions
- external actions are never one-click by default
- secrets, environment variables, and deployment links must be reviewed explicitly
- target-specific execution should be blocked until the plan is reviewed

## Current Tooling

Generate a promotion plan with:

```bash
python3 automation/promotion_plan.py --project /path/to/project
```

This creates a plan file under `data/new-build-agent/exports/`.

Run the guided checks with:

```bash
python3 automation/promotion_checks.py --plan /path/to/plan.json
python3 automation/promotion_checks.py --plan /path/to/plan.json --stage post_promotion_checks
```

Execute the approved GitHub publish step with:

```bash
python3 automation/promotion_execute.py --plan /path/to/plan.json --target github --commit-message "Promote project"
```

This writes an execution report that records the previous commit, the new commit, the pushed branch, and rollback commands.
