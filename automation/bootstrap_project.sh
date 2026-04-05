#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 /path/to/project <project-type> [risk-tier]"
  exit 1
fi

target_dir="$1"
project_type="$2"
risk_tier="${3:-medium}"

case "${project_type}" in
  application|website|service|internal-tool|automation|infrastructure|documentation|agent)
    ;;
  *)
    echo "Unsupported project type: ${project_type}"
    exit 1
    ;;
esac

case "${risk_tier}" in
  low|medium|high|critical)
    ;;
  *)
    echo "Unsupported risk tier: ${risk_tier}"
    exit 1
    ;;
esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template_root="${repo_root}/templates/project"

mkdir -p "${target_dir}"
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
copy_if_missing "${template_root}/project-control.template.yaml" "${target_dir}/project-control.yaml"
copy_if_missing "${template_root}/AGENTS.template.md" "${target_dir}/AGENTS.md"
copy_if_missing "${template_root}/CLAUDE.template.md" "${target_dir}/CLAUDE.md"
copy_if_missing "${template_root}/AI_BOOTSTRAP.template.md" "${target_dir}/AI_BOOTSTRAP.md"
copy_if_missing "${template_root}/docs/architecture.template.md" "${target_dir}/docs/architecture.md"
copy_if_missing "${template_root}/docs/risk-register.template.md" "${target_dir}/docs/risks/risk-register.md"
copy_if_missing "${template_root}/docs/CHANGELOG.template.md" "${target_dir}/docs/CHANGELOG.md"
copy_if_missing "${template_root}/docs/adr.template.md" "${target_dir}/docs/adr-template.md"
copy_if_missing "${template_root}/docs/exception-record.template.md" "${target_dir}/docs/exception-record-template.md"
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

python3 - <<'PY' "${target_dir}/project-control.yaml" "${project_type}" "${risk_tier}" "${target_dir}"
import pathlib
import sys

project_control = pathlib.Path(sys.argv[1])
project_type = sys.argv[2]
risk_tier = sys.argv[3]
target_dir = pathlib.Path(sys.argv[4])
project_name = target_dir.name

text = project_control.read_text()
text = text.replace("example-project", project_name)
text = text.replace("project_type: application", f"project_type: {project_type}")
text = text.replace("risk_tier: medium", f"risk_tier: {risk_tier}")
if project_type == "agent":
    text = text.replace("applicable: false", "applicable: true")
    text = text.replace("autonomy_level: A0", "autonomy_level: A1")
project_control.write_text(text)
PY

chmod +x "${target_dir}/scripts/governance-preflight.sh"

echo
echo "Bootstrap complete for ${target_dir}"
echo "Next steps:"
echo "  1. Set GOVERNANCE_HOME=${repo_root}"
echo "  2. Review project-control.yaml"
echo "  3. Run: bash \"${target_dir}/scripts/governance-preflight.sh\""

