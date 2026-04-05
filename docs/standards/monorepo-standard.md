# Monorepo Standard

## Purpose

This standard explains how to apply the governance framework in a monorepo without losing clarity.

## Root Requirements

The monorepo root should include:

- root `README.md`
- root `project-control.yaml`
- shared standards or conventions
- CI and enforcement configuration
- ownership boundaries

## Subproject Requirements

Each independently deployable or governed subproject should include:

- local `README.md`
- local documentation as needed
- explicit owner
- risk classification
- release boundary

## Preferred Structure

```text
monorepo/
  README.md
  project-control.yaml
  apps/
    customer-portal/
    marketing-site/
  services/
    billing-api/
  agents/
    deployment-governance-agent/
  packages/
  docs/
```

## Control Rules

- Shared controls may be centralized.
- Risk and release decisions must remain traceable per governed subproject.
- A high-risk subproject may require stronger controls than the rest of the monorepo.

