#!/usr/bin/env python3
"""
New Build Agent — GUI
Pop!_OS build machine project launcher.
"""

from __future__ import annotations

import json
import re
import subprocess
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# paths
GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
BOOTSTRAP = GOVERNANCE_HOME / "automation" / "bootstrap_project.sh"
REGISTRY = GOVERNANCE_HOME / "automation" / "project_registry.py"
CHANGE_CONTROL = GOVERNANCE_HOME / "automation" / "change_control.py"
PROMOTION_PLAN = GOVERNANCE_HOME / "automation" / "promotion_plan.py"
PROMOTION_CHECKS = GOVERNANCE_HOME / "automation" / "promotion_checks.py"
CODE_ROOT = Path.home() / "code"
AGENTS_ROOT = CODE_ROOT / "agents"
APPS_ROOT = CODE_ROOT / "Applications"

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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
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
        self.v_known_project = tk.StringVar()
        self.v_known_count = tk.StringVar(value="Known governed projects: scanning...")
        self.v_change_summary = tk.StringVar()
        self.known_projects: dict[str, dict] = {}

        self.v_name.trace_add("write", lambda *_: self._refresh_preview())
        self.v_type.trace_add("write", lambda *_: self._refresh_preview())

        self._setup_style()
        self._build_ui()
        self._refresh_preview()
        self._refresh_change_project()
        self._load_known_projects()
        self.after(40, self._finalize_initial_window)

    def _finalize_initial_window(self):
        # Let the WM receive a stable mapped geometry before combobox popdowns open.
        try:
            self.update_idletasks()
            self.geometry(self.geometry())
            self.deiconify()
            self.lift()
            self.focus_force()
            self.after(120, self._refresh_window_anchor)
        except tk.TclError:
            pass

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

        change_card = self._card(
            wrap,
            "Upgrade Manifests",
            "Generate a reviewable manifest for missing governance docs, then apply it only after you like the plan.",
        )

        selector_row = tk.Frame(change_card, bg=SURFACE)
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
            command=self._load_known_projects,
        ).pack(side="left", padx=(8, 0))

        tk.Label(
            change_card,
            textvariable=self.v_known_count,
            bg=SURFACE,
            fg=FG_DIM,
            font=SMALL,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self._row(change_card, "Project path", self._change_project_entry)

        summary = tk.Label(
            change_card,
            textvariable=self.v_change_summary,
            bg=SURFACE,
            fg=INFO,
            font=SMALL,
            justify="left",
            anchor="w",
            wraplength=760,
        )
        summary.pack(fill="x", pady=(2, 10))

        manifest_row = tk.Frame(change_card, bg=SURFACE)
        manifest_row.pack(fill="x", pady=4)
        tk.Label(manifest_row, text="Manifest", bg=SURFACE, fg=FG_DIM, font=SMALL, width=14, anchor="w").pack(side="left")
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

        controls = tk.Frame(change_card, bg=SURFACE)
        controls.pack(fill="x", pady=(10, 0))
        self._generate_btn = tk.Button(
            controls,
            text="Generate Manifest",
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

        self._apply_btn = tk.Button(
            controls,
            text="Apply Manifest",
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
        self._apply_btn.pack(side="left", padx=(10, 0))

        promotion_card = self._card(
            wrap,
            "External Sync Planning",
            "Prepare a staged rollout plan for GitHub, Vercel, Supabase, Stripe, and Resend without pushing anything yet.",
        )

        promotion_summary = tk.Label(
            promotion_card,
            text=(
                "This step is planning-only. It inspects project signals and writes a reviewable plan for local compliance, \
pre-promotion checks, external sync prep, post-promotion checks, and rollback readiness. Nothing is pushed automatically."
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
            text="Generate Promotion Plan",
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

        helper = self._card(
            wrap,
            "Safety guardrails",
            "This guided workflow is intentionally conservative so users do not accidentally damage paths or break connections.",
        )
        tk.Label(
            helper,
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
        self.known_projects = {}
        values: list[str] = []
        registry_by_path: dict[str, dict] = {}

        try:
            proc = subprocess.run(
                ["python3", str(REGISTRY), "list"],
                capture_output=True,
                text=True,
                check=False,
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

        self.v_known_count.set(
            f"Found {governed_count} governed and {candidate_count} candidate projects across {CODE_ROOT}, {AGENTS_ROOT}, and {APPS_ROOT}"
        )
        self._known_project_combo.configure(values=values)
        self.after(0, self._refresh_window_anchor)
        if values and (not self.v_known_project.get() or self.v_known_project.get() not in self.known_projects):
            self.v_known_project.set(values[0])
            self._on_known_project_selected()
        else:
            self._update_change_summary()
        self.after(80, self._refresh_window_anchor)

    def _refresh_known_project_for_path(self, project_path: str):
        self._load_known_projects()
        match = next((label for label, item in self.known_projects.items() if item.get("path") == project_path), None)
        if match:
            self.v_known_project.set(match)
            self._on_known_project_selected()
        else:
            self.v_change_project.set(project_path)
            self._update_change_summary()
        self.after(0, self._refresh_window_anchor)

    def _on_known_project_selected(self):
        item = self.known_projects.get(self.v_known_project.get())
        if not item:
            self._update_change_summary()
            return
        self.v_change_project.set(item['path'])
        self._update_change_summary(item)

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

    def _browse_project(self):
        selected = filedialog.askdirectory(
            title="Select governed project",
            initialdir=str(Path(self.v_change_project.get()).expanduser().resolve().parent) if self.v_change_project.get() else str(Path.home() / "code"),
        )
        if selected:
            self.v_change_project.set(selected)
            self._update_change_summary()

    def _browse_manifest(self):
        selected = filedialog.askopenfilename(
            title="Select manifest",
            initialdir=str((GOVERNANCE_HOME / "data" / "new-build-agent" / "exports").resolve()),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_manifest.set(selected)

    def _browse_promotion_plan(self):
        selected = filedialog.askopenfilename(
            title="Select promotion plan",
            initialdir=str((GOVERNANCE_HOME / "data" / "new-build-agent" / "exports").resolve()),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if selected:
            self.v_promotion_plan.set(selected)

    def _set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        self._create_btn.config(state=state)
        self._generate_btn.config(state=state)
        self._apply_btn.config(state=state)
        self._promotion_btn.config(state=state)
        self._precheck_btn.config(state=state)

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
                        "python3",
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
                )
                self._out("Registered project in local inventory", "info")

            self.v_change_project.set(str(target_dir))
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
                ["python3", str(CHANGE_CONTROL), "propose", "--project", project],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Manifest generation failed.", "err")
                return
            manifest = proc.stdout.strip()
            self.v_manifest.set(manifest)
            self._out(f"Generated manifest: {manifest}", "ok")
            if Path(manifest).exists():
                manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
                self._update_change_summary(manifest=manifest_data)
                self._out(Path(manifest).read_text(encoding="utf-8").strip(), "dim")
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_apply_manifest(self):
        manifest = self.v_manifest.get().strip()
        if not manifest:
            messagebox.showerror("Required", "Generate or choose a manifest first.")
            return
        if not Path(manifest).exists():
            messagebox.showerror("Missing file", f"Manifest not found:\n{manifest}")
            return
        if not messagebox.askyesno(
            "Apply manifest",
            "This will create missing governed files listed in the manifest.\nContinue?",
        ):
            return
        self._set_busy(True)
        self._clear_output()
        threading.Thread(target=self._run_apply_manifest, args=(manifest,), daemon=True).start()

    def _run_apply_manifest(self, manifest: str):
        try:
            proc = subprocess.run(
                ["python3", str(CHANGE_CONTROL), "apply", "--manifest", manifest],
                capture_output=True,
                text=True,
                check=False,
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
                self.after(0, lambda p=project_path: self._refresh_known_project_for_path(p))
                self._update_change_summary(manifest=manifest_data)
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

    def _run_generate_promotion_plan(self, project: str):
        try:
            proc = subprocess.run(
                ["python3", str(PROMOTION_PLAN), "--project", project],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                self._out(proc.stdout.strip(), "dim")
                self._out(proc.stderr.strip() or "Promotion plan generation failed.", "err")
                return
            plan_path = proc.stdout.strip()
            self.v_promotion_plan.set(plan_path)
            self._out("Generated staged promotion plan with pre-checks, post-checks, and rollback readiness. External targets remain blocked until explicitly approved.", "ok")
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
                    "Promotion plan ready",
                    "A staged promotion plan was created.\n\nIt includes pre-promotion checks, post-promotion checks, and rollback readiness notes for GitHub, Vercel, Supabase, Stripe, and Resend. It will not push or deploy anything automatically.",
                ))
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _run_prechecks(self, plan_path: str):
        try:
            proc = subprocess.run(
                ["python3", str(PROMOTION_CHECKS), "--plan", plan_path, "--stage", "pre_promotion_checks"],
                capture_output=True,
                text=True,
                check=False,
            )
            report_path = proc.stdout.strip()
            if report_path:
                self._out(f"Pre-check report: {report_path}", "info")
            if report_path and Path(report_path).exists():
                report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
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
    App().mainloop()
