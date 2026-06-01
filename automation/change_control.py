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
DOCUMENT_CONTROL_STANDARD = REPO_ROOT / "docs" / "standards" / "document-control-standard.md"
DOCUMENT_CONTROL_TARGET = "docs/standards/document-control-standard.md"
GOVERNANCE_BLOCK_ID = "current-build-pathway"
GOVERNANCE_BLOCK_START = f"<!-- GOVERNANCE-MANAGED-START: {GOVERNANCE_BLOCK_ID} -->"
GOVERNANCE_BLOCK_END = f"<!-- GOVERNANCE-MANAGED-END: {GOVERNANCE_BLOCK_ID} -->"
ENGINEERING_POLICY_BLOCK_ID = "durable-development-engineering-policy"
ENGINEERING_POLICY_BLOCK_START = f"<!-- GOVERNANCE-MANAGED-START: {ENGINEERING_POLICY_BLOCK_ID} -->"
ENGINEERING_POLICY_BLOCK_END = f"<!-- GOVERNANCE-MANAGED-END: {ENGINEERING_POLICY_BLOCK_ID} -->"
USE_CASE_BLOCK_ID = "engineering-governance-by-use-case"
USE_CASE_BLOCK_START = f"<!-- GOVERNANCE-MANAGED-START: {USE_CASE_BLOCK_ID} -->"
USE_CASE_BLOCK_END = f"<!-- GOVERNANCE-MANAGED-END: {USE_CASE_BLOCK_ID} -->"
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
COMMON_ENGINEERING_POLICY_BLOCK = f"""{ENGINEERING_POLICY_BLOCK_START}
## Engineering Policy Managed Instructions

- Read `docs/policy/durable-development-engineering-policy.md` before meaningful implementation work.
- Apply the durable development standard: smallest useful thing, safest durable way.
- Treat "works locally" as incomplete until review, risk-appropriate tests, security/privacy checks, documentation, and rollback expectations are addressed.
- Challenge risky shortcuts, hidden failures, unnecessary dependencies, weak authorization, dead code, and stale documentation.
{ENGINEERING_POLICY_BLOCK_END}
"""
COMMON_USE_CASE_BLOCK = f"""{USE_CASE_BLOCK_START}
## Use-Case Governance Managed Instructions

- Review `docs/standards/engineering-governance-by-use-case.md` before meaningful implementation work.
- Confirm the requested work matches the project's `use_case.primary` classification.
- Use use-case guidance to select appropriate controls, but do not override the selected `risk_tier` or `governance_level` unless that change is explicit.
{USE_CASE_BLOCK_END}
"""

MANAGED_INSTRUCTION_BLOCKS = {
    "AGENTS.md": [
        {
            "block_id": GOVERNANCE_BLOCK_ID,
            "start": GOVERNANCE_BLOCK_START,
            "end": GOVERNANCE_BLOCK_END,
            "content": COMMON_INSTRUCTION_BLOCK,
            "fragments": ["START_HERE.md", "docs/current-build-pathway.md", "date -Iseconds", "context-window-friendly"],
        },
        {
            "block_id": ENGINEERING_POLICY_BLOCK_ID,
            "start": ENGINEERING_POLICY_BLOCK_START,
            "end": ENGINEERING_POLICY_BLOCK_END,
            "content": COMMON_ENGINEERING_POLICY_BLOCK,
            "fragments": ["docs/policy/durable-development-engineering-policy.md", "works locally", "safest durable way"],
        },
        {
            "block_id": USE_CASE_BLOCK_ID,
            "start": USE_CASE_BLOCK_START,
            "end": USE_CASE_BLOCK_END,
            "content": COMMON_USE_CASE_BLOCK,
            "fragments": ["docs/standards/engineering-governance-by-use-case.md", "use_case.primary", "do not override"],
        },
    ],
    "AI_BOOTSTRAP.md": [
        {
            "block_id": GOVERNANCE_BLOCK_ID,
            "start": GOVERNANCE_BLOCK_START,
            "end": GOVERNANCE_BLOCK_END,
            "content": COMMON_INSTRUCTION_BLOCK,
            "fragments": ["START_HERE.md", "docs/current-build-pathway.md", "date -Iseconds", "context-window-friendly"],
        },
        {
            "block_id": ENGINEERING_POLICY_BLOCK_ID,
            "start": ENGINEERING_POLICY_BLOCK_START,
            "end": ENGINEERING_POLICY_BLOCK_END,
            "content": COMMON_ENGINEERING_POLICY_BLOCK,
            "fragments": ["docs/policy/durable-development-engineering-policy.md", "works locally", "safest durable way"],
        },
        {
            "block_id": USE_CASE_BLOCK_ID,
            "start": USE_CASE_BLOCK_START,
            "end": USE_CASE_BLOCK_END,
            "content": COMMON_USE_CASE_BLOCK,
            "fragments": ["docs/standards/engineering-governance-by-use-case.md", "use_case.primary", "do not override"],
        },
    ],
    "CLAUDE.md": [
        {
            "block_id": GOVERNANCE_BLOCK_ID,
            "start": GOVERNANCE_BLOCK_START,
            "end": GOVERNANCE_BLOCK_END,
            "content": f"""{GOVERNANCE_BLOCK_START}
## Governance Managed Instructions

Read `START_HERE.md` first, then `AI_BOOTSTRAP.md`. Follow `docs/current-build-pathway.md` for active work, timestamps, validation, and handoff notes.
{GOVERNANCE_BLOCK_END}
""",
            "fragments": ["START_HERE.md", "AI_BOOTSTRAP.md"],
        },
        {
            "block_id": ENGINEERING_POLICY_BLOCK_ID,
            "start": ENGINEERING_POLICY_BLOCK_START,
            "end": ENGINEERING_POLICY_BLOCK_END,
            "content": f"""{ENGINEERING_POLICY_BLOCK_START}
## Engineering Policy Managed Instructions

Read `docs/policy/durable-development-engineering-policy.md` before meaningful implementation work. Treat "works locally" as incomplete until risk-appropriate validation, review readiness, security/privacy checks, documentation, and rollback expectations are addressed.
{ENGINEERING_POLICY_BLOCK_END}
""",
            "fragments": ["docs/policy/durable-development-engineering-policy.md", "works locally"],
        },
        {
            "block_id": USE_CASE_BLOCK_ID,
            "start": USE_CASE_BLOCK_START,
            "end": USE_CASE_BLOCK_END,
            "content": f"""{USE_CASE_BLOCK_START}
## Use-Case Governance Managed Instructions

Review `docs/standards/engineering-governance-by-use-case.md` before meaningful implementation work. Use it to select appropriate controls, but do not override the selected `risk_tier` or `governance_level` unless that change is explicit.
{USE_CASE_BLOCK_END}
""",
            "fragments": ["docs/standards/engineering-governance-by-use-case.md", "do not override"],
        },
    ],
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
    "docs/policy/durable-development-engineering-policy.md": TEMPLATE_ROOT / "docs" / "policy" / "durable-development-engineering-policy.template.md",
    "docs/standards/engineering-governance-by-use-case.md": TEMPLATE_ROOT / "docs" / "standards" / "engineering-governance-by-use-case.template.md",
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

USE_CASE_BY_PROJECT_TYPE = {
    "application": "Web application / SaaS",
    "website": "Static / marketing website",
    "service": "Backend API / integration service",
    "internal-tool": "Internal utility / script",
    "automation": "Workflow automation",
    "infrastructure": "Infrastructure / deployment code",
    "documentation": "Static / marketing website",
    "agent": "AI agent with tools",
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
        "use_case": USE_CASE_BY_PROJECT_TYPE.get(project_type, "Web application / SaaS"),
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


def has_managed_instruction_guidance(block: dict, text: str) -> bool:
    if block["start"] in text and block["end"] in text:
        return True
    required_fragments = block.get("fragments", [])
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

    for relative_path, blocks in MANAGED_INSTRUCTION_BLOCKS.items():
        target = project_path / relative_path
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        for block in blocks:
            if has_managed_instruction_guidance(block, text):
                continue
            actions.append(
                {
                    "action": "append_managed_block",
                    "relative_path": relative_path,
                    "block_id": block["block_id"],
                    "content": block["content"],
                    "reason": f"Existing instruction file is missing {block['block_id']} guidance: {relative_path}",
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


def build_document_control_manifest(project_path: Path) -> dict:
    project_path = project_path.expanduser().resolve()
    source_text = DOCUMENT_CONTROL_STANDARD.read_text(encoding="utf-8")
    target = project_path / DOCUMENT_CONTROL_TARGET
    actions = []
    if not target.exists() or target.read_text(encoding="utf-8", errors="ignore") != source_text:
        actions.append(
            {
                "action": "sync_file",
                "relative_path": DOCUMENT_CONTROL_TARGET,
                "source": str(DOCUMENT_CONTROL_STANDARD),
                "reason": "Install or refresh the portable document-control standard for consistent governed documentation.",
            }
        )

    return {
        "manifest_version": 3,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project_path),
        "project_slug": project_path.name,
        "manifest_kind": "document_control_update",
        "status": "pending",
        "summary": f"Document-control update with {len(actions)} file sync(s)",
        "actions": actions,
        "rollback_note": (
            "Syncs only docs/standards/document-control-standard.md. "
            "Restore that file from git history or a backup if you want to revert."
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
        text = text.replace("primary: Web application / SaaS", f"primary: {context.get('use_case', USE_CASE_BY_PROJECT_TYPE.get(context['project_type'], 'Web application / SaaS'))}")
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
        prefix = "document-control" if manifest.get("manifest_kind") == "document_control_update" else "upgrade"
        output = EXPORT_ROOT / f"{prefix}-{manifest['project_slug']}-{stamp}.json"
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
            block = next(
                (
                    candidate
                    for candidate in MANAGED_INSTRUCTION_BLOCKS.get(action['relative_path'], [])
                    if candidate["block_id"] == action.get("block_id")
                ),
                None,
            )
            if block and has_managed_instruction_guidance(block, text):
                continue
            separator = "\n\n" if text.endswith("\n") else "\n\n"
            target.write_text(f"{text}{separator}{action['content'].rstrip()}\n", encoding='utf-8')
        elif action.get('action') == 'sync_file':
            source = Path(action['source'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
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


def cmd_propose_document_control(args: argparse.Namespace) -> int:
    manifest = build_document_control_manifest(Path(args.project))
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

    document_control = subparsers.add_parser('propose-document-control', help='Generate a manifest that syncs the portable document-control standard into a project.')
    document_control.add_argument('--project', required=True, help='Path to the project')
    document_control.add_argument('--output', help='Optional output path for the manifest JSON')
    document_control.set_defaults(func=cmd_propose_document_control)

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
