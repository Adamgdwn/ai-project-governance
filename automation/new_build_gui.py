#!/usr/bin/env python3
"""
New Build Agent — GUI
Pop!_OS build machine project launcher.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import re
from datetime import date
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────

GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
BOOTSTRAP       = GOVERNANCE_HOME / "automation" / "bootstrap_project.sh"
AGENTS_ROOT     = Path.home() / "code" / "agents"
APPS_ROOT       = Path.home() / "code" / "Applications"

# ── theme ─────────────────────────────────────────────────────────────────────

BG       = "#1b1b2f"
SURFACE  = "#24243e"
BORDER   = "#3a3a5c"
FG       = "#dde1f5"
FG_DIM   = "#8888aa"
ACCENT   = "#ffa348"
ENTRY_BG = "#1e1e38"
SUCCESS  = "#a6e3a1"
ERROR    = "#f38ba8"

FONT  = ("Sans", 10)
SMALL = ("Sans", 9)
MONO  = ("Monospace", 9)
PAD   = 14

# ── type / risk maps ──────────────────────────────────────────────────────────

TYPE_MAP = {
    "app":   ("application",   APPS_ROOT),
    "agent": ("agent",         AGENTS_ROOT),
    "tool":  ("internal-tool", APPS_ROOT),
    "other": ("automation",    APPS_ROOT),
}

RISK_MAP = {"normal": "medium", "heavy": "high"}

# ── helpers ───────────────────────────────────────────────────────────────────

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


# ── app ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("New Build Agent")
        self.configure(bg=BG)
        self.geometry("540x760")
        self.minsize(520, 600)
        self.resizable(True, True)

        self.v_name    = tk.StringVar()
        self.v_type    = tk.StringVar(value="app")
        self.v_stack   = tk.StringVar()
        self.v_builder = tk.StringVar(value="claude")
        self.v_risk    = tk.StringVar(value="normal")
        self.v_scope   = tk.BooleanVar(value=False)
        self.v_problem = tk.StringVar()
        self.v_user    = tk.StringVar()
        self.v_mvp     = tk.StringVar()

        self.v_name.trace_add("write", lambda *_: self._refresh_preview())
        self.v_type.trace_add("write", lambda *_: self._refresh_preview())

        self._setup_style()
        self._build_ui()
        self._refresh_preview()

    # ── style ─────────────────────────────────────────────────────────────────

    def _setup_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TCombobox",
            fieldbackground=ENTRY_BG, background=SURFACE,
            foreground=FG, selectbackground=SURFACE,
            selectforeground=FG, bordercolor=BORDER,
            arrowcolor=FG_DIM, insertcolor=FG,
            lightcolor=BORDER, darkcolor=BORDER)
        s.map("TCombobox",
            fieldbackground=[("readonly", ENTRY_BG)],
            foreground=[("readonly", FG)])

    # ── layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="New Build Agent",
                 bg=SURFACE, fg=ACCENT,
                 font=("Sans", 15, "bold")).pack()
        tk.Label(hdr, text="Scope  ·  Classify  ·  Scaffold",
                 bg=SURFACE, fg=FG_DIM, font=SMALL).pack()

        # Form sections
        self._section("PROJECT")
        self._project_rows()

        self._section("CONFIGURATION")
        self._config_rows()

        self._section("SCOPE BRIEF")
        self._scope_section()

        # Create button
        btn_wrap = tk.Frame(self, bg=BG)
        btn_wrap.pack(fill="x", padx=PAD, pady=(18, 6))
        self._btn = tk.Button(
            btn_wrap, text="Create Project",
            bg=ACCENT, fg="#1b1b2f",
            font=("Sans", 11, "bold"),
            relief="flat", bd=0,
            padx=28, pady=10,
            cursor="hand2",
            activebackground="#cc8230",
            activeforeground="#1b1b2f",
            command=self._on_create)
        self._btn.pack()

        # Output
        self._section("OUTPUT")
        self._output = tk.Text(
            self, bg=SURFACE, fg=FG, font=MONO,
            relief="flat", bd=0,
            state="disabled", height=10,
            wrap="char",
            highlightthickness=1,
            highlightbackground=BORDER)
        self._output.pack(fill="both", expand=True,
                          padx=PAD, pady=(0, PAD))
        self._output.tag_configure("ok",  foreground=SUCCESS)
        self._output.tag_configure("err", foreground=ERROR)
        self._output.tag_configure("dim", foreground=FG_DIM)

    def _section(self, title: str):
        f = tk.Frame(self, bg=BG)
        f.pack(fill="x", padx=PAD, pady=(14, 4))
        tk.Label(f, text=title, bg=BG, fg=FG_DIM,
                 font=("Sans", 8, "bold")).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True,
            padx=(8, 0), pady=5)

    def _row(self, label: str, make_widget):
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=PAD, pady=3)
        tk.Label(row, text=label, bg=BG, fg=FG_DIM,
                 font=SMALL, width=14, anchor="w").pack(side="left")
        make_widget(row).pack(side="left", fill="x", expand=True)

    def _entry(self, parent, var):
        return tk.Entry(
            parent, textvariable=var,
            bg=ENTRY_BG, fg=FG,
            insertbackground=FG,
            relief="flat", font=FONT, bd=6,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT)

    def _combo(self, parent, var, values):
        return ttk.Combobox(
            parent, textvariable=var,
            values=values, state="readonly",
            font=FONT, width=20)

    # ── sections ──────────────────────────────────────────────────────────────

    def _project_rows(self):
        self._row("Name", lambda p: self._entry(p, self.v_name))
        # Path preview (read-only label beneath name)
        prev = tk.Frame(self, bg=BG)
        prev.pack(fill="x", padx=PAD, pady=(0, 2))
        tk.Label(prev, text="", bg=BG, fg=FG_DIM,
                 font=SMALL, width=14).pack(side="left")
        self._lbl_preview = tk.Label(
            prev, text="", bg=BG, fg=FG_DIM,
            font=MONO, anchor="w", justify="left")
        self._lbl_preview.pack(side="left", fill="x", expand=True)

    def _config_rows(self):
        self._row("Type",    lambda p: self._combo(p, self.v_type,
            ["app", "agent", "tool", "other"]))
        self._row("Stack",   lambda p: self._entry(p, self.v_stack))
        self._row("Builder", lambda p: self._combo(p, self.v_builder,
            ["claude", "codex", "local", "hybrid"]))
        self._row("Risk",    lambda p: self._combo(p, self.v_risk,
            ["normal", "heavy"]))

    def _scope_section(self):
        chk_row = tk.Frame(self, bg=BG)
        chk_row.pack(fill="x", padx=PAD, pady=(0, 4))
        tk.Checkbutton(
            chk_row,
            text="Include scope brief now",
            variable=self.v_scope,
            bg=BG, fg=FG,
            selectcolor=SURFACE,
            activebackground=BG,
            activeforeground=FG,
            font=SMALL,
            command=self._toggle_scope,
        ).pack(side="left")

        # Rows created once, shown/hidden on toggle
        def scoped(parent, var):
            return self._entry(parent, var)

        def make_row(label, var):
            row = tk.Frame(self, bg=BG)
            tk.Label(row, text=label, bg=BG, fg=FG_DIM,
                     font=SMALL, width=14, anchor="w").pack(
                         side="left", padx=(PAD, 0))
            self._entry(row, var).pack(
                side="left", fill="x", expand=True,
                padx=(0, PAD))
            return row

        self._sr = [
            make_row("Problem",         self.v_problem),
            make_row("User / consumer", self.v_user),
            make_row("MVP",             self.v_mvp),
        ]
        # Hidden initially
        for r in self._sr:
            r.pack_forget()

    def _toggle_scope(self):
        if self.v_scope.get():
            for r in self._sr:
                r.pack(fill="x", pady=3)
        else:
            for r in self._sr:
                r.pack_forget()

    # ── preview ───────────────────────────────────────────────────────────────

    def _refresh_preview(self):
        name = self.v_name.get().strip()
        if not name:
            self._lbl_preview.config(text="")
            return
        _, root = TYPE_MAP.get(self.v_type.get(), ("application", APPS_ROOT))
        self._lbl_preview.config(text=str(root / slugify(name)))

    # ── create ────────────────────────────────────────────────────────────────

    def _on_create(self):
        name = self.v_name.get().strip()
        if not name:
            messagebox.showerror("Required", "Project name cannot be empty.")
            return

        gov_type, root = TYPE_MAP.get(self.v_type.get(), ("application", APPS_ROOT))
        slug        = slugify(name)
        target_dir  = root / slug
        risk_tier   = RISK_MAP.get(self.v_risk.get(), "medium")
        builder     = self.v_builder.get()
        stack       = self.v_stack.get().strip() or "not specified"

        data = dict(name=name, slug=slug, gov_type=gov_type,
                    risk_tier=risk_tier, stack=stack,
                    builder=builder, target_dir=str(target_dir))

        if self.v_scope.get():
            data.update(
                problem=self.v_problem.get().strip(),
                user_desc=self.v_user.get().strip(),
                mvp=self.v_mvp.get().strip())

        if target_dir.exists():
            if not messagebox.askyesno(
                "Directory exists",
                f"{target_dir}\nalready exists. "
                "Existing files will not be overwritten.\nContinue?"
            ):
                return

        self._btn.config(state="disabled")
        self._clear_output()
        threading.Thread(
            target=self._run,
            args=(target_dir, gov_type, risk_tier, builder, data),
            daemon=True
        ).start()

    def _run(self, target_dir, gov_type, risk_tier, builder, data):
        try:
            proc = subprocess.Popen(
                ["bash", str(BOOTSTRAP), str(target_dir), gov_type, risk_tier],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True)
            for line in proc.stdout:
                self._out(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                self._out("Bootstrap failed.", "err")
                return

            for d in ["docs/adr", "docs/specs", "docs/runbooks", "archive"]:
                (target_dir / d).mkdir(parents=True, exist_ok=True)
            self._out("Created: docs/adr  docs/specs  docs/runbooks  archive")

            pc = target_dir / "project-control.yaml"
            if pc.exists():
                txt = pc.read_text()
                txt = txt.replace("name: Project Owner",  "name: Adam Goodwin")
                txt = txt.replace("name: Technical Lead", f"name: {builder} session")
                pc.write_text(txt)

            write_initial_scope(target_dir, data)
            self._out("Created: INITIAL_SCOPE.md")
            self._out(f"\n✓  {target_dir}", "ok")

        except Exception as e:
            self._out(f"Error: {e}", "err")
        finally:
            self.after(0, lambda: self._btn.config(state="normal"))

    # ── output helpers ────────────────────────────────────────────────────────

    def _clear_output(self):
        self._output.config(state="normal")
        self._output.delete("1.0", "end")
        self._output.config(state="disabled")

    def _out(self, text: str, tag: str = ""):
        def _do():
            self._output.config(state="normal")
            self._output.insert("end", text + "\n", tag)
            self._output.see("end")
            self._output.config(state="disabled")
        self.after(0, _do)


if __name__ == "__main__":
    App().mainloop()
