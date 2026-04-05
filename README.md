# AI Project Governance Framework

A lightweight, opinionated governance framework for AI-assisted software projects — with a **New Build Agent** that handles project intake, classification, scaffolding, and documentation from a single command or desktop GUI.

---

## New Build Agent

The fastest way to start a governed project.

**Terminal:**
```bash
bash automation/new_build.sh
```

**Desktop GUI** (requires Python 3 + tkinter):
```bash
python3 automation/new_build_gui.py
```

It asks six questions and produces a fully structured, governed project directory:

```
~/code/Applications/my-app/
  ├── README.md
  ├── CLAUDE.md                 ← AI agent instructions
  ├── AGENTS.md                 ← Multi-agent coordination rules
  ├── AI_BOOTSTRAP.md           ← Canonical rules for any AI session
  ├── INITIAL_SCOPE.md          ← Intake answers + first-session checklist
  ├── project-control.yaml      ← Risk tier, owner, type, controls
  ├── docs/
  │   ├── architecture.md
  │   ├── adr/                  ← Architecture Decision Records
  │   ├── specs/
  │   ├── runbooks/
  │   ├── risks/risk-register.md
  │   ├── CHANGELOG.md
  │   ├── deployment-guide.md
  │   └── exception-record-template.md
  ├── scripts/
  │   └── governance-preflight.sh
  └── archive/
```

### Intake questions

| Question | Options |
|----------|---------|
| Project name | free text |
| Build type | `app` / `agent` / `tool` / `other` |
| Expected stack | free text |
| Primary builder model | `claude` / `codex` / `local` / `hybrid` |
| Governance level | `normal` (medium risk) / `heavy` (high risk) |
| Capture scope brief now? | yes / no |

### Project routing

| Type | Governance type | Default root |
|------|----------------|--------------|
| app | application | `~/code/Applications/` |
| agent | agent | `~/code/agents/` |
| tool | internal-tool | `~/code/Applications/` |
| other | automation | `~/code/Applications/` |

> **Note:** Root paths (`AGENTS_ROOT`, `APPS_ROOT`) are set at the top of `new_build.sh` and `new_build_gui.py`. Change them to match your machine layout. The default owner name `Adam Goodwin` in `new_build.sh` should also be updated for your use.

---

## What's in this repo

```
automation/          Scripts for scaffolding, governance checking, and project intake
  new_build.sh         Interactive terminal launcher (New Build Agent)
  new_build_gui.py     Desktop GUI launcher (tkinter, dark theme)
  bootstrap_project.sh Scaffolding engine — safe to run against existing projects
  governance_check.sh  Full governance validator
  check_required_files.sh Minimal required-file check
  new-build-agent.svg  Icon for desktop launcher

templates/project/   Starter files copied into every new project
  README.template.md
  CLAUDE.template.md
  AGENTS.template.md
  AI_BOOTSTRAP.template.md
  project-control.template.yaml
  scripts/governance-preflight.template.sh
  docs/               Architecture, ADR, risk register, runbook, changelog, etc.

docs/                Framework documentation
  policy/             Engineering governance policy
  standards/          Naming, structure, documentation, testing, security,
                      deployment, AI agent governance
  processes/          Project intake, exception management
  quick-start-governance-flow.md
  user-guide.md

checklists/          Project setup, release readiness, agent readiness
```

---

## Requirements

| Tool | Used for |
|------|---------|
| bash | `new_build.sh`, `bootstrap_project.sh`, `governance_check.sh` |
| Python 3 + tkinter | `new_build_gui.py` |
| sed, awk, python3 | Used internally by `bootstrap_project.sh` |

On Debian/Ubuntu/Pop!_OS, install tkinter with:
```bash
sudo apt install python3-tk
```

---

## Desktop launcher (Linux)

After cloning, create a `.desktop` file to launch the GUI from your application menu or desktop:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=New Build Agent
Comment=Scope and scaffold a new governed project
Icon=/path/to/repo/automation/new-build-agent.svg
Exec=python3 /path/to/repo/automation/new_build_gui.py
Terminal=false
StartupNotify=true
Categories=Development;Utility;
```

Place it in `~/.local/share/applications/` and mark it executable.

---

## Bootstrap script directly

`bootstrap_project.sh` can be used standalone to add governance structure to an existing project:

```bash
bash automation/bootstrap_project.sh /path/to/project application medium
```

Types: `application` `website` `service` `internal-tool` `automation` `infrastructure` `documentation` `agent`

Risk tiers: `low` `medium` `high` `critical`

Safe to run on existing projects — will not overwrite files that already exist.

---

## Governance model

- **Risk-adjusted**: four tiers (low / medium / high / critical), controls scale with risk
- **Exception-first deviations**: deviations are documented and approved, not silently skipped
- **AI-native**: `CLAUDE.md`, `AGENTS.md`, `AI_BOOTSTRAP.md` are first-class project artifacts
- **Agent-specific controls**: for `agent` type projects, additional docs are scaffolded (agent inventory, model registry, prompt register, tool permission matrix)
- **Machine-enforceable**: `governance_check.sh` and per-project `governance-preflight.sh` can gate CI

---

## License

MIT
