#!/usr/bin/env python3
"""Generate staged promotion plans for local-to-external rollout."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from change_control import build_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-agent" / "exports"
SIGNAL_FILES = [
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    ".env.example",
    ".env.local.example",
    ".env.template",
    "README.md",
    "docs/manual.md",
    "docs/roadmap.md",
]


def file_contains_any(project: Path, needles: list[str]) -> bool:
    for relative in SIGNAL_FILES:
        candidate = project / relative
        if not candidate.exists() or not candidate.is_file():
            continue
        try:
            content = candidate.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(needle in content for needle in needles):
            return True
    return False


def read_package_scripts(project: Path) -> dict[str, str]:
    package_file = project / "package.json"
    if not package_file.exists():
        return {}
    try:
        package_data = json.loads(package_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = package_data.get("scripts", {})
    if isinstance(scripts, dict):
        return {str(key): str(value) for key, value in scripts.items()}
    return {}


def build_local_checks(project: Path) -> dict[str, list[dict[str, str]]]:
    pre_checks: list[dict[str, str]] = []
    post_checks: list[dict[str, str]] = []

    preflight = project / "scripts" / "governance-preflight.sh"
    if preflight.exists():
        pre_checks.append(
            {
                "name": "governance_preflight",
                "command": "bash scripts/governance-preflight.sh",
                "kind": "automated",
                "reason": "Confirm required governance files and local repo policy before any promotion work.",
            }
        )

    has_python = (project / "pyproject.toml").exists() or (project / "requirements.txt").exists()
    has_python_tests = (project / "tests").exists() or (project / "pytest.ini").exists()
    if has_python and has_python_tests:
        pre_checks.append(
            {
                "name": "python_tests",
                "command": "python3 -m pytest -q",
                "kind": "automated_if_available",
                "reason": "Run the local Python test suite before promotion.",
            }
        )
        post_checks.append(
            {
                "name": "python_smoke_retest",
                "command": "python3 -m pytest -q",
                "kind": "automated_if_available",
                "reason": "Confirm the Python test suite still passes after promotion work.",
            }
        )

    package_scripts = read_package_scripts(project)
    if package_scripts:
        if "lint" in package_scripts:
            pre_checks.append(
                {
                    "name": "js_lint",
                    "command": "npm run lint",
                    "kind": "automated_if_available",
                    "reason": "Catch frontend or node-level issues before promotion.",
                }
            )
        if "test" in package_scripts:
            pre_checks.append(
                {
                    "name": "js_tests",
                    "command": "npm test",
                    "kind": "automated_if_available",
                    "reason": "Run the package test script before promotion.",
                }
            )
            post_checks.append(
                {
                    "name": "js_smoke_retest",
                    "command": "npm test",
                    "kind": "automated_if_available",
                    "reason": "Re-run the package test script after promotion work.",
                }
            )
        if "build" in package_scripts:
            pre_checks.append(
                {
                    "name": "js_build",
                    "command": "npm run build",
                    "kind": "automated_if_available",
                    "reason": "Verify the production build path before promotion.",
                }
            )
            post_checks.append(
                {
                    "name": "js_build_recheck",
                    "command": "npm run build",
                    "kind": "automated_if_available",
                    "reason": "Confirm the production build still succeeds after promotion.",
                }
            )

    if not pre_checks:
        pre_checks.append(
            {
                "name": "manual_smoke_review",
                "command": "manual review",
                "kind": "manual",
                "reason": "No safe automated local checks were detected, so a manual repo review is required before promotion.",
            }
        )
    if not post_checks:
        post_checks.append(
            {
                "name": "manual_post_promotion_review",
                "command": "manual review",
                "kind": "manual",
                "reason": "No safe automated post-promotion checks were detected, so a manual verification pass is required.",
            }
        )

    return {"pre": pre_checks, "post": post_checks}


def detect_targets(project: Path) -> dict[str, dict]:
    has_git = (project / ".git").exists()
    has_package = (project / "package.json").exists()
    has_pyproject = (project / "pyproject.toml").exists()
    has_requirements = (project / "requirements.txt").exists()
    has_readme = (project / "README.md").exists()
    has_governance = (project / "project-control.yaml").exists()
    has_vercel = (project / "vercel.json").exists() or (project / ".vercel").exists()
    has_supabase = (project / "supabase").exists()
    has_next = (project / "next.config.js").exists() or (project / "next.config.mjs").exists() or (project / ".next").exists()
    uses_stripe = file_contains_any(project, ["stripe", "stripe_secret", "stripe_publishable"])
    uses_resend = file_contains_any(project, ["resend", "resend_api_key"])

    return {
        "github": {
            "relevant": has_git or has_package or has_pyproject or has_requirements or has_readme or has_governance,
            "approval_required": True,
            "auto_execute": False,
            "planned_actions": [
                "review local changes",
                "create or verify remote repository linkage",
                "prepare branch, commit, and push plan",
            ],
            "post_promotion_checks": [
                "confirm the expected branch and commit are visible remotely",
                "confirm CI or status checks begin from the intended ref",
            ],
            "rollback_plan": [
                "document the previous stable commit before push",
                "use a revert commit or restore the previous deployment ref if promotion goes wrong",
            ],
        },
        "vercel": {
            "relevant": has_vercel or has_next or has_package,
            "approval_required": True,
            "auto_execute": False,
            "planned_actions": [
                "verify framework/build commands",
                "prepare environment variable checklist",
                "prepare deploy or relink instructions",
            ],
            "post_promotion_checks": [
                "verify the deployed URL responds successfully",
                "confirm critical app routes and environment bindings behave as expected",
            ],
            "rollback_plan": [
                "record the last known good deployment before promotion",
                "be ready to promote the previous stable deployment if the new one fails",
            ],
        },
        "supabase": {
            "relevant": has_supabase,
            "approval_required": True,
            "auto_execute": False,
            "planned_actions": [
                "inspect supabase config and migrations",
                "prepare safe migration/apply checklist",
                "prepare secrets and environment review",
            ],
            "post_promotion_checks": [
                "verify database connectivity and auth assumptions after the change",
                "confirm migrations or policy updates match the intended environment",
            ],
            "rollback_plan": [
                "record the last safe migration state before execution",
                "prepare a compensating migration or rollback steps before applying changes",
            ],
        },
        "stripe": {
            "relevant": uses_stripe,
            "approval_required": True,
            "auto_execute": False,
            "planned_actions": [
                "inventory Stripe products, prices, and webhook expectations",
                "prepare publishable and secret key environment checklist",
                "prepare dashboard-side changes and rollback notes before any live update",
            ],
            "post_promotion_checks": [
                "verify webhook endpoints and signing secrets still match the intended environment",
                "confirm test-mode or live-mode payment flows behave as expected",
            ],
            "rollback_plan": [
                "record current product, price, and webhook settings before any dashboard change",
                "be ready to restore prior Stripe configuration and disable new live paths if validation fails",
            ],
        },
        "resend": {
            "relevant": uses_resend,
            "approval_required": True,
            "auto_execute": False,
            "planned_actions": [
                "verify sending domains, API key scope, and sender identities",
                "prepare environment variable checklist for delivery settings",
                "prepare safe email rollout and rollback notes before enabling sends",
            ],
            "post_promotion_checks": [
                "confirm sender identities and domains are still valid",
                "run a safe delivery smoke test before enabling broad email sends",
            ],
            "rollback_plan": [
                "record prior sender and domain configuration before changes",
                "be ready to disable or revert the new sending path if delivery validation fails",
            ],
        },
    }


def local_compliance_stage(project: Path) -> dict:
    manifest = build_manifest(project)
    missing = [action["relative_path"] for action in manifest.get("actions", [])]
    return {
        "name": "local_compliance",
        "status": "ready" if not missing else "needs_work",
        "missing_items": missing,
        "note": "External sync planning should happen only after the local governance baseline is in a good state.",
    }


def build_plan(project: Path) -> dict:
    project = project.expanduser().resolve()
    targets = detect_targets(project)
    local_checks = build_local_checks(project)
    return {
        "plan_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project),
        "project_slug": project.name,
        "purpose": "Prepare staged local-to-external rollout without auto-pushing changes.",
        "policy": {
            "local_changes_allowed": True,
            "external_pushes_allowed_by_default": False,
            "require_explicit_approval_per_target": True,
            "rollback_expectation": "Every external target needs its own rollback notes before execution.",
        },
        "stages": [
            local_compliance_stage(project),
            {
                "name": "pre_promotion_checks",
                "status": "planned",
                "checks": local_checks["pre"],
                "note": "Run local function and readiness checks before any approved promotion action.",
            },
            {
                "name": "prepare_external_sync",
                "status": "planned",
                "targets": targets,
                "note": "This stage prepares target-specific plans only. It does not push, deploy, migrate, bill, or send email.",
            },
            {
                "name": "approve_and_execute",
                "status": "blocked_pending_human_approval",
                "note": "GitHub, Vercel, Supabase, Stripe, and Resend actions must each be explicitly approved before execution.",
            },
            {
                "name": "post_promotion_checks",
                "status": "blocked_pending_execution",
                "checks": local_checks["post"],
                "note": "After an approved promotion action, re-run local checks and the target-specific verification steps from the plan.",
            },
            {
                "name": "rollback_readiness",
                "status": "required_before_execution",
                "note": "Review target rollback notes before approving any external action. Promotion is not considered ready without a rollback path.",
            },
        ],
    }


def write_plan(plan: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = EXPORT_ROOT / f"promotion-{plan['project_slug']}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a staged promotion plan for a project.")
    parser.add_argument("--project", required=True, help="Path to the project")
    parser.add_argument("--output", help="Optional output path for the promotion plan JSON")
    args = parser.parse_args()

    plan = build_plan(Path(args.project))
    output = write_plan(plan, Path(args.output) if args.output else None)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
