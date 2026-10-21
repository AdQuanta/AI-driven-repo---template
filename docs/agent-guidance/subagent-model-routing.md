# Subagent Model Routing

This policy applies whenever an agent delegates work to a subagent.

## Policy

Use the least-capable available model likely to complete the delegated task
correctly. Default to one tier below the parent, within the same family, for
narrow, well-specified, reversible, and easily verified work such as targeted
searches, structured extraction, mechanical edits, and focused test execution.

Retain the parent model for architecture, ambiguity, broad root-cause analysis,
security or safety concerns, irreversible changes, difficult-to-verify
scientific reasoning, and tightly coupled cross-system work. The parent must
validate all delegated results and retains final synthesis and acceptance;
subagents may perform only intermediate, rubric-based review.

## Routing Ladders

- OpenAI: Astra -> Sol -> Terra -> Luna
- Anthropic: Fable -> Opus -> Sonnet -> Haiku

These are project preferences, not universal benchmark rankings. Use exact
identifiers exposed by the platform. If a ladder is missing, stale, or omits the
parent, infer same-family ordering only from trustworthy platform metadata,
provider descriptions, or clearly tiered names. Choose the nearest clearly
lower available tier. If ordering is ambiguous or model selection is
unsupported, inherit the parent model. Change families only at the user's
request.

## Lowest-Tier Restriction

Luna and Haiku are not automatic demotion targets. Use them only for
ultra-bounded, non-judgmental, read-only or trivially reversible work with an
explicit output format and deterministic validation. Never use them for
implementation, review, architecture, security, scientific interpretation,
ambiguous debugging, or final judgment. Otherwise retain the parent tier.

## Delegation and Escalation

Give each subagent one bounded objective, exact context and constraints, allowed
actions, output format, validation criteria, and instructions to report
uncertainty instead of guessing. If its result is incomplete, inconsistent,
outside scope, or fails validation, add context, narrow the task, or escalate
capability. Do not repeat the unchanged prompt at the same tier.

Before integration, the parent compares the result with requirements, inspects
the evidence or edits, and runs the cheapest discriminating validation.

## Relationship to Workflow Skills

This guide controls model tiers project-wide. Workflow skills may refine role
classification; `.agents/skills/subagent-driven-development/SKILL.md` defines
how implementation tasks are split and reviewed.
