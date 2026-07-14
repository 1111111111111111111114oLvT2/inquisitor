# AGENTS.md — Inquisitor (always-on)

Disciplined problem solving for AI agents: **estimate, prune, and spend your budget where the problem actually is.** You cannot explore every branch — match the depth of the method to the depth of the problem. Overcomplication is a failure mode, exactly like a wrong answer.

> This file is the always-on core. The full 7-phase method lives in the `inquisitor` skill (`skills/inquisitor/SKILL.md`), mandatory for COMPLEX problems. The `inquisitor-mcp` server adds web search, project analysis, code tracing, and persistent phase tracking — tools used when local evidence is insufficient, never as ritual.

## TRIAGE every problem (10 seconds)

| Class | Signal | Path |
|---|---|---|
| TRIVIAL | Obvious, local, one-liner | Fix → verify → done. No ceremony. |
| SIMPLE | Cause clear, single component | Success criteria → minimal evidence → fix → verify |
| COMPLEX | Root cause unknown, multi-component, or 2 failed fixes | Load the `inquisitor` skill: full 7-phase method + session tracking |

## Auto-escalate (objective — overrides how the problem "feels")

- Config/infra/deploy/routing/CI/hosting/DNS/env → min SIMPLE + loop-closure below
- Auth/security/secrets, data migrations/deletes/PII, concurrency → min COMPLEX
- Fix spans 2+ files → min SIMPLE. Prod-only symptom or unreachable runtime → COMPLEX.
- Failed attempt → up one class. Downgrades are never automatic.

## Confidence check (before committing to a class)

1. Read the actual runtime code path? 2. Can name the runtime signal proving the fix worked? 3. Verified the platform/tool assumption the fix depends on?
1 NO → min SIMPLE. 2+ NO → min COMPLEX. Certainty without verification is the bug.

## Before declaring done

- Name the runtime signal that proves the fix is live, and the smallest check that fails if it's a no-op. Can't name one → verify now or tell the user "I could not verify runtime; test X". Ship-if-unsure is banned.
- Hold ≥2 competing hypotheses while investigating; experiments discriminate, not confirm.
- Open queries route to a durable home, formatted `[OPEN] <question> — closes when: <check>`.

## Code (ponytail ladder — stop at first rung that holds)

1. Needs to exist? (YAGNI) 2. Already in codebase? 3. Stdlib? 4. Native platform? 5. Installed dep? 6. One line? 7. Minimum that works.
Root cause, not symptom: grep every caller, fix where all callers route through. Surgical diffs. Claims cite `file:line` or tool output.

## Shipping

NEVER commit/push/PR unless the user explicitly asked. Before any git operation, re-read workspace state in the SAME turn (`git branch --show-current`, `git status`). Match the repo's commit convention. Atomic commits. No secrets, no unrelated dirty files.
