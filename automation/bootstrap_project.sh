#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 /path/to/project <project-type> [governance-level]"
  exit 1
fi

target_dir="$1"
project_type="$2"
governance_input="${3:-2}"

case "${project_type}" in
  application|website|service|internal-tool|automation|infrastructure|documentation|agent)
    ;;
  *)
    echo "Unsupported project type: ${project_type}"
    exit 1
    ;;
esac

case "${governance_input}" in
  0)
    governance_level="0"
    risk_tier="low"
    ;;
  1)
    governance_level="1"
    risk_tier="low"
    ;;
  2)
    governance_level="2"
    risk_tier="medium"
    ;;
  3)
    governance_level="3"
    risk_tier="high"
    ;;
  4)
    governance_level="4"
    risk_tier="critical"
    ;;
  low)
    governance_level="1"
    risk_tier="low"
    ;;
  medium)
    governance_level="2"
    risk_tier="medium"
    ;;
  high)
    governance_level="3"
    risk_tier="high"
    ;;
  critical)
    governance_level="4"
    risk_tier="critical"
    ;;
  *)
    echo "Unsupported governance level: ${governance_input}"
    echo "Use 0, 1, 2, 3, or 4. Legacy risk tiers low/medium/high/critical are also accepted."
    exit 1
    ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template_root="${repo_root}/templates/project"

mkdir -p "${target_dir}"
mkdir -p "${target_dir}/docs/policy"
mkdir -p "${target_dir}/docs/standards"
mkdir -p "${target_dir}/docs/risks"
mkdir -p "${target_dir}/scripts"

copy_if_missing() {
  local src="$1"
  local dest="$2"

  if [[ -e "${dest}" ]]; then
    echo "Keeping existing file: ${dest}"
  else
    cp "${src}" "${dest}"
    echo "Created: ${dest}"
  fi
}

copy_if_missing "${template_root}/README.template.md" "${target_dir}/README.md"
copy_if_missing "${template_root}/START_HERE.template.md" "${target_dir}/START_HERE.md"
copy_if_missing "${template_root}/project-control.template.yaml" "${target_dir}/project-control.yaml"
copy_if_missing "${template_root}/AGENTS.template.md" "${target_dir}/AGENTS.md"
copy_if_missing "${template_root}/CLAUDE.template.md" "${target_dir}/CLAUDE.md"
copy_if_missing "${template_root}/AI_BOOTSTRAP.template.md" "${target_dir}/AI_BOOTSTRAP.md"
copy_if_missing "${template_root}/docs/architecture.template.md" "${target_dir}/docs/architecture.md"
copy_if_missing "${template_root}/docs/manual.template.md" "${target_dir}/docs/manual.md"
copy_if_missing "${template_root}/docs/roadmap.template.md" "${target_dir}/docs/roadmap.md"
copy_if_missing "${template_root}/docs/current-build-pathway.template.md" "${target_dir}/docs/current-build-pathway.md"
copy_if_missing "${template_root}/docs/policy/durable-development-engineering-policy.template.md" "${target_dir}/docs/policy/durable-development-engineering-policy.md"
copy_if_missing "${template_root}/docs/standards/engineering-governance-by-use-case.template.md" "${target_dir}/docs/standards/engineering-governance-by-use-case.md"
copy_if_missing "${template_root}/docs/risk-register.template.md" "${target_dir}/docs/risks/risk-register.md"
copy_if_missing "${template_root}/docs/CHANGELOG.template.md" "${target_dir}/docs/CHANGELOG.md"
copy_if_missing "${template_root}/docs/adr.template.md" "${target_dir}/docs/adr-template.md"
copy_if_missing "${template_root}/docs/exception-record.template.md" "${target_dir}/docs/exception-record-template.md"
copy_if_missing "${template_root}/scripts/governance-check.template.sh" "${target_dir}/scripts/governance-check.sh"
copy_if_missing "${template_root}/scripts/governance-preflight.template.sh" "${target_dir}/scripts/governance-preflight.sh"

if [[ "${project_type}" != "documentation" ]]; then
  copy_if_missing "${template_root}/docs/deployment-guide.template.md" "${target_dir}/docs/deployment-guide.md"
  copy_if_missing "${template_root}/docs/runbook.template.md" "${target_dir}/docs/runbook.md"
fi

if [[ "${project_type}" == "agent" ]]; then
  copy_if_missing "${template_root}/docs/agent-inventory.template.md" "${target_dir}/docs/agent-inventory.md"
  copy_if_missing "${template_root}/docs/model-registry.template.md" "${target_dir}/docs/model-registry.md"
  copy_if_missing "${template_root}/docs/prompt-register.template.md" "${target_dir}/docs/prompt-register.md"
  copy_if_missing "${template_root}/docs/tool-permission-matrix.template.md" "${target_dir}/docs/tool-permission-matrix.md"
fi

python3 - <<'PY' "${target_dir}/project-control.yaml" "${project_type}" "${risk_tier}" "${governance_level}" "${target_dir}"
from datetime import datetime
import pathlib
import sys

project_control = pathlib.Path(sys.argv[1])
project_type = sys.argv[2]
risk_tier = sys.argv[3]
governance_level = sys.argv[4]
target_dir = pathlib.Path(sys.argv[5])
project_name = target_dir.name
generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
use_case_by_type = {
    "application": "Web application / SaaS",
    "website": "Static / marketing website",
    "service": "Backend API / integration service",
    "internal-tool": "Internal utility / script",
    "automation": "Workflow automation",
    "infrastructure": "Infrastructure / deployment code",
    "documentation": "Static / marketing website",
    "agent": "AI agent with tools",
}
autonomy_by_governance = {
    "0": "A2",
    "1": "A2",
    "2": "A1",
    "3": "A1",
    "4": "A0",
}

text = project_control.read_text()
text = text.replace("example-project", project_name)
text = text.replace("project_type: application", f"project_type: {project_type}")
text = text.replace("primary: Web application / SaaS", f"primary: {use_case_by_type[project_type]}")
text = text.replace("risk_tier: medium", f"risk_tier: {risk_tier}")
text = text.replace("governance_level: 2", f"governance_level: {governance_level}")
if project_type == "agent":
    text = text.replace("applicable: false", "applicable: true")
    text = text.replace("autonomy_level: A0", f"autonomy_level: {autonomy_by_governance[governance_level]}")
project_control.write_text(text)

for relative_path in ["START_HERE.md", "docs/current-build-pathway.md"]:
    path = target_dir / relative_path
    if path.exists():
        body = path.read_text()
        body = body.replace("YYYY-MM-DD", generated_at)
        path.write_text(body)
PY

chmod +x "${target_dir}/scripts/governance-check.sh"
chmod +x "${target_dir}/scripts/governance-preflight.sh"

echo
echo "Bootstrap complete for ${target_dir}"
echo "Next steps:"
echo "  1. Review project-control.yaml"
echo "  2. Run: bash \"${target_dir}/scripts/governance-preflight.sh\""
echo "  3. Optionally set GOVERNANCE_HOME=${repo_root} to use the central governance repository from inside the project."
