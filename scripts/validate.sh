#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "${repo_root}/automation/governance_check.sh" "${repo_root}"
bash "${repo_root}/automation/check_required_files.sh" "${repo_root}"

mapfile -t python_files < <(find "${repo_root}/automation" -maxdepth 1 -name '*.py' -print | sort)
if (( ${#python_files[@]} > 0 )); then
  python3 -m py_compile "${python_files[@]}"
fi

mapfile -t shell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" "${repo_root}/templates/project/scripts" -name '*.sh' -print | sort)
for file in "${shell_files[@]}"; do
  bash -n "${file}"
done

python3 -m unittest discover -s "${repo_root}/tests" -p 'test_*.py'
