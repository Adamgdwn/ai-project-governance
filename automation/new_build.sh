#!/usr/bin/env bash
# new_build.sh — New Build Agent
#
# Interactive intake, classification, and scaffolding launcher.
# Wraps bootstrap_project.sh; does not replace it.
#
# Usage:
#   bash ~/code/Rules\ of\ Development\ and\ Deployment/automation/new_build.sh

set -euo pipefail

GOVERNANCE_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOTSTRAP="${GOVERNANCE_HOME}/automation/bootstrap_project.sh"
AGENTS_ROOT="${HOME}/code/agents"
APPS_ROOT="${HOME}/code/Applications"
TODAY="$(date +%Y-%m-%d)"

# ── helpers ───────────────────────────────────────────────────────────────────

hr()  { printf '%.0s─' {1..60}; echo; }
msg() { echo "  $*"; }

ask() {
  local prompt="$1" default="${2:-}" answer
  if [[ -n "$default" ]]; then
    read -rp "  ${prompt} [${default}]: " answer || { echo; exit 1; }
    printf '%s' "${answer:-$default}"
  else
    read -rp "  ${prompt}: " answer || { echo; exit 1; }
    printf '%s' "$answer"
  fi
}

ask_choice() {
  local prompt="$1"; shift
  local choices=("$@")
  local answer valid
  while true; do
    read -rp "  ${prompt} ($(IFS=/; echo "${choices[*]}")): " answer || { echo; exit 1; }
    valid=""
    for c in "${choices[@]}"; do
      [[ "$answer" == "$c" ]] && valid=1 && break
    done
    [[ -n "$valid" ]] && break
    msg "Please enter one of: ${choices[*]}"
  done
  printf '%s' "$answer"
}

slugify() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _/' '-' \
    | tr -cd '[:alnum:]-' \
    | sed 's/--*/-/g; s/^-//; s/-$//'
}

# ── header ────────────────────────────────────────────────────────────────────

echo
hr
msg "New Build Agent"
msg "Scope → Classify → Scaffold"
hr
echo

# ── intake ────────────────────────────────────────────────────────────────────

RAW_NAME=""
while [[ -z "$RAW_NAME" ]]; do
  RAW_NAME=$(ask "Project name")
  [[ -z "$RAW_NAME" ]] && msg "Name cannot be empty."
done

BUILD_TYPE=$(ask_choice "Build type" app agent tool other)

case "$BUILD_TYPE" in
  app)
    GOV_TYPE="application"
    TARGET_ROOT="$APPS_ROOT"
    ;;
  agent)
    GOV_TYPE="agent"
    TARGET_ROOT="$AGENTS_ROOT"
    ;;
  tool)
    GOV_TYPE="internal-tool"
    TARGET_ROOT="$APPS_ROOT"
    ;;
  other)
    echo
    msg "Supported types: website / service / internal-tool / automation / infrastructure / documentation"
    GOV_TYPE=$(ask "Governance project type")
    ROOT_CHOICE=$(ask_choice "Target root" agents applications)
    [[ "$ROOT_CHOICE" == "agents" ]] && TARGET_ROOT="$AGENTS_ROOT" || TARGET_ROOT="$APPS_ROOT"
    ;;
esac

STACK=$(ask "Expected stack" "not specified")

PRIMARY_MODEL=$(ask_choice "Primary builder" claude codex local hybrid)

RISK_LEVEL=$(ask_choice "Governance level" normal heavy)
[[ "$RISK_LEVEL" == "heavy" ]] && RISK_TIER="high" || RISK_TIER="medium"

SCOPE_NOW=$(ask_choice "Capture scope brief now?" yes no)

PROBLEM="" USER_DESC="" MVP=""
if [[ "$SCOPE_NOW" == "yes" ]]; then
  echo
  msg "Scope brief — brief answers are fine:"
  PROBLEM=$(ask  "What problem does this solve")
  USER_DESC=$(ask "Who is the primary user or consumer")
  MVP=$(ask      "What does the MVP look like")
fi

# ── derive ────────────────────────────────────────────────────────────────────

SLUG=$(slugify "$RAW_NAME")
TARGET_DIR="${TARGET_ROOT}/${SLUG}"

# ── confirm ───────────────────────────────────────────────────────────────────

echo
hr
msg "Plan"
hr
msg "Name:        ${RAW_NAME}"
msg "Slug:        ${SLUG}"
msg "Type:        ${GOV_TYPE}"
msg "Risk tier:   ${RISK_TIER}"
msg "Model:       ${PRIMARY_MODEL}"
msg "Stack:       ${STACK}"
msg "Location:    ${TARGET_DIR}"
echo

if [[ -d "$TARGET_DIR" ]]; then
  msg "WARNING: ${TARGET_DIR} already exists. Existing files will not be overwritten."
  echo
fi

CONFIRM=$(ask_choice "Create this project?" yes no)
[[ "$CONFIRM" != "yes" ]] && { msg "Aborted."; exit 0; }

# ── scaffold ──────────────────────────────────────────────────────────────────

echo
msg "Scaffolding..."
echo

bash "$BOOTSTRAP" "$TARGET_DIR" "$GOV_TYPE" "$RISK_TIER"

# Extra directories not created by bootstrap_project.sh
mkdir -p \
  "${TARGET_DIR}/docs/adr" \
  "${TARGET_DIR}/docs/specs" \
  "${TARGET_DIR}/docs/runbooks" \
  "${TARGET_DIR}/archive"

echo "Created: docs/adr  docs/specs  docs/runbooks  archive"

# ── fill project-control.yaml ─────────────────────────────────────────────────

PC="${TARGET_DIR}/project-control.yaml"
if [[ -f "$PC" ]]; then
  sed -i "s/name: Project Owner/name: Adam Goodwin/" "$PC"
  sed -i "s/name: Technical Lead/name: ${PRIMARY_MODEL} session/" "$PC"
fi

# ── INITIAL_SCOPE.md ──────────────────────────────────────────────────────────

SCOPE_FILE="${TARGET_DIR}/INITIAL_SCOPE.md"

cat > "$SCOPE_FILE" <<EOF
# Initial Scope — ${RAW_NAME}

Generated: ${TODAY}

## Classification

| Field          | Value             |
|----------------|-------------------|
| Project name   | ${RAW_NAME}       |
| Slug / dir     | ${SLUG}           |
| Type           | ${GOV_TYPE}       |
| Risk tier      | ${RISK_TIER}      |
| Stack          | ${STACK}          |
| Primary model  | ${PRIMARY_MODEL}  |
| Location       | ${TARGET_DIR}     |

## Build approach

Primary builder: **${PRIMARY_MODEL}**

EOF

if [[ -n "$PROBLEM" ]]; then
  cat >> "$SCOPE_FILE" <<EOF
## Scope brief

**Problem:** ${PROBLEM}

**Primary user / consumer:** ${USER_DESC}

**MVP:** ${MVP}

EOF
else
  cat >> "$SCOPE_FILE" <<'EOF'
## Scope brief

Not captured at intake. Fill in before the first coding session.

- **Problem:**
- **Primary user / consumer:**
- **MVP:**

EOF
fi

cat >> "$SCOPE_FILE" <<'EOF'
## First session checklist

- [ ] Fill in commands in `AI_BOOTSTRAP.md`
- [ ] Confirm risk tier in `project-control.yaml`
- [ ] Add first ADR if architecture decisions were made at intake
- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`
EOF

echo "Created: INITIAL_SCOPE.md"

# ── summary ───────────────────────────────────────────────────────────────────

echo
hr
msg "Done — ${RAW_NAME}"
hr
msg "Path: ${TARGET_DIR}"
echo
msg "Files created:"
for f in README.md CLAUDE.md AGENTS.md AI_BOOTSTRAP.md INITIAL_SCOPE.md project-control.yaml; do
  [[ -f "${TARGET_DIR}/${f}" ]] && msg "  ${f}"
done
echo
msg "Next:"
msg "  1. Fill in commands in AI_BOOTSTRAP.md"
msg "  2. Review project-control.yaml"
msg "  3. Open: ${TARGET_DIR}"
echo
