# Current Build Pathway

Last Updated: 2026-05-31
Status: active
Owner: Technical Lead

## Purpose

This document is the live path from current plan to completed build. It keeps agent work small, timestamped, and easy to resume.

## Required Work Pattern

For each substantial work session:

1. Start from `START_HERE.md`.
2. Run the governance preflight for the target project.
3. Review `docs/standards/engineering-governance-by-use-case.md`.
4. Review `docs/policy/durable-development-engineering-policy.md`.
5. Review `project-control.yaml` and open exceptions.
6. Capture a timestamp with `date -Iseconds`.
7. Define the next build chunk in this document.
8. Complete and validate that chunk before expanding scope.
9. Update this document with status, validation, and the next chunk.

## Chunking Standard

Each build chunk should be small enough to fit comfortably in an agent context window.

A good chunk has:

- one objective
- clear input files or documents
- clear output files or behavior
- explicit validation steps
- a timestamped status note

Avoid mixing unrelated code, governance, deployment, and product decisions in one chunk unless the change cannot be validated any other way.

## Active Path

| Step | Status | Timestamp | Owner | Notes |
|------|--------|-----------|-------|-------|
| Add start/pathway governance baseline | complete | 2026-05-27T08:59:36-06:00 | Codex session | Added `START_HERE.md`, `docs/current-build-pathway.md`, timestamp rules, and context-friendly chunk guidance to scaffold and checks. |
| Validate governance framework | complete | 2026-05-27T08:59:36-06:00 | Codex session | Repo governance, shell syntax, Python syntax, fresh scaffold, and safe upgrade checks passed. |
| Handoff existing-build upgrade path | complete | 2026-05-27T08:59:36-06:00 | Codex session | Existing builds can receive missing files through `automation/change_control.py` copy-if-missing manifests. |
| Add managed instruction upgrades | complete | 2026-05-27T10:35:37-06:00 | Codex session | Extended compliance manifests so existing `AGENTS.md`, `AI_BOOTSTRAP.md`, and `CLAUDE.md` can receive append-only managed guidance when missing. |
| Improve GUI pathway experience | complete | 2026-05-27T11:25:51-06:00 | Codex session | Refreshed the desktop UI palette, clarified the governance/release pathway, added scrollable tab content, and removed prototype-like visual language. |
| Add durable development engineering policy | complete | 2026-05-31T10:34:56-06:00 | Codex session | Folded the downloaded engineering policy into governed docs, scaffolds, checks, and upgrade manifests. |
| Risk-scale durable development policy | complete | 2026-05-31T10:37:24-06:00 | Codex session | Reviewed the durable policy against existing governance standards and clarified that controls scale by `risk_tier`, `governance_level`, and active build pathway. |
| Add use-case engineering governance | complete | 2026-05-31T10:49:31-06:00 | Codex session | Added use-case governance standard, scaffold/check/upgrade wiring, and explicit guardrails that use-case guidance does not override selected `risk_tier` or `governance_level`. |
| Audit build against engineering standards | complete | 2026-05-31T10:56:25-06:00 | Codex session | Added `docs/repository-audit-2026-05-31.md` with standards findings, validation evidence, and remediation order. |
| Remediate standards audit findings | complete | 2026-05-31T11:13:32-06:00 | Codex session | Filled operating records, added validation/tests/CI, removed headless provider credential passthrough, required explicit Git staging, and expanded generated promotion checks. |
| Add existing-repo upgrade safety rule | complete | 2026-05-31T11:35:07-06:00 | Codex session | Documented manifest review, non-jeopardy checks, post-apply governance validation, idempotency proposal, and git status verification for existing repo upgrades. |
| Add portable document control standard | complete | 2026-05-31T18:24:39-06:00 | Codex session | Expanded `docs/standards/document-control-standard.md` into a self-contained standard another repo can adopt by reference, including Markdown hierarchy, metadata, timestamp, pathway, handoff, audit, register, runbook, and ADR patterns. |
| Add schema validation for governed plans | complete | 2026-05-31T19:33:24-06:00 | Codex session | Added dependency-free schema validation for `project-control.yaml` and generated promotion plans; wired it into plan generation, check execution, local validation, tests, and automation docs. |
| Add guided desktop workflows | complete | 2026-05-31T19:49:18-06:00 | Codex session | Reshaped the GUI into three calmer workflows: new build, governance and release, and document-control update for existing repos. Added preview-first document-control manifests that sync only `docs/standards/document-control-standard.md`. |
| Redesign intake for non-technical users | complete | 2026-05-31T20:24:00-06:00 | Codex session | Replaced the New Build form with a research-informed guided intake: one decision at a time, plain-language options, inferred technical settings, review screen, and advanced controls. |
| Plan Windows clone/update support | complete | 2026-06-01T10:59:05-06:00 | Codex session | Added the permanent Windows and version-update roadmap to `docs/user-guide.md`. First execution chunk is Windows bootstrap and validation; later chunks add version source of truth, update checks, guarded self-update, and GUI update affordances. |
| Chunk 1 Windows-first launch support | complete | 2026-06-01T11:07:02-06:00 | Codex session | Added cross-platform Python scaffolding, PowerShell new-build/GUI/validation launchers, Windows CI validation, Windows setup docs, and tests for Bash-free scaffolding. Existing `project-control.yaml` files are preserved during bootstrap. |
| Rename product and repository identity | complete | 2026-06-01T11:24:03-06:00 | Codex session | Renamed tracked product, repo slug, runtime artifact paths, launcher labels, docs, inventory IDs, and filename references to New Build Governance Agent. GitHub repository rename is handled as the final external publish step. |
| Chunk 2 version source of truth | complete | 2026-06-01T11:36:57-06:00 | Codex session | Added `VERSION` as the version source of truth, `automation/version.py`, command-line version reporting, GUI version display, release/version documentation, and a timestamped chunk ledger in `docs/user-guide.md`. |
| Chunk 3 read-only update checks | complete | 2026-06-01T12:00:28-06:00 | Codex session | Added `automation/update_check.py` and launcher flags for read-only GitHub release/tag comparison. Reports `current`, `behind`, `ahead`, or `unable_to_check`; no update action is performed. |
| Chunk 4 guarded self-update | complete | 2026-06-01T12:17:12-06:00 | Codex session | Added `automation/self_update.py` and launcher flags for guarded fast-forward updates. The command refuses dirty, detached, missing-upstream, ahead, and diverged checkouts and never resets, stashes, rebases, force-pulls, or changes branches. |
| Chunk 5 Windows validation hardening | complete | 2026-06-01T12:38:41-06:00 | Codex session | Expanded `scripts/validate.ps1` with agent-specific required-file checks, `scripts` directory validation, and deterministic Windows smoke tests for version, headless version, PowerShell launcher version, update-check JSON, and self-update failure reporting. |

## Timestamp Rule

Use ISO-style timestamps for work notes, handoffs, decisions, exceptions, release notes, and validation records. Prefer the local command:

```bash
date -Iseconds
```

## Validation Log

| Timestamp | Command | Result | Notes |
|-----------|---------|--------|-------|
| 2026-05-27T08:59:36-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| 2026-05-27T08:59:36-06:00 | `bash -n ...` | pass | Shell syntax passed for scaffold, governance, launcher, and template scripts. |
| 2026-05-27T08:59:36-06:00 | `python3 -m py_compile ...` | pass | Python syntax passed for changed automation entry points. |
| 2026-05-27T08:59:36-06:00 | temporary scaffold and preflight | pass | Fresh application scaffold included the new baseline files and passed preflight. |
| 2026-05-27T08:59:36-06:00 | temporary change-control propose/apply | pass | Existing file was preserved; missing start/pathway files were created through manifest apply. |
| 2026-05-27T10:35:37-06:00 | `python3 -m py_compile automation/change_control.py automation/new_build_gui.py` | pass | Python syntax passed after managed instruction changes. |
| 2026-05-27T10:35:37-06:00 | fresh scaffold compliance proposal | pass | Freshly scaffolded project had no compliance drift. |
| 2026-05-27T10:35:37-06:00 | managed instruction upgrade validation | pass | Existing instruction files were preserved, managed blocks were appended once, and a second proposal produced no repeat append actions. |
| 2026-05-27T10:35:37-06:00 | minimal project compliance apply | pass | Minimal existing project received baseline instruction and pathway files. |
| 2026-05-27T10:35:37-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| 2026-05-27T11:25:51-06:00 | `python3 -m py_compile automation/new_build_gui.py automation/change_control.py` | pass | GUI and compliance engine syntax passed. |
| 2026-05-27T11:25:51-06:00 | shell syntax validation | pass | New build and governance shell scripts passed `bash -n`. |
| 2026-05-27T11:25:51-06:00 | GUI language and color scan | pass | Old blue/purple/prototype markers were removed from the GUI and launcher icon. |
| 2026-05-27T11:25:51-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| 2026-05-31T10:34:56-06:00 | `python3 -m py_compile automation/change_control.py automation/new_build_gui.py automation/new_build_headless.py automation/project_registry.py` | pass | Python syntax passed after durable engineering policy integration. |
| 2026-05-31T10:34:56-06:00 | `bash -n ...` | pass | Shell syntax passed for bootstrap, required-file checks, governance checks, new-build launcher, and scaffold scripts. |
| 2026-05-31T10:34:56-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | Durable engineering policy is now required and present; 0 warnings. |
| 2026-05-31T10:34:56-06:00 | temporary fresh scaffold and preflight | pass | Fresh application scaffold created `docs/policy/durable-development-engineering-policy.md` and passed preflight. |
| 2026-05-31T10:34:56-06:00 | temporary change-control propose/apply/idempotency check | pass | Existing project received the policy file and managed instruction guidance; second proposal had no remaining actions. |
| 2026-05-31T10:34:56-06:00 | `bash automation/check_required_files.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | Minimal required-file check now includes the durable engineering policy. |
| 2026-05-31T10:37:24-06:00 | durable policy rigidity review | pass | Policy now explicitly allows lightweight notes/manual validation for low-risk work and stronger evidence for high/critical work. |
| 2026-05-31T10:37:24-06:00 | `python3 -m py_compile automation/change_control.py automation/new_build_gui.py automation/new_build_headless.py automation/project_registry.py` | pass | Python syntax still passes after policy wording changes. |
| 2026-05-31T10:37:24-06:00 | `bash -n ...` | pass | Shell syntax still passes. |
| 2026-05-31T10:37:24-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings. |
| 2026-05-31T10:49:31-06:00 | `python3 -m py_compile automation/change_control.py automation/new_build_gui.py automation/new_build_headless.py automation/project_registry.py` | pass | Python syntax passed after use-case governance integration. |
| 2026-05-31T10:49:31-06:00 | `bash -n ...` | pass | Shell syntax passed after use-case governance integration. |
| 2026-05-31T10:49:31-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | Use-case standard is now required and present; 0 warnings. |
| 2026-05-31T10:49:31-06:00 | temporary website scaffold at governance level 1 | pass | Scaffold preserved selected `risk_tier: low` and `governance_level: 1` while adding `use_case.primary`. |
| 2026-05-31T10:49:31-06:00 | temporary change-control propose/apply/idempotency check | pass | Existing project received use-case standard and managed guidance; second proposal had no remaining actions. |
| 2026-05-31T10:49:31-06:00 | `bash automation/check_required_files.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | Minimal required-file check now includes use-case governance standard. |
| 2026-05-31T10:56:25-06:00 | full standards audit | complete | Created `docs/repository-audit-2026-05-31.md`; primary findings are placeholder control docs and declared enforcement gaps. |
| 2026-05-31T10:56:25-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings after audit report creation. |
| 2026-05-31T10:56:25-06:00 | `python3 -m py_compile $(find automation -maxdepth 1 -name '*.py' -print)` | pass | Python syntax passed after audit report creation. |
| 2026-05-31T11:13:32-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, Python compile, shell syntax, unittest, and secret-hygiene checks passed. |
| 2026-05-31T11:13:32-06:00 | generated promotion plan and `python3 automation/promotion_checks.py --plan <plan> --stage pre_promotion_checks` | pass | Generated pre-checks included governance preflight, Python compile, shell syntax, and unittest. |
| 2026-05-31T11:35:07-06:00 | existing-repo upgrade safety documentation review | complete | Added explicit pre-apply and post-apply verification instructions to user-facing docs. |
| 2026-05-31T18:26:01-06:00 | `bash automation/governance_check.sh /home/adamgoodwin/code/agents/New\ Build\ Agent` | pass | 0 warnings after document control standard expansion. |
| 2026-05-31T18:26:01-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, Python compile, shell syntax, unittest, and secret-hygiene checks passed. |
| 2026-05-31T19:33:24-06:00 | `python3 -m py_compile automation/schema_validation.py automation/promotion_plan.py automation/promotion_checks.py` | pass | Schema validator and promotion integrations compile. |
| 2026-05-31T19:33:24-06:00 | `python3 -m unittest tests.test_schema_validation tests.test_promotion_plan` | pass | Focused schema and promotion-plan tests passed. |
| 2026-05-31T19:33:24-06:00 | `python3 automation/schema_validation.py --promotion-plan /tmp/new-build-governance-agent-promotion-schema-test.json` | pass | Generated promotion plan satisfied the schema. |
| 2026-05-31T19:33:24-06:00 | `python3 automation/promotion_checks.py --plan /tmp/new-build-governance-agent-promotion-schema-test.json --stage pre_promotion_checks --output /tmp/new-build-governance-agent-check-report-schema-test.json` | pass | Schema validation ran before checks; pre-promotion checks passed. |
| 2026-05-31T19:33:24-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed. |
| 2026-05-31T19:49:18-06:00 | `python3 -m py_compile automation/change_control.py automation/new_build_gui.py` | pass | GUI and document-control manifest command compile. |
| 2026-05-31T19:49:18-06:00 | `python3 -m unittest tests.test_change_control` | pass | Existing governance manifest behavior and document-control sync manifest passed. |
| 2026-05-31T19:49:18-06:00 | `python3 automation/change_control.py propose-document-control --project /tmp --output /tmp/doc-control-test-manifest.json` | pass | Generated a document-control-only sync manifest. |
| 2026-05-31T19:49:18-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed. |
| 2026-05-31T19:49:18-06:00 | Tk startup smoke test | pass | Instantiated `automation/new_build_gui.py` App, ran `update_idletasks`, and destroyed the window successfully. |
| 2026-05-31T20:24:00-06:00 | `python3 -m py_compile automation/new_build_gui.py` | pass | Guided intake GUI compiles. |
| 2026-05-31T20:24:00-06:00 | Tk guided intake smoke test | pass | Instantiated the GUI, filled a sample non-technical intake, verified inferred setup, and destroyed the window successfully. |
| 2026-05-31T20:24:00-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed. |
| 2026-06-01T10:59:05-06:00 | `bash scripts/validate.sh` | pass | Documentation-only Windows/update roadmap change passed governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks. |
| 2026-06-01T11:07:02-06:00 | `python3 -m unittest tests.test_scaffold_project` | pass | Cross-platform scaffolding creates agent baseline, preserves existing files, and does not reclassify existing `project-control.yaml`. |
| 2026-06-01T11:07:02-06:00 | Python and Bash scaffold smoke test | pass | Fresh project created through `automation/scaffold_project.py` and through `automation/bootstrap_project.sh`; both passed `automation/governance_check.sh`. |
| 2026-06-01T11:07:02-06:00 | Headless launcher smoke test | pass | `automation/new_build_headless.py` created a fresh project using the Python scaffolder with `HOME` isolated to a temporary directory; generated project passed governance check. |
| 2026-06-01T11:07:02-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed. PowerShell syntax check was skipped locally because `pwsh` is not installed; Windows CI now runs `scripts/validate.ps1`. |
| 2026-06-01T11:07:02-06:00 | `git diff --check` | pass | No whitespace errors. |
| 2026-06-01T11:24:03-06:00 | tracked naming scan | pass | `git grep` found no remaining tracked legacy product-name, repo-slug, runtime-slug, or inventory-prefix references. |
| 2026-06-01T11:24:03-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed after rename. PowerShell syntax check was skipped locally because `pwsh` is not installed. |
| 2026-06-01T11:24:03-06:00 | `git diff --check` | pass | No whitespace errors after rename. |
| 2026-06-01T11:24:03-06:00 | GitHub Actions follow-up | fixed | Ubuntu CI exposed cross-platform differences when parsing PowerShell from Bash. `scripts/validate.sh` now delegates PowerShell syntax validation to `scripts/validate.ps1` in the Windows CI job. |
| 2026-06-01T11:36:57-06:00 | version command checks | pass | `automation/version.py`, `automation/new_build.sh --version`, `automation/new_build_headless.py --version`, and `automation/scaffold_project.py --version` reported `0.3.0`. |
| 2026-06-01T11:36:57-06:00 | `python3 -m unittest tests.test_version` | pass | Version file, helper output, CLI JSON, headless version flag, and `freedom.tool.yaml` alignment passed. |
| 2026-06-01T11:36:57-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed with 19 tests. |
| 2026-06-01T11:36:57-06:00 | `git diff --check` | pass | No whitespace errors after Chunk 2. |
| 2026-06-01T11:58:51-06:00 | `python3 -m unittest tests.test_update_check tests.test_version` | pass | Update-check comparison tests covered current, behind, ahead, and unable states; version tests still passed. |
| 2026-06-01T11:58:51-06:00 | `python3 automation/update_check.py --json` | pass | Live GitHub check returned `unable_to_check` because no semantic version release/tag exists yet; command remained read-only and exited successfully. |
| 2026-06-01T12:00:28-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed with 23 tests. |
| 2026-06-01T12:00:28-06:00 | `git diff --check` | pass | No whitespace errors after Chunk 3. |
| 2026-06-01T12:00:28-06:00 | launcher update-check commands | pass | `bash automation/new_build.sh --check-updates` and `python3 automation/new_build_headless.py --check-updates` reported `unable_to_check` without modifying the repo. |
| 2026-06-01T12:17:12-06:00 | `python3 -m unittest tests.test_self_update` | pass | Temporary Git remote/clone tests covered fast-forward update, dry-run, dirty refusal, local-ahead refusal, and up-to-date behavior. |
| 2026-06-01T12:17:59-06:00 | `bash scripts/validate.sh` | pass | Governance, required-file, project-control schema, Python compile, shell syntax, unittest, and secret-hygiene checks passed with 28 tests. |
| 2026-06-01T12:17:59-06:00 | `git diff --check` | pass | No whitespace errors after Chunk 4. |
| 2026-06-01T12:17:59-06:00 | `python3 automation/self_update.py --dry-run --json` | pass | Current checkout correctly refused self-update while Chunk 4 files were uncommitted, proving dirty-worktree protection on the real repo. |
| 2026-06-01T12:38:41-06:00 | `bash scripts/validate.sh` | pass | Linux validation still passes after Windows validator hardening; PowerShell validation is delegated to Windows CI. |
| 2026-06-01T12:38:41-06:00 | `git diff --check` | pass | No whitespace errors after Chunk 5. |
| 2026-06-01T12:39:32-06:00 | update/self-update smoke commands | pass | Local equivalents of the new Windows smoke checks returned valid update-check JSON and expected self-update missing-repo failure JSON. |
| 2026-06-01T12:41:31-06:00 | Windows CI follow-up | fixed | Windows reported missing/non-directory self-update paths as `NotADirectoryError`; `automation/self_update.py` now handles `OSError` and `tests.test_self_update` covers file-path repo failures. Local validation passed with 29 tests. |
| 2026-06-01T12:43:10-06:00 | Windows CI follow-up | fixed | Windows validation checks passed but PowerShell preserved the intentional self-update smoke-test exit code. `scripts/validate.ps1` now exits `0` after successful validation. |

## Next Handoff

Next agent should begin at `START_HERE.md`. Chunk 5 is complete. The active next chunk is Chunk 6: GUI update affordances. Add update-check controls and offer update actions only when repo state is safe.
