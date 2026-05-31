# Claude project instructions

Read `./START_HERE.md` first, then `./AI_BOOTSTRAP.md`, and follow them as the canonical project rule files. Use `./docs/standards/engineering-governance-by-use-case.md` for control guidance only; do not override the selected `risk_tier` or `governance_level`. Review `./docs/policy/durable-development-engineering-policy.md` before meaningful implementation work. Build the smallest useful thing in the safest durable way, and do not treat "works locally" as complete.

Additional rules:
- Do not move or rename core files unless explicitly asked.
- Prefer small diffs over large rewrites.
- When changing behavior, update docs in the same task.
