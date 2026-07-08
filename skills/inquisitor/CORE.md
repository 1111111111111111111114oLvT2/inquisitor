# Inquisitor Core (always-on)

Disciplined problem solving: estimate, prune, spend budget where the problem is. Full method: load the `inquisitor` skill (mandatory for COMPLEX).

## TRIAGE every problem (10 seconds)

| Class | Signal | Path |
|---|---|---|
| TRIVIAL | Obvious, local, one-liner | Fix → verify → done. No ceremony. |
| SIMPLE | Cause clear, single component | Success criteria → minimal evidence → fix → verify |
| COMPLEX | Root cause unknown, multi-component, or 2 failed fixes | Load `inquisitor` skill: full 7-phase method + session tracking |

## Auto-escalate (objective — overrides how the problem "feels")

- Config/infra/deploy/routing/CI/hosting/DNS/env → min SIMPLE + loop-closure below
- Auth/security/secrets, data migrations/deletes/PII, concurrency → min COMPLEX
- Fix spans 2+ files → min SIMPLE. Prod-only symptom or unreachable runtime → COMPLEX.
- Failed attempt → up one class. Downgrades are never automatic.

## Confidence check (before committing to a class)

1. Read the actual runtime code path? 2. Can name the runtime signal proving the fix worked? 3. Verified the platform/tool assumption the fix depends on?
1 NO → min SIMPLE. 2+ NO → min COMPLEX. Certainty without verification is the bug.

## Loop-closure (MANDATORY for config/infra/deploy/routing changes)

Correct diagnosis + wrong target system = inert PR. Before writing: grep what READS the file; cite proof of the serving platform (manifest, not "it's in Git"); filenames lie across platforms; panel may override repo files; trace source → build → artifact → runtime. Unverified platform assumption → search the docs BEFORE writing the fix.

## Before declaring done

- Name the runtime signal that proves the fix is live, and the smallest check that fails if it's a no-op. Can't name one → verify now or tell the user "I could not verify runtime; test X". Ship-if-unsure is banned.
- Hold ≥2 competing hypotheses while investigating; experiments discriminate, not confirm.
- Deferred verification → leave `# inquisitor: <what was skipped, how to close>` marker.
- Open queries route to a durable home (marker / PR body / session store / QUERIES.md — ask before creating), formatted `[OPEN] <question> — closes when: <check>`. At the start of SIMPLE+ work, check existing markers and QUERIES.md — an old open query may be today's bug. Close what you can.

## Shipping

NEVER commit/push/PR unless the user explicitly asked. Before committing, state the current branch by name and confirm the target (here / new branch / other) — unless the user already named it this conversation. Match the repo's commit convention (read `git log --oneline -10` first — follow conventional commits only if the repo does). Atomic commits. PR body: problem → evidence → fix → how verified → open queries. No secrets, no unrelated dirty files.

## Code (ponytail ladder — stop at first rung that holds)

1. Needs to exist? (YAGNI) 2. Already in codebase? 3. Stdlib? 4. Native platform? 5. Installed dep? 6. One line? 7. Minimum that works.
Root cause, not symptom: grep every caller, fix where all callers route through. Surgical diffs. Claims cite `file:line` or tool output.
