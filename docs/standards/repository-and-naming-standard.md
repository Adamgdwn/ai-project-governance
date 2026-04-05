# Repository and Naming Standard

## Purpose

This standard defines naming conventions and repository structure expectations for consistency across project types.

## Naming Principles

- Names must be understandable, concise, and durable.
- Consistency is preferred, but naming may vary by artifact type when there is a good reason.
- Abbreviations should be avoided unless they are widely understood.

## Default Naming Conventions

### Repository Names

Use a type-appropriate convention:

- application and website repositories: `kebab-case`
- service and API repositories: `kebab-case`
- infrastructure repositories: `kebab-case`
- documentation repositories: `kebab-case`
- script files: `snake_case` or `kebab-case`, chosen once per repository
- environment variables: `UPPER_SNAKE_CASE`
- code symbols: follow language conventions

Examples:

- `customer-portal`
- `billing-api`
- `marketing-site`
- `ops-automation`

### AI Agent Naming

Use human-readable role-oriented names in documentation, and stable machine-safe identifiers in code and config.

Examples:

- display name: `Deployment Governance Agent`
- identifier: `deployment-governance-agent`

## Required Top-Level Repository Structure

Every repository should include, where applicable:

- `README.md`
- `.gitignore`
- `docs/`
- `tests/` or type-appropriate test location
- `scripts/` for operational or helper scripts
- `.github/` or equivalent CI folder when automation exists

Each project must also contain or generate:

- `project-control.yaml`
- deployment and runbook documentation if deployable

## Preferred Common Layout

Use one common layout unless the technology stack strongly suggests otherwise.

Example:

```text
repo-name/
  README.md
  project-control.yaml
  docs/
    architecture.md
    deployment-guide.md
    runbook.md
    adr/
    risks/
  src/
  tests/
  scripts/
  .github/
```

## Permitted Deviations

Deviation from the preferred structure is acceptable when:

- the framework or platform has a dominant convention
- the repository is a monorepo
- the project type is documentation-only
- generated structure is imposed by a trusted vendor tool

Any significant deviation should be documented.

## Monorepo Handling

Monorepos are supported when:

- the root defines shared governance controls
- each governed application or service has local ownership and documentation
- release boundaries are clear
- secrets and deployments are scoped to the correct subproject

See the monorepo standard for details.

