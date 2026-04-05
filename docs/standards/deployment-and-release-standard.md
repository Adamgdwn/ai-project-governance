# Deployment and Release Standard

## Purpose

This standard defines deployment expectations for systems that can be released or operated.

## Principles

- Releases must be intentional, reproducible, and reversible.
- Higher-risk systems require stronger checks and clearer approvals.
- Environment drift should be minimized.

## Default Environment Model

Deployable projects should define, at minimum:

- `dev`
- `staging` or equivalent validation environment
- `prod`

Deviations are allowed for low-risk or non-deployable projects when documented.

## Required Release Controls

All deployable projects must define:

- release owner
- release process
- rollback path
- environment configuration model
- post-deployment validation steps

## Risk-Scaled Release Expectations

### Low

- documented deploy steps
- basic smoke check

### Medium

- repeatable deployment workflow
- staging validation
- release checklist

### High

- approval before production deployment
- rollback instructions
- operational runbook
- release evidence retained in CI or deployment tooling

### Critical

- dual approval by project owner and technical lead
- stronger change visibility
- incident communication path
- recovery expectations documented

## Release History

Each project must retain a release history through one or more of:

- changelog
- tags and release notes
- CI deployment records

