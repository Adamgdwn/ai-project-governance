# Contributing

Thank you for helping improve New Build Governance Agent. This project is meant to make AI-assisted project startup more reliable without turning every small build into heavyweight process.

## Good Contribution Areas

- clearer setup instructions for Windows, macOS, and Linux
- safer launchers and validation scripts
- better project scaffolding defaults
- practical agent instructions that reduce context bloat
- release-readiness and governance checks that catch real problems
- documentation that helps new users understand when to use the framework

## Ground Rules

- Keep the guided intake small and understandable.
- Do not overwrite user project files during scaffolding.
- Prefer conservative, update-safe behavior over destructive automation.
- Keep governance proportional to risk.
- Avoid adding provider-specific secrets, tokens, or owner-funded credentials.
- Document new commands, generated files, or release expectations in the README or relevant docs.

## Development Checks

Run the targeted checks for the area you changed. For general changes, start with:

```bash
bash scripts/validate.sh
python3 -m pytest
git diff --check
```

On Windows, use:

```powershell
.\scripts\validate.ps1
py -3 -m pytest
git diff --check
```

If a check is unavailable on your platform, mention that in the pull request.

## Pull Requests

Please describe:

- what changed
- why it helps project startup or agent governance
- which operating systems or launch paths you tested
- any follow-up work that remains

By contributing, you agree that your contribution is provided under the MIT License.
