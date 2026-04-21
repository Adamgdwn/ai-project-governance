#!/usr/bin/env python3
"""
New Build Agent — headless wrapper.

Reads one JSON object from stdin, scaffolds a governed project, emits one JSON
object to stdout as the last line. Progress lines go to stderr.

Called by the Freedom dispatcher via params_transport: stdin_json.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
BOOTSTRAP = GOVERNANCE_HOME / "automation" / "bootstrap_project.sh"
REGISTRY = GOVERNANCE_HOME / "automation" / "project_registry.py"
AGENTS_ROOT = Path.home() / "code" / "agents"
APPS_ROOT = Path.home() / "code" / "Applications"

GOV_TYPES = {
    "application", "website", "service", "internal-tool",
    "automation", "infrastructure", "documentation", "agent",
}
RISK_TIERS = {"low", "medium", "high", "critical"}
BUILD_TYPE_GOV_MAP = {"app": "application", "agent": "agent", "tool": "internal-tool", "other": "internal-tool"}


def progress(msg: str) -> None:
    print(f"[new-build-agent] {msg}", file=sys.stderr, flush=True)


def fail(msg: str, **extra) -> None:
    print(json.dumps({"ok": False, "error": msg, **extra}), flush=True)
    sys.exit(1)


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[ _/]", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def resolve_target_root(build_type: str, governance_type: str) -> Path:
    if build_type == "agent" or governance_type == "agent":
        return AGENTS_ROOT
    return APPS_ROOT


def main() -> None:
    raw = sys.stdin.read()
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON input: {e}")
        return

    project_name = params.get("project_name", "").strip()
    build_type = params.get("build_type", "").strip()

    if not project_name:
        fail("project_name is required")
        return
    if build_type not in {"app", "agent", "tool", "other"}:
        fail(f"build_type must be one of app/agent/tool/other, got: {build_type!r}")
        return

    governance_type = params.get("governance_type", "").strip() or BUILD_TYPE_GOV_MAP.get(build_type, "internal-tool")
    if governance_type not in GOV_TYPES:
        fail(f"governance_type {governance_type!r} not valid; must be one of: {sorted(GOV_TYPES)}")
        return

    risk_tier = params.get("risk_tier", "medium").strip()
    if risk_tier not in RISK_TIERS:
        fail(f"risk_tier must be one of {sorted(RISK_TIERS)}, got: {risk_tier!r}")
        return

    primary_builder = params.get("primary_builder", "codex session").strip() or "codex session"
    stack = params.get("stack", "not specified").strip() or "not specified"
    scope_problem = params.get("scope_problem", "").strip()
    scope_user = params.get("scope_user", "").strip()
    scope_mvp = params.get("scope_mvp", "").strip()
    audit_correlation_id = params.get("audit_correlation_id", "")

    slug = slugify(project_name)
    root = resolve_target_root(build_type, governance_type)
    target_dir = root / slug

    progress(f"name={project_name!r} slug={slug!r} type={governance_type} target={target_dir}")

    if target_dir.exists():
        progress("Directory already exists — returning already-existed.")
        existing = sorted(str(f) for f in target_dir.rglob("*") if f.is_file())[:50]
        print(json.dumps({
            "status": "already-existed",
            "project_path": str(target_dir),
            "slug": slug,
            "files_created": [],
            "warnings": [f"{target_dir} already existed; no files were overwritten."],
            "existing_file_count": len(existing),
        }), flush=True)
        return

    # ── bootstrap ─────────────────────────────────────────────────────────────

    progress("Running bootstrap_project.sh...")
    try:
        subprocess.run(
            ["bash", str(BOOTSTRAP), str(target_dir), governance_type, risk_tier],
            check=True,
            stderr=sys.stderr,
        )
    except subprocess.CalledProcessError as e:
        fail(f"bootstrap_project.sh failed with exit code {e.returncode}")
        return

    for extra in ["docs/adr", "docs/specs", "docs/runbooks", "archive"]:
        (target_dir / extra).mkdir(parents=True, exist_ok=True)
    progress("Created extra dirs: docs/adr docs/specs docs/runbooks archive")

    # ── project-control.yaml ──────────────────────────────────────────────────

    pc = target_dir / "project-control.yaml"
    if pc.exists():
        text = pc.read_text()
        text = text.replace("name: Project Owner", "name: Adam Goodwin")
        text = text.replace("name: Technical Lead", f"name: {primary_builder}")
        pc.write_text(text)

    # ── INITIAL_SCOPE.md ──────────────────────────────────────────────────────

    today = date.today().isoformat()
    scope_lines = [
        f"# Initial Scope — {project_name}",
        "",
        f"Generated: {today}",
        "",
        "## Classification",
        "",
        "| Field          | Value |",
        "|----------------|-------|",
        f"| Project name   | {project_name} |",
        f"| Slug / dir     | {slug} |",
        f"| Type           | {governance_type} |",
        f"| Risk tier      | {risk_tier} |",
        f"| Stack          | {stack} |",
        f"| Primary model  | {primary_builder} |",
        f"| Location       | {target_dir} |",
        "",
        "## Build approach",
        "",
        f"Primary builder: **{primary_builder}**",
        "",
    ]

    if scope_problem:
        scope_lines += [
            "## Scope brief",
            "",
            f"**Problem:** {scope_problem}",
            "",
            f"**User / consumer:** {scope_user}",
            "",
            f"**MVP:** {scope_mvp}",
            "",
        ]
    else:
        scope_lines += [
            "## Scope brief",
            "",
            "Not captured at intake. Fill in before the first coding session.",
            "",
            "- **Problem:**",
            "- **Primary user / consumer:**",
            "- **MVP:**",
            "",
        ]

    scope_lines += [
        "## First session checklist",
        "",
        "- [ ] Fill in commands in `AI_BOOTSTRAP.md`",
        "- [ ] Confirm risk tier in `project-control.yaml`",
        "- [ ] Add first ADR if architecture decisions were made at intake",
        "- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`",
    ]

    (target_dir / "INITIAL_SCOPE.md").write_text("\n".join(scope_lines) + "\n")
    progress("Created: INITIAL_SCOPE.md")

    # ── project registry ──────────────────────────────────────────────────────

    registry_id = None
    if REGISTRY.exists():
        try:
            reg = subprocess.run(
                [
                    sys.executable, str(REGISTRY), "register",
                    "--project-name", project_name,
                    "--slug", slug,
                    "--path", str(target_dir),
                    "--project-type", governance_type,
                    "--risk-tier", risk_tier,
                    "--builder", primary_builder,
                    "--stack", stack,
                    "--problem", scope_problem,
                    "--user-desc", scope_user,
                    "--mvp", scope_mvp,
                ],
                capture_output=True,
                text=True,
            )
            if reg.returncode == 0:
                progress(f"Registered: {slug}")
                for line in reg.stdout.splitlines():
                    m = re.search(r'"id"\s*:\s*(\d+)', line)
                    if m:
                        registry_id = int(m.group(1))
            else:
                progress(f"Registry non-fatal warning: {reg.stderr.strip()}")
        except Exception as e:
            progress(f"Registry non-fatal error: {e}")

    # ── result ────────────────────────────────────────────────────────────────

    files_created = sorted(str(f) for f in target_dir.rglob("*") if f.is_file())
    result: dict = {
        "status": "created",
        "project_path": str(target_dir),
        "slug": slug,
        "files_created": files_created,
        "warnings": [],
    }
    if registry_id is not None:
        result["registry_id"] = registry_id
    if audit_correlation_id:
        result["audit_correlation_id"] = audit_correlation_id

    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
