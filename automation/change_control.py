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

CORE_BASELINE_FILES = {
    "project-control.yaml": TEMPLATE_ROOT / "project-control.template.yaml",
    "AGENTS.md": TEMPLATE_ROOT / "AGENTS.template.md",
    "docs/manual.md": TEMPLATE_ROOT / "docs" / "manual.template.md",
    "docs/roadmap.md": TEMPLATE_ROOT / "docs" / "roadmap.template.md",
    "docs/architecture.md": TEMPLATE_ROOT / "docs" / "architecture.template.md",
    "docs/deployment-guide.md": TEMPLATE_ROOT / "docs" / "deployment-guide.template.md",
    "docs/runbook.md": TEMPLATE_ROOT / "docs" / "runbook.template.md",
    "docs/CHANGELOG.md": TEMPLATE_ROOT / "docs" / "CHANGELOG.template.md",
    "docs/risks/risk-register.md": TEMPLATE_ROOT / "docs" / "risk-register.template.md",
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
    handles_money = has_stripe
    handles_sensitive_data = has_supabase or any((project_path / name).exists() for name in [".env.local", ".env", ".env.example"])

    return {
        "project_name": project_path.name,
        "project_type": project_type,
        "risk_tier": risk_tier,
        "handles_money": handles_money,
        "handles_sensitive_data": handles_sensitive_data,
        "is_agent": project_type == "agent",
    }


def baseline_files_for_profile(profile: dict) -> dict[str, Path]:
    files = dict(CORE_BASELINE_FILES)
    if profile.get("is_agent"):
        files.update(AGENT_ONLY_FILES)
    return files


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
            if relative_path == "scripts/governance-preflight.sh":
                action["chmod"] = "+x"
            actions.append(action)

    manifest_kind = "promotion" if not (project_path / "project-control.yaml").exists() else "upgrade"
    return {
        "manifest_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project_path),
        "project_slug": project_path.name,
        "project_profile": profile,
        "manifest_kind": manifest_kind,
        "status": "pending",
        "summary": f"{manifest_kind.title()} manifest with {len(actions)} missing governance file(s)",
        "actions": actions,
        "rollback_note": "Only creates missing governance files. Remove newly created files manually if you want to revert.",
    }


def render_template(template: Path, context: dict) -> str:
    text = template.read_text(encoding="utf-8")
    if template.name == "project-control.template.yaml":
        text = text.replace("example-project", context["project_name"])
        text = text.replace("project_type: application", f"project_type: {context['project_type']}")
        text = text.replace("risk_tier: medium", f"risk_tier: {context['risk_tier']}")
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
        if action.get('action') != 'create_file':
            raise ValueError(f"Unsupported action: {action}")
        target = project_path / action['relative_path']
        if target.exists():
            continue
        template = Path(action['template'])
        target.parent.mkdir(parents=True, exist_ok=True)
        content = render_template(template, action.get('render_context', profile))
        target.write_text(content, encoding='utf-8')
        if action.get('chmod') == '+x':
            target.chmod(target.stat().st_mode | 0o111)
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
