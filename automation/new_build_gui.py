#!/usr/bin/env python3
"""
New Build Agent — GUI
Pop!_OS build machine project launcher.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import traceback
from datetime import date
from pathlib import Path

# paths
GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
BOOTSTRAP = GOVERNANCE_HOME / "automation" / "bootstrap_project.sh"
REGISTRY = GOVERNANCE_HOME / "automation" / "project_registry.py"
CHANGE_CONTROL = GOVERNANCE_HOME / "automation" / "change_control.py"
PROMOTION_PLAN = GOVERNANCE_HOME / "automation" / "promotion_plan.py"
PROMOTION_CHECKS = GOVERNANCE_HOME / "automation" / "promotion_checks.py"
PROMOTION_REMEDIATE = GOVERNANCE_HOME / "automation" / "promotion_remediate.py"
PROMOTION_EXECUTE = GOVERNANCE_HOME / "automation" / "promotion_execute.py"
LOG_PATH = GOVERNANCE_HOME / "data" / "new-build-agent" / "logs" / "gui-startup.log"
CODE_ROOT = Path.home() / "code"
AGENTS_ROOT = CODE_ROOT / "agents"
APPS_ROOT = CODE_ROOT / "Applications"

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except Exception:  # pragma: no cover - startup fallback
    tk = None
    filedialog = None
    messagebox = None
    ttk = None

TkBase = tk.Tk if tk is not None else object

# theme
BG = "#171827"
SURFACE = "#20223a"
SURFACE_ALT = "#262949"
BORDER = "#393d66"
FG = "#edf1ff"
FG_DIM = "#9ca3c8"
ACCENT = "#ffb357"
ACCENT_DARK = "#d98b2d"
ENTRY_BG = "#171a30"
SUCCESS = "#b2f2bb"
ERROR = "#ff9aa2"
INFO = "#9bd0ff"

FONT = ("Sans", 10)
SMALL = ("Sans", 9)
TITLE = ("Sans", 18, "bold")
MONO = ("Monospace", 9)
PAD = 16

TYPE_MAP = {
    "app": ("application", APPS_ROOT),
    "agent": ("agent", AGENTS_ROOT),
    "tool": ("internal-tool", APPS_ROOT),
    "other": ("automation", APPS_ROOT),
}

RISK_MAP = {"normal": "medium", "heavy": "high"}


def log_startup_error(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip() + "\n")


def build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    preferred = [
        "/usr/local/sbin",
        "/usr/local/bin",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
    ]
    existing = [item for item in env.get("PATH", "").split(":") if item]
    merged: list[str] = []
    for item in preferred + existing:
        if item not in merged:
            merged.append(item)
    env["PATH"] = ":".join(merged)
    env.setdefault("GOVERNANCE_HOME", str(GOVERNANCE_HOME))
    return env


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[ _/]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def write_initial_scope(target: Path, d: dict) -> None:
    rows = [
        f"| Project name   | {d['name']} |",
        f"| Slug / dir     | {d['slug']} |",
        f"| Type           | {d['gov_type']} |",
        f"| Risk tier      | {d['risk_tier']} |",
        f"| Stack          | {d['stack']} |",
        f"| Primary model  | {d['builder']} |",
        f"| Location       | {d['target_dir']} |",
    ]
    scope_block = (
        f"**Problem:** {d['problem']}\n\n"
        f"**User / consumer:** {d['user_desc']}\n\n"
        f"**MVP:** {d['mvp']}"
    ) if d.get("problem") else (
        "Not captured at intake. Fill in before the first coding session.\n\n"
        "- **Problem:**\n- **User / consumer:**\n- **MVP:**"
    )
    text = f"""# Initial Scope — {d['name']}

Generated: {date.today().isoformat()}

## Classification

| Field          | Value |
|----------------|-------|
{chr(10).join(rows)}

## Build approach

Primary builder: **{d['builder']}**

## Scope brief

{scope_block}

## First session checklist

- [ ] Fill in commands in `AI_BOOTSTRAP.md`
- [ ] Confirm risk tier in `project-control.yaml`
- [ ] Add first ADR if architecture decisions were made at intake
- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`
"""
    (target / "INITIAL_SCOPE.md").write_text(text)


def read_project_metadata(project_path: Path) -> dict[str, str]:
    metadata = {
        "project_name": project_path.name,
        "project_type": "unknown",
        "risk_tier": "unknown",
        "builder": "unknown",
        "stack": "not specified",
    }
    control = project_path / "project-control.yaml"
    if not control.exists():
        return metadata
    for line in control.read_text(encoding="utf-8").splitlines():
        if line.startswith("project_name:"):
            metadata["project_name"] = line.split(":", 1)[1].strip() or project_path.name
        elif line.startswith("project_type:"):
            metadata["project_type"] = line.split(":", 1)[1].strip() or "unknown"
        elif line.startswith("risk_tier:"):
            metadata["risk_tier"] = line.split(":", 1)[1].strip() or "unknown"
    return metadata


class App(TkBase):
    def __init__(self):
        super().__init__()
        self.title("New Build Agent")
        self.configure(bg=BG)
        self.geometry("920x860")
        self.minsize(820, 720)
        self.resizable(True, True)

        self.v_name = tk.StringVar()
        self.v_type = tk.StringVar(value="app")
        self.v_stack = tk.StringVar()
        self.v_builder = tk.StringVar(value="claude")
        self.v_risk = tk.StringVar(value="normal")
        self.v_scope = tk.BooleanVar(value=True)
        self.v_problem = tk.StringVar()
        self.v_user = tk.StringVar()
        self.v_mvp = tk.StringVar()

        self.v_change_project = tk.StringVar()
        self.v_manifest = tk.StringVar()
        self.v_promotion_plan = tk.StringVar()
        self.v_commit_message = tk.StringVar()
        self.v_execution_report = tk.StringVar()
        self.v_known_project = tk.StringVar()
        self.v_known_count = tk.StringVar(value="Known governed projects: scanning...")
        self.v_change_summary = tk.StringVar()
        self.v_workflow_hint = tk.StringVar(value="Choose a project to begin the guided promotion flow.")
        self.known_projects: dict[str, dict] = {}
        self._pending_known_project_path: str | None = None
        self._busy_job: str | None = None
        self._busy_step = 0

        self.v_name.trace_add("write", lambda *_: self._refresh_preview())
        self.v_type.trace_add("write", lambda *_: self._refresh_preview())

        self._setup_style()
        self._build_ui()
        self._refresh_preview()
        self._refresh_change_project()
        self._update_workflow_hint()
        self.after(40, self._load_known_projects_async)

    def _load_known_projects_async(self):
        threading.Thread(target=self._load_known_projects, daemon=True).start()

    def _refresh_window_anchor(self):
        try:
            self.update_idletasks()
            self.geometry(self.geometry())
        except tk.TclError:
            pass

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=SURFACE,
            foreground=FG_DIM,
            padding=(16, 10),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", SURFACE_ALT)],
            foreground=[("selected", FG)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=ENTRY_BG,
            background=SURFACE,
            foreground=FG,
            selectbackground=SURFACE,
            selectforeground=FG,
            bordercolor=BORDER,
            arrowcolor=FG_DIM,
            insertcolor=FG,
            lightcolor=BORDER,
            darkcolor=BORDER,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", ENTRY_BG)],
            foreground=[("readonly", FG)],
        )

    def _build_ui(self):
        header = tk.Frame(self, bg=BG, padx=PAD, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="New Build Agent", bg=BG, fg=ACCENT, font=TITLE).pack(anchor="w")
        tk.Label(
            header,
            text="Create governed projects and manage upgrade manifests from one control surface.",
            bg=BG,
            fg=FG_DIM,
            font=SMALL,
        ).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))

        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True)

        self.create_tab = tk.Frame(notebook, bg=BG)
        self.change_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self.create_tab, text="Create")
        notebook.add(self.change_tab, text="Change Control")

        self._build_create_tab()
        self._build_change_tab()
        self._build_output(body)
        self._build_busy_overlay(body)

    def _card(self, parent, title: str, subtitle: str | None = None) -> tk.Frame:
        frame = tk.Frame(
            parent,
            bg=SURFACE,
            highlightthickness=1,
            highlightbackground=BORDER,
            bd=0,
            padx=14,
            pady=12,
        )
        frame.pack(fill="x", pady=(0, 12))
        tk.Label(frame, text=title, bg=SURFACE, fg=FG, font=("Sans", 11, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(
                frame,
                text=subtitle,
                bg=SURFACE,
                fg=FG_DIM,
                font=SMALL,
                wraplength=760,
                justify="left",
            ).pack(anchor="w", pady=(4, 10))
        return frame

    def _build_create_tab(self):
        wrap = tk.Frame(self.create_tab, bg=BG, padx=2, pady=2)
        wrap.pack(fill="both", expand=True, padx=2, pady=2)

        project_card = self._card(
            wrap,
            "Project Setup",
            "Create a new governed project under your standard workspace roots.",
        )
        self._row(project_card, "Name", lambda p: self._entry(p, self.v_name))

        preview = tk.Frame(project_card, bg=SURFACE)
        preview.pack(fill="x", pady=(4, 10))
        tk.Label(preview, text="Target", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._lbl_preview = tk.Label(preview, text="", bg=SURFACE, fg=INFO, font=MONO, anchor="w", justify="left")
        self._lbl_preview.pack(side="left", fill="x", expand=True)

        config_card = self._card(
            wrap,
            "Configuration",
            "Classify the project and choose the builder profile that will own the first session.",
        )
        self._row(config_card, "Type", lambda p: self._combo(p, self.v_type, ["app", "agent", "tool", "other"]))
        self._row(config_card, "Stack", lambda p: self._entry(p, self.v_stack))
        self._row(config_card, "Builder", lambda p: self._combo(p, self.v_builder, ["claude", "codex", "local", "hybrid"]))
        self._row(config_card, "Risk", lambda p: self._combo(p, self.v_risk, ["normal", "heavy"]))

        scope_card = self._card(
            wrap,
            "Scope Brief",
            "Capture the initial problem statement so the generated project opens with context instead of a blank slate.",
        )
        toggle_row = tk.Frame(scope_card, bg=SURFACE)
        toggle_row.pack(fill="x", pady=(0, 8))
        tk.Checkbutton(
            toggle_row,
            text="Include scope brief now",
            variable=self.v_scope,
            bg=SURFACE,
            fg=FG,
            selectcolor=SURFACE_ALT,
            activebackground=SURFACE,
            activeforeground=FG,
            font=SMALL,
            command=self._toggle_scope,
        ).pack(side="left")

        self._scope_rows = [
            self._scope_row(scope_card, "Problem", self.v_problem),
            self._scope_row(scope_card, "User / consumer", self.v_user),
            self._scope_row(scope_card, "MVP", self.v_mvp),
        ]
        self._toggle_scope()

        action_row = tk.Frame(wrap, bg=BG)
        action_row.pack(fill="x", pady=(4, 4))
        self._create_btn = tk.Button(
            action_row,
            text="Create Project",
            bg=ACCENT,
            fg="#1b1b2f",
            font=("Sans", 11, "bold"),
            relief="flat",
            bd=0,
            padx=26,
            pady=10,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#1b1b2f",
            command=self._on_create,
        )
        self._create_btn.pack(anchor="w")

    def _build_change_tab(self):
        wrap = tk.Frame(self.change_tab, bg=BG, padx=2, pady=2)
        wrap.pack(fill="both", expand=True, padx=2, pady=2)

        flow_card = self._card(
            wrap,
            "Guided Flow",
            "Select a project, preview the local changes, apply the local promotion, then plan and verify anything external.",
        )
        flow_row = tk.Frame(flow_card, bg=SURFACE)
        flow_row.pack(fill="x")
        for index, label in enumerate([
            "Select Project",
            "Preview Promotion",
            "Promote Folder",
            "Generate Plan",
            "Run Checks",
            "Execute GitHub",
        ]):
            chip = tk.Label(
                flow_row,
                text=f"{index + 1}. {label}",
                bg=SURFACE_ALT if index % 2 == 0 else ENTRY_BG,
                fg=FG,
                font=("Sans", 9, "bold"),
                padx=12,
                pady=8,
            )
            chip.pack(side="left")
            if index < 5:
                tk.Label(
                    flow_row,
                    text="→",
                    bg=SURFACE,
                    fg=ACCENT,
                    font=("Sans", 13, "bold"),
                    padx=8,
                ).pack(side="left")

        layout = tk.Frame(wrap, bg=BG)
        layout.pack(fill="both", expand=True)

        rail = tk.Frame(layout, bg=BG, width=250)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)

        main = tk.Frame(layout, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=(12, 0))

        next_card = self._card(
            rail,
            "Next Move",
            "This panel keeps the current flow obvious while you work.",
        )
        tk.Label(
            next_card,
            textvariable=self.v_workflow_hint,
            bg=SURFACE,
            fg=INFO,
            font=("Sans", 10, "bold"),
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        rail_card = self._card(
            rail,
            "Workflow Rail",
            "Use the steps in order. Each later action assumes the earlier one is already in place.",
        )
        tk.Label(
            rail_card,
            text=(
                "1. Pick the target project\n\n"
                "2. Generate the promotion preview\n\n"
                "3. Apply only after the preview looks right\n\n"
                "4. Generate the external sync plan\n\n"
                "5. Run local checks from that plan\n\n"
                "6. Execute the approved GitHub publish step"
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        helper = self._card(
            rail,
            "Guardrails",
            "This workflow is conservative by design.",
        )
        tk.Label(
            helper,
            text=(
                "Creates missing governance files only.\n\n"
                "Does not rename folders, delete files, or rewire dependencies."
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=210,
        ).pack(fill="x")

        project_card = self._card(
            main,
            "1. Select Project",
            "Start with the project you want to guide into governance, then refresh the local project registry if the list looks stale.",
        )

        selector_row = tk.Frame(project_card, bg=SURFACE)
        selector_row.pack(fill="x", pady=(0, 8))
        tk.Label(selector_row, text="Known project", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._known_project_combo = ttk.Combobox(
            selector_row,
            textvariable=self.v_known_project,
            values=[],
            state="readonly",
            font=FONT,
        )
        self._known_project_combo.pack(side="left", fill="x", expand=True)
        self._known_project_combo.bind("<<ComboboxSelected>>", lambda *_: self._on_known_project_selected())
        tk.Button(
            selector_row,
            text="Refresh",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._load_known_projects_async,
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            project_card,
            textvariable=self.v_known_count,
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self._row(project_card, "Project path", self._change_project_entry)

        summary = tk.Label(
            project_card,
            textvariable=self.v_change_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        )
        summary.pack(fill="x", pady=(2, 10))

        preview_card = self._card(
            main,
            "2. Preview Local Promotion",
            "Generate the local governance preview first so you can inspect exactly which files would be created.",
        )

        manifest_controls = tk.Frame(preview_card, bg=SURFACE)
        manifest_controls.pack(fill="x", pady=(0, 10))
        self._generate_btn = tk.Button(
            manifest_controls,
            text="Preview Promotion",
            bg=ACCENT,
            fg="#1b1b2f",
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#1b1b2f",
            command=self._on_generate_manifest,
        )
        self._generate_btn.pack(side="left")
        tk.Label(
            manifest_controls,
            text="Create the manifest before trying to apply anything.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        manifest_row = tk.Frame(preview_card, bg=SURFACE)
        manifest_row.pack(fill="x", pady=4)
        tk.Label(manifest_row, text="Promotion file", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._manifest_entry = tk.Entry(
            manifest_row,
            textvariable=self.v_manifest,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._manifest_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            manifest_row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_manifest,
        ).pack(side="left", padx=(8, 0))

        apply_card = self._card(
            main,
            "3. Apply Local Promotion",
            "Only after the preview looks right, apply the manifest to create any missing governance files.",
        )

        controls = tk.Frame(apply_card, bg=SURFACE)
        controls.pack(fill="x", pady=(0, 4))
        self._apply_btn = tk.Button(
            controls,
            text="Promote Folder",
            bg=SURFACE_ALT,
            fg=FG,
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_apply_manifest,
        )
        self._apply_btn.pack(side="left")

        tk.Label(
            apply_card,
            text=(
                "Promote Folder is the execution step for local governance promotion. "
                "It only creates missing governance files listed in the preview."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(10, 0))

        promotion_card = self._card(
            main,
            "4. Plan And Verify External Sync",
            "Once the local promotion is in place, generate the staged rollout plan and run the local checks it calls for.",
        )

        promotion_summary = tk.Label(
            promotion_card,
            text=(
                "This step is planning-only. It inspects project signals and writes a reviewable plan for local compliance, \
pre-promotion checks, external sync prep, approval-and-execute guidance, post-promotion checks, and rollback readiness. Nothing is pushed automatically from this step alone."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        )
        promotion_summary.pack(fill="x", pady=(0, 10))

        plan_row = tk.Frame(promotion_card, bg=SURFACE)
        plan_row.pack(fill="x", pady=4)
        tk.Label(plan_row, text="Plan file", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._promotion_entry = tk.Entry(
            plan_row,
            textvariable=self.v_promotion_plan,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._promotion_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            plan_row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_promotion_plan,
        ).pack(side="left", padx=(8, 0))

        promotion_controls = tk.Frame(promotion_card, bg=SURFACE)
        promotion_controls.pack(fill="x", pady=(10, 0))
        self._promotion_btn = tk.Button(
            promotion_controls,
            text="Generate External Plan",
            bg=ACCENT,
            fg="#1b1b2f",
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#1b1b2f",
            command=self._on_generate_promotion_plan,
        )
        self._promotion_btn.pack(side="left")

        self._precheck_btn = tk.Button(
            promotion_controls,
            text="Run Pre-Checks",
            bg=SURFACE_ALT,
            fg=FG,
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_run_prechecks,
        )
        self._precheck_btn.pack(side="left", padx=(10, 0))

        self._postcheck_btn = tk.Button(
            promotion_controls,
            text="Run Post-Checks",
            bg=SURFACE_ALT,
            fg=FG,
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_run_postchecks,
        )
        self._postcheck_btn.pack(side="left", padx=(10, 0))

        self._remediate_btn = tk.Button(
            promotion_controls,
            text="Fix Missing Test Tools",
            bg=SURFACE_ALT,
            fg=FG,
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=BORDER,
            activeforeground=FG,
            command=self._on_fix_missing_test_tools,
        )
        self._remediate_btn.pack(side="left", padx=(10, 0))

        execute_card = self._card(
            main,
            "5. Execute Approved GitHub Sync",
            "This mirrors the local git workflow: stage changes, create a commit, push the current branch, and record rollback instructions before any live issue needs a response.",
        )

        self._row(execute_card, "Commit message", lambda p: self._entry(p, self.v_commit_message))

        execute_controls = tk.Frame(execute_card, bg=SURFACE)
        execute_controls.pack(fill="x", pady=(6, 8))
        self._execute_btn = tk.Button(
            execute_controls,
            text="Execute GitHub Publish",
            bg=ACCENT,
            fg="#1b1b2f",
            font=("Sans", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#1b1b2f",
            command=self._on_execute_github,
        )
        self._execute_btn.pack(side="left")
        tk.Label(
            execute_controls,
            text="Use only after the local promotion and checks look acceptable.",
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
        ).pack(side="left", padx=(12, 0))

        report_row = tk.Frame(execute_card, bg=SURFACE)
        report_row.pack(fill="x", pady=4)
        tk.Label(report_row, text="Execute report", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._execute_entry = tk.Entry(
            report_row,
            textvariable=self.v_execution_report,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self._execute_entry.pack(side="left", fill="x", expand=True)

        tk.Label(
            execute_card,
            text=(
                "Rollback safety: the execution report records the pre-push commit, the new commit, "
                "the published branch, and the revert commands to run if production must be backed out."
            ),
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(fill="x", pady=(10, 0))

        final_card = self._card(
            main,
            "6. Safety Guardrails",
            "This guided workflow is intentionally conservative so users do not accidentally damage paths or break connections.",
        )
        tk.Label(
            final_card,
            text=(
                "What it does now:\n"
                "- creates missing governance docs from trusted templates\n"
                "- previews the exact planned files in a manifest before apply\n\n"
                "What it does not do:\n"
                "- rename or move project folders\n"
                "- delete files\n"
                "- rewrite dependency wiring or remap connections\n\n"
                "If we later add dependency-changing upgrades, they should ship as a separate preview-first workflow with stronger checks."
            ),
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        ).pack(anchor="w")

    def _build_output(self, parent):
        output_card = self._card(
            parent,
            "Activity Log",
            "Live output from project creation, audit helpers, and change-control commands.",
        )
        self._output = tk.Text(
            output_card,
            bg=ENTRY_BG,
            fg=FG,
            font=MONO,
            relief="flat",
            bd=0,
            state="disabled",
            height=14,
            wrap="word",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self._output.pack(fill="both", expand=True)
        self._output.tag_configure("ok", foreground=SUCCESS)
        self._output.tag_configure("err", foreground=ERROR)
        self._output.tag_configure("dim", foreground=FG_DIM)
        self._output.tag_configure("info", foreground=INFO)

    def _build_busy_overlay(self, parent):
        self._busy_overlay = tk.Frame(
            parent,
            bg="#101320",
            highlightthickness=1,
            highlightbackground=ACCENT,
            bd=0,
            padx=28,
            pady=24,
        )
        self._busy_icon = tk.Label(
            self._busy_overlay,
            text="☢",
            bg="#101320",
            fg=ACCENT,
            font=("Sans", 38, "bold"),
        )
        self._busy_icon.pack()
        self._busy_label = tk.Label(
            self._busy_overlay,
            text="Working...",
            bg="#101320",
            fg=FG,
            font=("Sans", 12, "bold"),
        )
        self._busy_label.pack(pady=(8, 2))
        tk.Label(
            self._busy_overlay,
            text="Running the selected workflow and updating the control surface.",
            bg="#101320",
            fg=FG_DIM,
            font=SMALL,
            justify="center",
        ).pack()

    def _animate_busy(self):
        if not self._busy_overlay.winfo_ismapped():
            self._busy_job = None
            return
        frames = [
            "◢ ☢ ◣",
            "◣ ☢ ◥",
            "◤ ☢ ◢",
            "◥ ☢ ◤",
        ]
        self._busy_icon.config(text=frames[self._busy_step % len(frames)])
        self._busy_step += 1
        self._busy_job = self.after(120, self._animate_busy)

    def _update_workflow_hint(self):
        project = self.v_change_project.get().strip()
        manifest = self.v_manifest.get().strip()
        plan = self.v_promotion_plan.get().strip()
        execution_report = self.v_execution_report.get().strip()

        if not project:
            text = "Choose a project first."
        elif not manifest:
            text = "Generate the promotion preview next."
        elif Path(manifest).exists() and not plan:
            text = "Review the preview, then apply it or move on to the external plan."
        elif not Path(plan).exists():
            text = "Generate the external sync plan next."
        elif not execution_report:
            text = "Run the pre-checks next, then execute GitHub publish when you approve the rollout."
        else:
            text = "GitHub publish has an execution report. Use post-checks and rollback notes if production validation fails."
        self.v_workflow_hint.set(text)

    def _row(self, parent, label: str, make_widget):
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, bg=parent["bg"], fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        make_widget(row).pack(side="left", fill="x", expand=True)

    def _scope_row(self, parent, label: str, var: tk.StringVar):
        row = tk.Frame(parent, bg=SURFACE)
        tk.Label(row, text=label, bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
        self._entry(row, var).pack(side="left", fill="x", expand=True)
        return row

    def _entry(self, parent, var):
        return tk.Entry(
            parent,
            textvariable=var,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )

    def _combo(self, parent, var, values):
        return ttk.Combobox(parent, textvariable=var, values=values, state="readonly", font=FONT, width=24)

    def _change_project_entry(self, parent):
        row = tk.Frame(parent, bg=SURFACE)
        entry = tk.Entry(
            row,
            textvariable=self.v_change_project,
            bg=ENTRY_BG,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            font=FONT,
            bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="Browse",
            bg=SURFACE_ALT,
            fg=FG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            command=self._browse_project,
        ).pack(side="left", padx=(8, 0))
        return row

    def _toggle_scope(self):
        for row in self._scope_rows:
            if self.v_scope.get():
                row.pack(fill="x", pady=4)
            else:
                row.pack_forget()

    def _refresh_preview(self):
        name = self.v_name.get().strip()
        if not name:
            self._lbl_preview.config(text="")
            return
        _, root = TYPE_MAP.get(self.v_type.get(), ("application", APPS_ROOT))
        self._lbl_preview.config(text=str(root / slugify(name)))

    def _refresh_change_project(self):
        if not self.v_change_project.get():
            self.v_change_project.set(str(AGENTS_ROOT))

    def _load_known_projects(self):
        values: list[str] = []
        registry_by_path: dict[str, dict] = {}

        try:
            proc = subprocess.run(
                [sys.executable, str(REGISTRY), "list"],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    registry_by_path[item.get("path", "")] = item
        except Exception:
            registry_by_path = {}

        discovered: list[dict] = []
        seen_paths: set[str] = set()

        def classify_project(child: Path, root_name: str) -> dict | None:
            if not child.is_dir():
                return None
            markers = [
                child / "project-control.yaml",
                child / "package.json",
                child / "pyproject.toml",
                child / "requirements.txt",
                child / "README.md",
            ]
            has_governance = markers[0].exists()
            has_project_signals = any(marker.exists() for marker in markers[1:])
            if not has_governance and not has_project_signals:
                return None

            item = dict(registry_by_path.get(str(child), {}))
            item.setdefault("project_name", child.name)
            item.setdefault("project_type", "unknown")
            item.setdefault("risk_tier", "unknown")
            item.setdefault("latest_audit_status", "unverified")
            item["path"] = str(child)
            item["slug"] = child.name
            item["root_group"] = root_name
            item["discovery_class"] = "governed" if has_governance else "candidate"
            item["display_status"] = item.get("latest_audit_status") or "unverified"
            if item["discovery_class"] == "candidate":
                item["display_status"] = "candidate"
            return item

        for root_name, root in (("code", CODE_ROOT), ("agents", AGENTS_ROOT), ("applications", APPS_ROOT)):
            if not root.exists():
                continue
            for child in sorted(root.iterdir()):
                resolved = str(child.resolve())
                if resolved in seen_paths:
                    continue
                item = classify_project(child, root_name)
                if item is None:
                    continue
                discovered.append(item)
                seen_paths.add(resolved)

        governed_count = 0
        candidate_count = 0
        for item in discovered:
            if item["discovery_class"] == "governed":
                governed_count += 1
            else:
                candidate_count += 1
            label = (
                f"{item['project_name']} — {item['root_group']} / {item['discovery_class']} "
                f"[{item.get('display_status') or 'unverified'}]"
            )
            self.known_projects[label] = item
            values.append(label)

        summary = (
            f"Found {governed_count} governed and {candidate_count} candidate projects across "
            f"{CODE_ROOT}, {AGENTS_ROOT}, and {APPS_ROOT}"
        )
        self.after(0, lambda: self._apply_known_projects(discovered, values, summary))

    def _apply_known_projects(self, discovered: list[dict], values: list[str], summary: str):
        self.known_projects = {
            (
                f"{item['project_name']} — {item['root_group']} / {item['discovery_class']} "
                f"[{item.get('display_status') or 'unverified'}]"
            ): item
            for item in discovered
        }
        self.v_known_count.set(summary)
        self._known_project_combo.configure(values=values)
        self._refresh_window_anchor()
        if self._pending_known_project_path:
            match = next(
                (label for label, item in self.known_projects.items() if item.get("path") == self._pending_known_project_path),
                None,
            )
            self._pending_known_project_path = None
            if match:
                self.v_known_project.set(match)
                self._on_known_project_selected()
            elif values and (not self.v_known_project.get() or self.v_known_project.get() not in self.known_projects):
                self.v_known_project.set(values[0])
                self._on_known_project_selected()
            else:
                self._update_change_summary()
        else:
            if values and (not self.v_known_project.get() or self.v_known_project.get() not in self.known_projects):
                self.v_known_project.set(values[0])
                self._on_known_project_selected()
            else:
                self._update_change_summary()
        self.after(80, self._refresh_window_anchor)

    def _refresh_known_project_for_path(self, project_path: str):
        self._pending_known_project_path = project_path
        threading.Thread(target=self._load_known_projects, daemon=True).start()
        self.after(0, self._refresh_window_anchor)

    def _on_known_project_selected(self):
        item = self.known_projects.get(self.v_known_project.get())
        if not item:
            self._update_change_summary()
            return
        self.v_change_project.set(item['path'])
        self.v_execution_report.set("")
        self._update_change_summary(item)

    def _sync_project_registry(self, project_path: str) -> None:
        project = Path(project_path).expanduser().resolve()
        metadata = read_project_metadata(project)
        subprocess.run(
            [
                sys.executable,
                str(REGISTRY),
                "register",
                "--project-name",
                metadata["project_name"],
                "--slug",
                project.name,
                "--path",
                str(project),
                "--project-type",
                metadata["project_type"],
                "--risk-tier",
                metadata["risk_tier"],
                "--builder",
                metadata["builder"],
                "--stack",
                metadata["stack"],
            ],
            check=True,
            env=build_subprocess_env(),
        )

        proc = subprocess.run(
            ["bash", str(GOVERNANCE_HOME / "automation" / "governance_check.sh"), str(project)],
            capture_output=True,
            text=True,
            check=False,
            env=build_subprocess_env(),
        )
        missing_files = []
        warnings = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("FAIL: Missing required file "):
                missing_files.append(line.removeprefix("FAIL: Missing required file "))
            elif line.startswith("WARN: "):
                warnings.append(line.removeprefix("WARN: "))

        subprocess.run(
            [
                sys.executable,
                str(REGISTRY),
                "record-audit",
                "--slug",
                project.name,
                "--path",
                str(project),
                "--status",
                "pass" if proc.returncode == 0 else "fail",
                "--missing-files",
                *missing_files,
                "--warnings",
                *warnings,
            ],
            check=True,
            env=build_subprocess_env(),
        )

    def _update_change_summary(self, item: dict | None = None, manifest: dict | None = None):
        if item is None:
            item = next((v for k, v in self.known_projects.items() if v.get('path') == self.v_change_project.get()), None)

        lines = []
        if item:
            lines.append(f"Selected project: {item.get('project_name', item.get('slug', 'unknown'))}")
            lines.append(f"Class: {item.get('discovery_class', 'unknown')}")
            if item.get('discovery_class') == 'candidate':
                lines.append('Verification: candidate project detected from local project signals')
                lines.append('Governance status: not promoted yet')
            else:
                lines.append(f"Audit status: {item.get('latest_audit_status') or 'unverified'}")
            lines.append(f"Path: {item.get('path', '')}")
        elif self.v_change_project.get():
            lines.append(f"Selected path: {self.v_change_project.get()}")

        if manifest is not None:
            actions = manifest.get('actions', [])
            if actions:
                planned = ', '.join(action.get('relative_path', '?') for action in actions)
                lines.append(f"Planned changes: create {planned}")
            else:
                lines.append('Planned changes: none; the selected project already has the guided baseline docs.')

        lines.append('Safety: this workflow only creates missing governance docs.')
        lines.append('It does not rename, move, delete, or remap dependencies.')
        lines.append('Candidate projects can be guided into governance, but they are not treated as fully governed yet.')
        lines.append('A candidate label means the app recognized a project; it is not a failure state.')
        self.v_change_summary.set('\n'.join(lines))
        self._update_workflow_hint()

    def _browse_project(self):
        selected = filedialog.askdirectory(
            title="Select governed project",
            initialdir=str(Path(self.v_change_project.get()).expanduser().resolve().parent) if self.v_change_project.get() else str(Path.home() / "code"),
        )
        if selected:
            self.v_change_project.set(selected)
            self.v_execution_report.set("")
            self._update_change_summary()

    def _browse_manifest(self):
        selected = filedialog.askopenfilename(
            title="Select manifest",
            initialdir=str((GOVERNANCE_HOME / "data" / "new-build-agent" / "exports").resolve()),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_manifest.set(selected)
            self.v_execution_report.set("")
            self._update_workflow_hint()

    def _browse_promotion_plan(self):
        selected = filedialog.askopenfilename(
            title="Select promotion plan",
            initialdir=str((GOVERNANCE_HOME / "data" / "new-build-agent" / "exports").resolve()),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_promotion_plan.set(selected)
            self.v_execution_report.set("")
            self._update_workflow_hint()

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self._create_btn.config(state=state)
        self._generate_btn.config(state=state)
        self._apply_btn.config(state=state)
        self._promotion_btn.config(state=state)
        self._precheck_btn.config(state=state)
        self._postcheck_btn.config(state=state)
        self._remediate_btn.config(state=state)
        self._execute_btn.config(state=state)
        if busy:
            self._busy_step = 0
            self._busy_overlay.place(relx=0.5, rely=0.5, anchor="center")
            self._busy_overlay.lift()
            if self._busy_job is None:
                self._animate_busy()
        else:
            if self._busy_job is not None:
                self.after_cancel(self._busy_job)
                self._busy_job = None
            self._busy_overlay.place_forget()

    def _on_create(self):
        name = self.v_name.get().strip()
        if not name:
            messagebox.showerror("Required", "Project name cannot be empty.")
            return

        gov_type, root = TYPE_MAP.get(self.v_type.get(), ("application", APPS_ROOT))
        slug = slugify(name)
        target_dir = root / slug
        risk_tier = RISK_MAP.get(self.v_risk.get(), "medium")
        builder = self.v_builder.get()
        stack = self.v_stack.get().strip() or "not specified"

        data = dict(
            name=name,
            slug=slug,
            gov_type=gov_type,
            risk_tier=risk_tier,
            stack=stack,
            builder=builder,
            target_dir=str(target_dir),
        )

        if self.v_scope.get():
            data.update(
                problem=self.v_problem.get().strip(),
                user_desc=self.v_user.get().strip(),
                mvp=self.v_mvp.get().strip(),
            )

        if target_dir.exists():
            if not messagebox.askyesno(
                "Directory exists",
                f"{target_dir}\nalready exists. Existing files will not be overwritten.\nContinue?",
            ):
                return

        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_create, args=(target_dir, gov_type, risk_tier, builder, data), daemon=True).start()

    def _run_create(self, target_dir, gov_type, risk_tier, builder, data):
        try:
            proc = subprocess.Popen(
                ["bash", str(BOOTSTRAP), str(target_dir), gov_type, risk_tier],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=build_subprocess_env(),
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                self._out(line.rstrip(), "dim")
            proc.wait()
            if proc.returncode != 0:
                self._out("Bootstrap failed.", "err")
                return

            for directory in ["docs/adr", "docs/specs", "docs/runbooks", "archive"]:
                (target_dir / directory).mkdir(parents=True, exist_ok=True)
            self._out("Created: docs/adr  docs/specs  docs/runbooks  archive", "info")

            pc = target_dir / "project-control.yaml"
            if pc.exists():
                txt = pc.read_text()
                txt = txt.replace("name: Project Owner", "name: Adam Goodwin")
                txt = txt.replace("name: Technical Lead", f"name: {builder} session")
                pc.write_text(txt)

            write_initial_scope(target_dir, data)
            self._out("Created: INITIAL_SCOPE.md", "info")

            if REGISTRY.exists():
                subprocess.run(
                    [
                        sys.executable,
                        str(REGISTRY),
                        "register",
                        "--project-name",
                        data["name"],
                        "--slug",
                        data["slug"],
                        "--path",
                        str(target_dir),
                        "--project-type",
                        gov_type,
                        "--risk-tier",
                        risk_tier,
                        "--builder",
                        builder,
                        "--stack",
                        data["stack"],
                        "--problem",
                        data.get("problem", ""),
                        "--user-desc",
                        data.get("user_desc", ""),
                        "--mvp",
                        data.get("mvp", ""),
                    ],
                    check=True,
                    env=build_subprocess_env(),
                )
                self._out("Registered project in local inventory", "info")

            self.after(0, lambda: self.v_change_project.set(str(target_dir)))
            self._out("Created baseline docs: manual + roadmap", "info")
            self._out(f"Ready: {target_dir}", "ok")

        except Exception as exc:
            self._out(f"Error: {exc}", "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_generate_manifest(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a governed project path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_generate_manifest, args=(project,), daemon=True).start()

    def _run_generate_manifest(self, project: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(CHANGE_CONTROL), "propose", "--project", project],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Promotion preview generation failed.", "err")
                return
            manifest = proc.stdout.strip()
            self.after(0, lambda: self.v_manifest.set(manifest))
            self.after(0, lambda: self.v_execution_report.set(""))
            self._out(f"Generated promotion preview: {manifest}", "ok")
            if Path(manifest).exists():
                manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
                self.after(0, lambda data=manifest_data: self._update_change_summary(manifest=data))
                self._out(Path(manifest).read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_apply_manifest(self):
        manifest = self.v_manifest.get().strip()
        if not manifest:
            messagebox.showerror("Required", "Preview or choose a promotion file first.")
            return
        if not Path(manifest).exists():
            messagebox.showerror("Missing file", f"Promotion file not found:\n{manifest}")
            return
        if not messagebox.askyesno(
            "Promote folder",
            "This will execute the local governance promotion by creating missing governed files listed in the preview.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_apply_manifest, args=(manifest,), daemon=True).start()

    def _run_apply_manifest(self, manifest: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(CHANGE_CONTROL), "apply", "--manifest", manifest],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Manifest apply failed.", "err")
                return
            if proc.stdout.strip():
                self._out(proc.stdout.strip(), "ok")
            manifest_path = Path(manifest)
            if manifest_path.exists():
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                project_path = manifest_data.get("project_path", self.v_change_project.get())
                self._sync_project_registry(project_path)
                self.after(0, lambda p=project_path: self._refresh_known_project_for_path(p))
                self.after(0, lambda data=manifest_data: self._update_change_summary(manifest=data))
                self._out(manifest_path.read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_generate_promotion_plan(self):
        project = self.v_change_project.get().strip()
        if not project:
            messagebox.showerror("Required", "Choose a project path first.")
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_generate_promotion_plan, args=(project,), daemon=True).start()

    def _on_run_prechecks(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a promotion plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Promotion plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Run pre-checks",
            "This will run the safe local pre-promotion checks listed in the plan.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_prechecks, args=(plan_path,), daemon=True).start()

    def _on_run_postchecks(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a promotion plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Promotion plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Run re-check",
            "This will run the post-promotion re-checks listed in the plan.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_postchecks, args=(plan_path,), daemon=True).start()

    def _on_fix_missing_test_tools(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a promotion plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Promotion plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Install missing test tools",
            (
                "This will try to install missing local test tooling for the selected project, "
                "starting with pytest in the project's detected Python environment, and then rerun pre-checks.\n\nContinue?"
            ),
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_fix_missing_test_tools, args=(plan_path,), daemon=True).start()

    def _on_execute_github(self):
        plan_path = self.v_promotion_plan.get().strip()
        if not plan_path:
            messagebox.showerror("Required", "Generate or choose a promotion plan first.")
            return
        if not Path(plan_path).exists():
            messagebox.showerror("Missing file", f"Promotion plan not found:\n{plan_path}")
            return
        if not messagebox.askyesno(
            "Execute GitHub publish",
            (
                "This will stage local changes in the selected project, create a git commit, push the current branch, "
                "and record rollback instructions in an execution report.\n\nContinue?"
            ),
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(
            target=self._run_execute_github,
            args=(plan_path, self.v_commit_message.get().strip()),
            daemon=True,
        ).start()

    def _run_generate_promotion_plan(self, project: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(PROMOTION_PLAN), "--project", project],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "External plan generation failed.", "err")
                return
            plan_path = proc.stdout.strip()
            self.after(0, lambda: self.v_promotion_plan.set(plan_path))
            self.after(0, lambda: self.v_execution_report.set(""))
            self._out("Generated staged promotion plan with pre-checks, approval-and-execute guidance, post-promotion checks, and rollback readiness.", "ok")
            self._out(f"Plan file: {plan_path}", "info")
            if Path(plan_path).exists():
                plan_data = json.loads(Path(plan_path).read_text(encoding="utf-8"))
                stages = plan_data.get("stages", [])
                if stages:
                    for stage in stages:
                        self._out(f"{stage.get('name')}: {stage.get('status')}", "dim")
                sync_stage = next((stage for stage in stages if stage.get("name") == "prepare_external_sync"), None)
                if sync_stage:
                    targets = sync_stage.get("targets", {})
                    relevant = [name for name, data in targets.items() if data.get("relevant")]
                    if relevant:
                        self._out("Detected targets: " + ", ".join(relevant), "info")
                    else:
                        self._out("Detected targets: none yet; this project still has a planning shell for future external sync.", "info")
                self._out(Path(plan_path).read_text(encoding="utf-8").strip(), "dim")
                self.after(0, lambda: messagebox.showinfo(
                    "External plan ready",
                    "A staged external plan was created.\n\nIt includes pre-promotion checks, approval-and-execute guidance, post-promotion checks, and rollback readiness notes for GitHub, Vercel, Supabase, Stripe, and Resend.",
                ))
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_prechecks(self, plan_path: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(PROMOTION_CHECKS), "--plan", plan_path, "--stage", "pre_promotion_checks"],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Pre-check report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                self._sync_project_registry(report_data["project_path"])
                self.after(0, lambda p=report_data["project_path"]: self._refresh_known_project_for_path(p))
                self._out(f"Pre-check status: {report_data.get('overall_status', 'unknown')}", "ok" if report_data.get('overall_status') == 'passed' else "info")
                for result in report_data.get("results", []):
                    tag = "ok" if result.get("status") == "passed" else ("err" if result.get("status") == "failed" else "info")
                    self._out(f"{result.get('name')}: {result.get('status')}", tag)
                    if result.get("stdout"):
                        self._out(result.get("stdout").strip(), "dim")
                    if result.get("stderr"):
                        self._out(result.get("stderr").strip(), "err")
                if report_data.get("overall_status") == "passed":
                    self.after(0, lambda: messagebox.showinfo("Pre-checks passed", "Local pre-promotion checks passed. External targets still require explicit approval."))
                elif report_data.get("overall_status") == "manual_required":
                    self.after(0, lambda: messagebox.showinfo("Manual review required", "Some pre-checks require manual review before promotion."))
                else:
                    self.after(0, lambda: messagebox.showwarning("Pre-checks failed", "One or more pre-promotion checks failed. Review the report before proceeding."))
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_postchecks(self, plan_path: str):
        try:
            proc = subprocess.run(
                [sys.executable, str(PROMOTION_CHECKS), "--plan", plan_path, "--stage", "post_promotion_checks"],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Re-check report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                self._sync_project_registry(report_data["project_path"])
                self.after(0, lambda p=report_data["project_path"]: self._refresh_known_project_for_path(p))
                self._out(
                    f"Re-check status: {report_data.get('overall_status', 'unknown')}",
                    "ok" if report_data.get("overall_status") == "passed" else "info",
                )
                for result in report_data.get("results", []):
                    tag = "ok" if result.get("status") == "passed" else ("err" if result.get("status") == "failed" else "info")
                    self._out(f"{result.get('name')}: {result.get('status')}", tag)
                    if result.get("stdout"):
                        self._out(result.get("stdout").strip(), "dim")
                    if result.get("stderr"):
                        self._out(result.get("stderr").strip(), "err")
                if report_data.get("overall_status") == "passed":
                    self.after(0, lambda: messagebox.showinfo("Re-checks passed", "Post-promotion re-checks passed."))
                elif report_data.get("overall_status") == "manual_required":
                    self.after(0, lambda: messagebox.showinfo("Manual review required", "Some post-promotion re-checks require manual review."))
                else:
                    self.after(0, lambda: messagebox.showwarning("Re-checks failed", "One or more post-promotion re-checks failed. Review the report before proceeding."))
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_fix_missing_test_tools(self, plan_path: str):
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(PROMOTION_REMEDIATE),
                    "--plan",
                    plan_path,
                    "--tool",
                    "pytest",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Remediation report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                status = report_data.get("status", "unknown")
                if status == "failed":
                    self._out(report_data.get("error", "Test tool remediation failed."), "err")
                    self.after(0, lambda: messagebox.showwarning("Remediation failed", "The missing test tool could not be installed automatically."))
                    return
                if status == "already_present":
                    self._out("pytest is already available in the detected project environment.", "ok")
                else:
                    self._out("Installed pytest in the detected project environment.", "ok")
                python_command = " ".join(report_data.get("python_command", []))
                if python_command:
                    self._out(f"Python environment: {python_command}", "info")
                if report_data.get("stdout"):
                    self._out(report_data["stdout"], "dim")
                self._out("Re-running pre-checks after remediation...", "info")
                self._run_prechecks(plan_path)
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_execute_github(self, plan_path: str, commit_message: str):
        try:
            command = [
                sys.executable,
                str(PROMOTION_EXECUTE),
                "--plan",
                plan_path,
                "--target",
                "github",
            ]
            if commit_message:
                command.extend(["--commit-message", commit_message])
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                env=build_subprocess_env(),
            )
            report_path = proc.stdout.strip()
            if report_path:
                self.after(0, lambda p=report_path: self.v_execution_report.set(p))
                self.after(0, self._update_workflow_hint)
                self._out(f"Execute report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
                status = report_data.get("status", "unknown")
                self._out(
                    f"GitHub execute status: {status}",
                    "ok" if status == "executed" else "err",
                )
                if status == "executed":
                    self._out(f"Repo: {report_data.get('repo_name', 'unknown')}", "info")
                    self._out(f"Branch: {report_data.get('branch', 'unknown')}", "info")
                    self._out(f"Previous head: {report_data.get('previous_head', 'unknown')}", "dim")
                    self._out(f"New head: {report_data.get('new_head', 'unknown')}", "ok")
                    if report_data.get("pr_url"):
                        self._out(f"Draft PR: {report_data['pr_url']}", "info")
                    self._out(report_data.get("rollback_note", ""), "info")
                    for command_text in report_data.get("rollback_commands", []):
                        self._out(command_text, "dim")
                    self.after(0, lambda: messagebox.showinfo("GitHub publish complete", "GitHub publish completed and rollback instructions were recorded."))
                else:
                    self._out(report_data.get("error", "GitHub publish failed."), "err")
                    self.after(0, lambda: messagebox.showwarning("GitHub publish failed", "The GitHub publish step failed. Review the execution report and output log."))
            elif proc.stderr.strip():
                self._out(proc.stderr.strip(), "err")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _clear_output(self):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.config(state="disabled")

    def _out(self, text: str, tag: str = ""):
        if not text:
            return

        def _do():
            self._output.config(state="normal")
            self._output.insert("end", text + "\n", tag)
            self._output.see("end")
            self._output.config(state="disabled")

        self.after(0, _do)


if __name__ == "__main__":
    try:
        if tk is None:
            raise RuntimeError(
                "Tkinter is not available for this Python installation. "
                "Install python3-tk and relaunch New Build Agent."
            )
        App().mainloop()
    except Exception as exc:
        details = "".join(traceback.format_exception(exc))
        log_startup_error(details)
        if messagebox is not None and tk is not None:
            try:
                fallback = tk.Tk()
                fallback.withdraw()
                messagebox.showerror(
                    "New Build Agent failed to start",
                    f"{exc}\n\nStartup log: {LOG_PATH}",
                )
                fallback.destroy()
            except Exception:
                pass
        print(f"New Build Agent failed to start: {exc}", file=sys.stderr)
        print(f"Startup log: {LOG_PATH}", file=sys.stderr)
        raise SystemExit(1)
