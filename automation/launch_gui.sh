#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT}/data/new-build-agent/logs"
mkdir -p "${LOG_DIR}"

export GOVERNANCE_HOME="${ROOT}"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

pick_python() {
  local candidates=()

  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidates+=("${PYTHON_BIN}")
  fi

  if [[ -x "${HOME}/.pyenv/shims/python3" ]]; then
    candidates+=("${HOME}/.pyenv/shims/python3")
  fi

  if [[ -d "${HOME}/.pyenv/versions" ]]; then
    while IFS= read -r candidate; do
      candidates+=("${candidate}")
    done < <(find -L "${HOME}/.pyenv/versions" -maxdepth 3 -path '*/bin/python3' | sort -r)
  fi

  if command -v python3 >/dev/null 2>&1; then
    candidates+=("$(command -v python3)")
  fi

  local seen=()
  local candidate
  for candidate in "${candidates[@]}"; do
    [[ -x "${candidate}" ]] || continue
    if [[ " ${seen[*]} " == *" ${candidate} "* ]]; then
      continue
    fi
    seen+=("${candidate}")
    if "${candidate}" - <<'PY' >/dev/null 2>&1
import tkinter
PY
    then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  return 1
}

if ! PYTHON_BIN="$(pick_python)"; then
  echo "Unable to find a Python with tkinter support. Install python3-tk or a tkinter-enabled pyenv Python." >&2
  exit 1
fi

exec "${PYTHON_BIN}" "${ROOT}/automation/new_build_gui.py" >>"${LOG_DIR}/gui-launch.log" 2>&1
