#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT}/data/new-build-agent/logs"
mkdir -p "${LOG_DIR}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "python3 is required to launch New Build Agent." >&2
  exit 1
fi

export GOVERNANCE_HOME="${ROOT}"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

exec "${PYTHON_BIN}" "${ROOT}/automation/new_build_gui.py" >>"${LOG_DIR}/gui-launch.log" 2>&1
