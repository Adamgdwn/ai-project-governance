# AI Agent Governance Standard

## Purpose

This standard defines additional controls required for AI agents and agentic systems.

## Principles

- Agents must be governable, observable, and constrainable.
- Autonomy must be matched to risk.
- Prompt, model, and tool changes must be traceable.

## Required Agent Records

Every governed agent project must maintain:

- agent inventory
- model registry
- prompt or instruction register
- tool permission matrix
- evaluation set or evaluation approach
- human oversight rules
- rollback or disable procedure

## Required Design Decisions

Each agent must document:

- intended purpose
- disallowed actions
- approved tool classes
- maximum autonomy level
- escalation path for ambiguous or risky situations

## Autonomy Levels

Suggested default model:

- `A0`: advisory only, no actions
- `A1`: proposes actions for approval
- `A2`: performs bounded actions with logging
- `A3`: performs broader actions with strong guardrails and review

Higher autonomy requires stronger controls, especially at high or critical risk.

## Tool Governance

For each tool or integration, document:

- tool name
- purpose
- allowed operations
- prohibited operations
- approval requirements
- failure behavior

## Evaluation Expectations

Agents must be evaluated for:

- instruction adherence
- unsafe action resistance
- tool-use correctness
- escalation behavior
- regression after meaningful changes

## Change Control

Material changes include:

- model change
- prompt or policy change
- tool access change
- autonomy increase
- deployment target change

Material changes require documented review and re-evaluation.

