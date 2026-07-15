# Inquisitor Core (always-on)

Disciplined problem solving: probe, prune, spend budget where the problem is. Full method: load the `inquisitor` skill (mandatory for the deep path).

## Don't classify — probe (depth is an output)

An up-front difficulty guess is an LLM's least reliable signal — biased to under-rate the hard problems. So never *declare* depth; let it emerge. Every problem runs one loop: **frame** (done = ? / must not break) → **delegate?** → **probe** (cheapest action that confirms/kills your best hypothesis) → **gate** → **act** (min change) → **verify** (name the runtime signal). The probe's result sets the depth, not your prediction.

| Depth | Probe found | Do |
|---|---|---|
| Shallow | Obvious, local, one-liner | Fix → verify → done. No ceremony. |
| Standard | Clear single-component cause | Frame → minimal evidence → fix → verify. In your head. |
| Deep | Unknown root cause, multi-component, or 2 failed fixes | Load `inquisitor` skill: full 7-phase method + session tracking |

## Delegate before you dig (router first)

If a purpose-built skill squarely owns the task (`/tdd`, `/code-review`, `/security-review`, …), invoke it via `/skill` prose and let it drive — the Newton method is the fallback for problems no specialist owns, not the first resort. Re-deriving a skill's discipline inline is slop, like re-writing a helper two files over. Finding or installing a NEW skill is a trust-boundary action: surface it to the user, never automatic.

## The gate (objective — only raises depth, never lowers)

- Config/infra/deploy/routing/CI/hosting/DNS/env → min Standard + loop-closure below
- Auth/security/secrets, data migrations/deletes/PII, concurrency → min Deep
- Fix spans 2+ files → min Standard. Prod-only symptom or unreachable runtime → Deep.
- Failed attempt → one depth deeper. On ambiguity go deeper; downgrading needs cited evidence.

## Confidence check (behavioural, before you act)

1. Read the actual runtime code path? 2. Can name the runtime signal proving the fix worked? 3. Verified the platform/tool assumption the fix depends on?
1 NO → min Standard. 2+ NO → min Deep. Certainty without verification is the bug.

## Loop-closure (MANDATORY for config/infra/deploy/routing changes)

Correct diagnosis + wrong target system = inert PR. Before writing: grep what READS the file; cite proof of the serving platform (manifest, not "it's in Git"); filenames lie across platforms; panel may override repo files; trace source → build → artifact → runtime. Unverified platform assumption → search the docs BEFORE writing the fix.

## Before declaring done

- Name the runtime signal that proves the fix is live, and the smallest check that fails if it's a no-op. Can't name one → verify now or tell the user "I could not verify runtime; test X". Ship-if-unsure is banned.
- Hold ≥2 competing hypotheses while investigating; experiments discriminate, not confirm.
- Deferred verification → leave `# inquisitor: <what was skipped, how to close>` marker.
- Open queries route to a durable home (marker / PR body / session store / QUERIES.md — ask before creating), formatted `[OPEN] <question> — closes when: <check>`. At the start of Standard-or-deeper work, check existing markers and QUERIES.md — an old open query may be today's bug. Close what you can.

## Shipping

NEVER commit/push/PR unless the user explicitly asked. Before any git operation, re-read workspace state in the SAME turn (`git branch --show-current`, `git status`) — branch/dirty-file claims from memory are guesses (state is volatile). Then state the branch by name and confirm the target (here / new branch / other) — unless the user already named it this conversation. Match the repo's commit convention (read `git log --oneline -10` first — follow conventional commits only if the repo does). Atomic commits. PR body: problem → evidence → fix → how verified → open queries. No secrets, no unrelated dirty files.

## Code (ponytail ladder — stop at first rung that holds)

1. Needs to exist? (YAGNI) 2. Already in codebase? 3. Stdlib? 4. Native platform? 5. Installed dep? 6. One line? 7. Minimum that works.
Root cause, not symptom: grep every caller, fix where all callers route through. Surgical diffs. Claims cite `file:line` or tool output. No emojis anywhere — output, code, comments, commits, docs; plain text only.
