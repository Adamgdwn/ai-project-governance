#!/usr/bin/env python3
"""Generate and apply structured upgrade manifests for New Build Agent."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "templates" / "project"
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-agent" / "exports"
GOVERNANCE_BLOCK_ID = "current-build-pathway"
GOVERNANCE_BLOCK_START = f"<!-- GOVERNANCE-MANAGED-START: {GOVERNANCE_BLOCK_ID} -->"
GOVERNANCE_BLOCK_END = f"<!-- GOVERNANCE-MANAGED-END: {GOVERNANCE_BLOCK_ID} -->"
COMMON_INSTRUCTION_BLOCK = f"""{GOVERNANCE_BLOCK_START}
## Governance Managed Instructions

- Read `START_HERE.md` first.
- Follow `docs/current-build-pathway.md` for the active plan, chunk status, validation, and next handoff.
- Run `bash scripts/governance-preflight.sh` before substantial code or configuration changes when available.
- Review `project-control.yaml` and open exceptions before implementation.
- Capture material work, decisions, validation, and handoffs with `date -Iseconds`.
- Work in context-window-friendly chunks with one objective, clear files, validation, and handoff notes.
{GOVERNANCE_BLOCK_END}
"""

MANAGED_INSTRUCTION_BLOCKS = {
    "AGENTS.md": COMMON_INSTRUCTION_BLOCK,
    "AI_BOOTSTRAP.md": COMMON_INSTRUCTION_BLOCK,
    "CLAUDE.md": f"""{GOVERNANCE_BLOCK_START}
## Governance Managed Instructions

Read `START_HERE.md` first, then `AI_BOOTSTRAP.md`. Follow `docs/current-build-pathway.md` for active work, timestamps, validation, and handoff notes.
{GOVERNANCE_BLOCK_END}
""",
}

MANAGED_INSTRUCTION_FRAGMENTS = {
    "AGENTS.md": ["START_HERE.md", "docs/current-build-pathway.md", "date -Iseconds", "context-window-friendly"],
    "AI_BOOTSTRAP.md": ["START_HERE.md", "docs/current-build-pathway.md", "date -Iseconds", "context-window-friendly"],
    "CLAUDE.md": ["START_HERE.md", "AI_BOOTSTRAP.md"],
}

CORE_BASELINE_FILES = {
    "README.md": TEMPLATE_ROOT / "README.template.md",
    "START_HERE.md": TEMPLATE_ROOT / "START_HERE.template.md",
    "project-control.yaml": TEMPLATE_ROOT / "project-control.template.yaml",
    "AGENTS.md": TEMPLATE_ROOT / "AGENTS.template.md",
    "CLAUDE.md": TEMPLATE_ROOT / "CLAUDE.template.md",
    "AI_BOOTSTRAP.md": TEMPLATE_ROOT / "AI_BOOTSTRAP.template.md",
    "docs/manual.md": TEMPLATE_ROOT / "docs" / "manual.template.md",
    "docs/roadmap.md": TEMPLATE_ROOT / "docs" / "roadmap.template.md",
    "docs/current-build-pathway.md": TEMPLATE_ROOT / "docs" / "current-build-pathway.template.md",
    "docs/architecture.md": TEMPLATE_ROOT / "docs" / "architecture.template.md",
    "docs/deployment-guide.md": TEMPLATE_ROOT / "docs" / "deployment-guide.template.md",
    "docs/runbook.md": TEMPLATE_ROOT / "docs" / "runbook.template.md",
    "docs/CHANGELOG.md": TEMPLATE_ROOT / "docs" / "CHANGELOG.template.md",
    "docs/risks/risk-register.md": TEMPLATE_ROOT / "docs" / "risk-register.template.md",
    "scripts/governance-check.sh": TEMPLATE_ROOT / "scripts" / "governance-check.template.sh",
    "scripts/governance-preflight.sh": TEMPLATE_ROOT / "scripts" / "governance-preflight.template.sh",
}

AGENT_ONLY_FILES = {
    "docs/agent-inventory.md": TEMPLATE_ROOT / "docs" / "agent-inventory.template.md",
    "docs/model-registry.md": TEMPLATE_ROOT / "docs" / "model-registry.template.md",
    "docs/prompt-register.md": TEMPLATE_ROOT / "docs" / "prompt-register.template.md",
    "docs/tool-permission-matrix.md": TEMPLATE_ROOT / "docs" / "tool-permission-matrix.template.md",
}


def infer_project_profile(project_path: Path) -> dict:
    has_package = (project_path / "package.json").exists()
    has_pyproject = (project_path / "pyproject.toml").exists()
    has_requirements = (project_path / "requirements.txt").exists()
    has_next = (project_path / "next.config.js").exists() or (project_path / "next.config.mjs").exists() or (project_path / "next.config.ts").exists()
    has_supabase = (project_path / "supabase").exists()
    has_stripe = False
    package_file = project_path / "package.json"
    if package_file.exists():
        try:
            pkg = json.loads(package_file.read_text(encoding="utf-8"))
            blob = json.dumps(pkg).lower()
            has_stripe = "stripe" in blob
        except Exception:
            pass
    if not has_stripe:
        env_example = project_path / ".env.example"
        if env_example.exists():
            has_stripe = "stripe" in env_example.read_text(encoding="utf-8", errors="ignore").lower()

    if project_path.name.endswith("agent") or "agent" in project_path.name.lower():
        project_type = "agent"
    elif has_package or has_next:
        project_type = "application"
    elif has_pyproject or has_requirements:
        project_type = "automation"
    else:
        project_type = "application"

    risk_tier = "high" if has_stripe else ("medium" if has_supabase or has_package or has_pyproject else "low")
    governance_level = {
        "low": "1",
        "medium": "2",
        "high": "3",
        "critical": "4",
    }[risk_tier]
    handles_money = has_stripe
    handles_sensitive_data = has_supabase or any((project_path / name).exists() for name in [".env.local", ".env", ".env.example"])

    return {
        "project_name": project_path.name,
        "project_type": project_type,
        "risk_tier": risk_tier,
        "governance_level": governance_level,
        "handles_money": handles_money,
        "handles_sensitive_data": handles_sensitive_data,
        "is_agent": project_type == "agent",
    }


def baseline_files_for_profile(profile: dict) -> dict[str, Path]:
    files = dict(CORE_BASELINE_FILES)
    if profile.get("is_agent"):
        files.update(AGENT_ONLY_FILES)
    return files


def has_managed_instruction_guidance(relative_path: str, text: str) -> bool:
    if GOVERNANCE_BLOCK_START in text and GOVERNANCE_BLOCK_END in text:
        return True
    required_fragments = MANAGED_INSTRUCTION_FRAGMENTS.get(relative_path, [])
    return bool(required_fragments) and all(fragment in text for fragment in required_fragments)


def build_manifest(project_path: Path) -> dict:
    project_path = project_path.expanduser().resolve()
    profile = infer_project_profile(project_path)
    actions = []
    for relative_path, template_path in baseline_files_for_profile(profile).items():
        target = project_path / relative_path
        if not target.exists():
            action = {
                "action": "create_file",
                "relative_path": relative_path,
                "template": str(template_path),
                "reason": f"Required governance file missing: {relative_path}",
            }
            if relative_path == "project-control.yaml":
                action["render_context"] = profile
            if relative_path in {"scripts/governance-check.sh", "scripts/governance-preflight.sh"}:
                action["chmod"] = "+x"
            actions.append(action)

    for relative_path, block in MANAGED_INSTRUCTION_BLOCKS.items():
        target = project_path / relative_path
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        if has_managed_instruction_guidance(relative_path, text):
            continue
        actions.append(
            {
                "action": "append_managed_block",
                "relative_path": relative_path,
                "block_id": GOVERNANCE_BLOCK_ID,
                "content": block,
                "reason": f"Existing instruction file is missing current governance guidance: {relative_path}",
            }
        )

    manifest_kind = "promotion" if not (project_path / "project-control.yaml").exists() else "upgrade"
    create_count = sum(1 for action in actions if action.get("action") == "create_file")
    append_count = sum(1 for action in actions if action.get("action") == "append_managed_block")
    return {
        "manifest_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project_path),
        "project_slug": project_path.name,
        "project_profile": profile,
        "manifest_kind": manifest_kind,
        "status": "pending",
        "summary": (
            f"{manifest_kind.title()} manifest with {create_count} missing governance file(s) "
            f"and {append_count} managed instruction append(s)"
        ),
        "actions": actions,
        "rollback_note": (
            "Creates missing governance files and appends clearly marked managed instruction blocks. "
            "Remove newly created files or the marked managed blocks manually if you want to revert."
        ),
    }


def render_template(template: Path, context: dict) -> str:
    text = template.read_text(encoding="utf-8")
    text = text.replace("YYYY-MM-DD", datetime.now(timezone.utc).isoformat())
    if template.name == "project-control.template.yaml":
        governance_level = context.get("governance_level", {
            "low": "1",
            "medium": "2",
            "high": "3",
            "critical": "4",
        }.get(context["risk_tier"], "2"))
        text = text.replace("example-project", context["project_name"])
        text = text.replace("project_type: application", f"project_type: {context['project_type']}")
        text = text.replace("risk_tier: medium", f"risk_tier: {context['risk_tier']}")
        text = text.replace("governance_level: 2", f"governance_level: {governance_level}")
        text = text.replace("name: Project Owner", "name: Adam Goodwin")
        text = text.replace("name: Technical Lead", "name: governed promotion")
        text = text.replace("handles_sensitive_data: false", f"handles_sensitive_data: {'true' if context['handles_sensitive_data'] else 'false'}")
        text = text.replace("handles_money: false", f"handles_money: {'true' if context['handles_money'] else 'false'}")
        if context.get("is_agent"):
            text = text.replace("applicable: false", "applicable: true")
            text = text.replace("autonomy_level: A0", "autonomy_level: A1")
    return text


def write_manifest(manifest: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        output = EXPORT_ROOT / f"upgrade-{manifest['project_slug']}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding='utf-8')
    return output


def apply_manifest(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    project_path = Path(manifest['project_path'])
    profile = manifest.get('project_profile', infer_project_profile(project_path))
    for action in manifest.get('actions', []):
        target = project_path / action['relative_path']
        if action.get('action') == 'create_file':
            if target.exists():
                continue
            template = Path(action['template'])
            target.parent.mkdir(parents=True, exist_ok=True)
            content = render_template(template, action.get('render_context', profile))
            target.write_text(content, encoding='utf-8')
            if action.get('chmod') == '+x':
                target.chmod(target.stat().st_mode | 0o111)
        elif action.get('action') == 'append_managed_block':
            if not target.exists():
                raise FileNotFoundError(f"Instruction file disappeared before apply: {target}")
            text = target.read_text(encoding='utf-8', errors='ignore')
            if has_managed_instruction_guidance(action['relative_path'], text):
                continue
            separator = "\n\n" if text.endswith("\n") else "\n\n"
            target.write_text(f"{text}{separator}{action['content'].rstrip()}\n", encoding='utf-8')
        else:
            raise ValueError(f"Unsupported action: {action}")
    manifest['status'] = 'applied'
    manifest['applied_at'] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding='utf-8')


def cmd_propose(args: argparse.Namespace) -> int:
    manifest = build_manifest(Path(args.project))
    out = write_manifest(manifest, Path(args.output) if args.output else None)
    print(out)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    apply_manifest(Path(args.manifest).expanduser().resolve())
    print(f"Applied {args.manifest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Structured change control for New Build Agent.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    propose = subparsers.add_parser('propose', help='Generate an upgrade or promotion manifest for a project.')
    propose.add_argument('--project', required=True, help='Path to the project')
    propose.add_argument('--output', help='Optional output path for the manifest JSON')
    propose.set_defaults(func=cmd_propose)

    apply_cmd = subparsers.add_parser('apply', help='Apply a previously generated manifest.')
    apply_cmd.add_argument('--manifest', required=True, help='Path to the manifest JSON')
    apply_cmd.set_defaults(func=cmd_apply)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
