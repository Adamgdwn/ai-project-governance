#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/project"
  exit 1
fi

project_path="$1"

if [[ ! -d "${project_path}" ]]; then
  echo "Project path does not exist: ${project_path}"
  exit 1
fi

required_files=(
  "README.md"
  "project-control.yaml"
  "docs/architecture.md"
  "docs/risks/risk-register.md"
)

missing=0

for rel_path in "${required_files[@]}"; do
  if [[ -f "${project_path}/${rel_path}" ]]; then
    echo "PASS: Found ${rel_path}"
  else
    echo "Missing required file: ${rel_path}"
    missing=1
  fi
done

if [[ ${missing} -ne 0 ]]; then
  echo
  echo "Baseline required-file check failed."
  exit 1
fi

echo
echo "Baseline required files are present."
