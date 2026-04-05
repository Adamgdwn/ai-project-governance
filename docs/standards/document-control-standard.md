# Document Control Standard

## Purpose

This standard defines how governed documents are named, versioned, reviewed, approved, and maintained.

## Principles

- Controlled documents must be easy to identify.
- Ownership and review responsibility must be explicit.
- Versions must be traceable.
- The process should add discipline without adding unnecessary friction.

## Document Classes

Use these default document classes:

- `POL`: policy
- `STD`: standard
- `PRC`: process
- `TPL`: template
- `CHK`: checklist
- `ADR`: architecture decision record
- `RUN`: runbook
- `GUI`: user guide or quick-start guide
- `REG`: register or log

## Document Identifier Format

Controlled documents should use this identifier format in the document header when practical:

`<CLASS>-<DOMAIN>-<NUMBER>`

Examples:

- `POL-ENG-001`
- `STD-ENG-001`
- `PRC-ENG-001`
- `GUI-ENG-001`

Notes:

- `DOMAIN` may remain `ENG` for this framework unless a wider taxonomy is adopted later.
- `NUMBER` should be a zero-padded sequence within the class and domain.

## Required Metadata

Controlled documents should include, either in a front-matter block or a short metadata section:

- document title
- document ID
- version
- status
- owner
- approver or approval role
- effective date
- last reviewed date
- next review date

## Status Values

Use these default statuses:

- `draft`
- `active`
- `superseded`
- `retired`

## Versioning Rules

Use semantic-style document versions:

- major version for material policy or control changes
- minor version for meaningful content additions or clarifications
- patch version for typo fixes or non-substantive edits

Examples:

- `1.0.0` initial approved issue
- `1.1.0` added a new required control
- `1.1.1` corrected wording only
- `2.0.0` materially changed the approval model

## File Naming Rules

File names should remain human-readable and stable.

- use `kebab-case`
- include the document purpose, not the control ID
- avoid version numbers in file names

Examples:

- `document-control-standard.md`
- `engineering-governance-policy.md`
- `project-intake-process.md`

## Review Cadence

Default review cadence:

- policy and standards: at least annually
- processes and guides: at least annually
- templates and checklists: when dependent controls change, and at least annually
- runbooks for live systems: at least every 6 months, or after incidents
- agent registers and tool permissions: after each material change and at least quarterly for high-risk systems

## Approval Expectations

Use this default approval model:

- policy and standards: project owner and technical lead
- process changes affecting production governance: project owner and technical lead
- templates and checklists: technical lead
- project-local controlled documents: project owner or delegate, with technical lead review where risk warrants

## Change Logging

Material changes to controlled documents should be recorded in one of:

- document revision history section
- changelog
- repository history with clear commit messages

Higher-risk governance documents should prefer an explicit revision history section.

## Superseded Documents

When a document is replaced:

- mark the old document as `superseded`
- reference the replacement document
- retain the prior document for traceability unless there is a compelling reason not to

## Recommended Metadata Block

```text
Document ID: STD-ENG-008
Version: 1.0.0
Status: active
Owner: Technical Lead
Approver: Project Owner
Effective Date: YYYY-MM-DD
Last Reviewed: YYYY-MM-DD
Next Review: YYYY-MM-DD
```

## Applicability

This standard applies strongly to governance documents and should be used selectively for project-local documents based on project risk and operational importance.

