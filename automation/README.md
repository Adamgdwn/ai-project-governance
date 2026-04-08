# Automation

Scripts for scaffolding, governance checking, and project intake.

---

## new_build.sh — New Build Agent

Interactive launcher. Asks intake questions, classifies the project,
scaffolds the correct structure, and writes a scope file.

**Run it:**
```bash
bash ~/code/Rules\ of\ Development\ and\ Deployment/automation/new_build.sh
```

**What it asks:**
- Project name
- Build type: app / agent / tool / other
- Expected stack
- Primary builder model: claude / codex / local / hybrid
- Governance level: normal / heavy
- Whether to capture a scope brief now

**What it creates:**
```
~/code/agents/<slug>/          (for agents)
~/code/Applications/<slug>/    (for apps and tools)
  ├── README.md
  ├── CLAUDE.md
  ├── AGENTS.md
  ├── AI_BOOTSTRAP.md
  ├── INITIAL_SCOPE.md         ← intake answers + first-session checklist
  ├── project-control.yaml
  ├── docs/
  │   ├── adr/
  │   ├── specs/
  │   ├── runbooks/
  │   ├── architecture.md
  │   ├── manual.md
  │   ├── roadmap.md
  │   ├── risks/risk-register.md
  │   └── ...
  ├── scripts/governance-preflight.sh
  └── archive/
```

**Notes:**
- Uses `bootstrap_project.sh` as its scaffolding engine.
- Will not overwrite existing files if the directory already exists.
- Fill in the `## Commands` section of `AI_BOOTSTRAP.md` before the first coding session.

---

## bootstrap_project.sh — Project Scaffolder

Creates a governed project structure from templates.

```bash
bash bootstrap_project.sh /path/to/project <type> [risk-tier]
```

Types: `application` `website` `service` `internal-tool` `automation`
       `infrastructure` `documentation` `agent`

Risk tiers: `low` `medium` `high` `critical` (default: medium)

Called automatically by `new_build.sh`. Can also be run directly to bootstrap
an existing ungoverned project (safe — will not overwrite existing files).

---

## governance_check.sh — Governance Validator

Checks a project for required governance files and valid `project-control.yaml` fields.

```bash
bash governance_check.sh /path/to/project
```

Run this after bootstrapping, or from the project's own preflight script:
```bash
bash scripts/governance-preflight.sh
```

---

## check_required_files.sh — Minimal File Check

Lightweight check for required file presence only. Subset of `governance_check.sh`.

```bash
bash check_required_files.sh /path/to/project
```

---

## project_registry.py — Local Project Inventory

Stores a local record of successful project scaffolds and audit results.

**Examples:**
```bash
python3 automation/project_registry.py list
python3 automation/project_registry.py register --project-name demo --slug demo --path ~/code/agents/demo --project-type agent --risk-tier medium --builder codex --stack python
```

---

## audit_projects.py — Workspace Governance Audit

Scans `~/code/agents` and `~/code/Applications` for governed projects, runs `governance_check.sh`, and records the audit result in the local registry.

**Run it:**
```bash
python3 automation/audit_projects.py
python3 automation/audit_projects.py --json
```

---

## change_control.py — Structured Upgrade Manifests

Generates and applies reviewable upgrade manifests for governed project drift.

**Examples:**
```bash
python3 automation/change_control.py propose --project ~/code/agents/my-project
python3 automation/change_control.py apply --manifest data/new-build-agent/exports/upgrade-my-project-20260408T000000Z.json
```

---

## promotion_plan.py — External Sync Planning

Generates a staged promotion plan for GitHub, Vercel, Supabase, Stripe, Resend, and similar targets without executing any external action. Plans now include local pre-checks, post-checks, and rollback readiness notes.

**Example:**
```bash
python3 automation/promotion_plan.py --project ~/code/Applications/frogger
```

---

## promotion_checks.py — Guided Pre/Post Checks

Runs the local pre-promotion or post-promotion checks defined in a generated promotion plan and writes a JSON report.

**Examples:**
```bash
python3 automation/promotion_checks.py --plan data/new-build-agent/exports/promotion-frogger-20260408T000000Z.json
python3 automation/promotion_checks.py --plan data/new-build-agent/exports/promotion-frogger-20260408T000000Z.json --stage post_promotion_checks
```

---

## Recommended additions (future)

- Schema validation for `project-control.yaml`
- Naming convention checks
- Exception expiry alerts
- Release readiness validation
- Agent governance compliance scoring

---

## Consolidation plan

The current plan is to keep `New Build Agent` as the primary product and absorb the useful backend/controller concepts from the separate `New Project Setup Agent` prototype.

See:

- `docs/processes/new-build-agent-consolidation-plan.md`
