#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "${repo_root}/automation/governance_check.sh" "${repo_root}"
bash "${repo_root}/automation/check_required_files.sh" "${repo_root}"
python3 "${repo_root}/automation/schema_validation.py" --project "${repo_root}"

mapfile -t python_files < <(find "${repo_root}/automation" -maxdepth 1 -name '*.py' -print | sort)
if (( ${#python_files[@]} > 0 )); then
  python3 -m py_compile "${python_files[@]}"
fi

mapfile -t shell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" "${repo_root}/templates/project/scripts" -name '*.sh' -print | sort)
for file in "${shell_files[@]}"; do
  bash -n "${file}"
done

mapfile -t powershell_files < <(find "${repo_root}/automation" "${repo_root}/scripts" -maxdepth 1 -name '*.ps1' -print | sort)
if (( ${#powershell_files[@]} > 0 )); then
  if command -v pwsh >/dev/null 2>&1; then
    for file in "${powershell_files[@]}"; do
      PS_SYNTAX_FILE="${file}" pwsh -NoProfile -Command '
        $File = $env:PS_SYNTAX_FILE
        $tokens = $null
        $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($File, [ref]$tokens, [ref]$errors) | Out-Null
        if ($errors.Count -gt 0) {
          throw "PowerShell syntax failed for ${File}: $($errors[0].Message)"
        }
      ' "${file}"
    done
  else
    echo "SKIP: PowerShell syntax check requires pwsh."
  fi
fi

python3 -m unittest discover -s "${repo_root}/tests" -p 'test_*.py'
