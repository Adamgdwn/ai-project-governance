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

## Recommended additions (future)

- Schema validation for `project-control.yaml`
- Naming convention checks
- Exception expiry alerts
- Release readiness validation
- Agent governance compliance scoring
