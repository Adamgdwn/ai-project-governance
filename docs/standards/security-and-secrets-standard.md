# Security and Secrets Standard

## Purpose

This standard defines baseline controls for secrets, sensitive data, and secure delivery.

## Principles

- Sensitive access must be intentional, minimal, and reviewable.
- Secrets must never be embedded in source control.
- Data handling controls must scale with sensitivity and risk.

## Required Controls

Every project must address:

- secret storage and rotation method
- environment segregation
- least-privilege access
- dependency management
- logging and sensitive data exposure rules
- backup and recovery expectations where applicable

## Secrets Rules

- Secrets must be stored in approved secret managers or protected environment systems.
- Example placeholder files such as `.env.example` may be committed, but not real secret values.
- Production credentials must not be shared through chat, code comments, or untracked local files intended for long-term use.

## Sensitive Data Rules

Projects that handle money, personal data, or privileged business data must define:

- data categories handled
- where data is stored
- retention expectations
- masking or redaction needs
- access boundaries

## Secure Delivery Expectations

At medium risk and above, projects should include:

- secret scanning
- dependency vulnerability review
- access review for deployment credentials

At high risk and above, projects should also include:

- explicit security review during project setup
- documented incident response contact or owner

At critical risk, projects should also include:

- stronger approval controls for privileged changes
- periodic review of permissions and integrations

