# Companion skills & references

inquisitor is a **router as much as an investigator** (Rung 0 of the method): when a purpose-built skill squarely fits a task, it hands off — `/tdd` for test-first work, `/code-review` for a diff, and so on — instead of re-deriving that discipline inline.

**inquisitor does not install those skills for you.** Installing a skill loads third-party instructions (and sometimes code) into your agent — a trust-boundary action it deliberately leaves to you. Install a specialist and inquisitor will delegate to it; skip it and inquisitor falls back to its own method, or tells you a skill would fit and asks.

This is the curated set that pairs well. **Review a repo before installing** — you are loading its instructions into your agent.

---

## Recommended skills

### vercel-labs/skills — the discovery + install layer (~26k stars)
Not a specialist to delegate to — the **package manager for the skills ecosystem** (`npx skills`), plus a bundled `find-skills` skill. This is what makes inquisitor's Rung 0 *executable*: when inquisitor says *"a `/foo` skill would fit — want me to find one?"*, this is how you answer it, and how you install any of the specialists below from one command across agents.

```bash
npx skills find "test-first workflow"   # discover (or browse the leaderboard at skills.sh)
npx skills add owner/repo               # install from GitHub/GitLab/git URL/local path
```

inquisitor's own skill already uses the ecosystem's `skills/<name>/SKILL.md` layout, so it is installable the same way — `npx skills add 1111111111111111111114oLvT2/inquisitor` — with no extra packaging.

### mattpocock/skills — the core companion (~170k stars)
The closest match to inquisitor's delegation targets: `/tdd`, `/code-review`, `/diagnosing-bugs`, `/research`, `/implement`, and ~25 more — each a small, single-purpose skill. When inquisitor's Rung 0 says "hand off to `/tdd` or `/code-review`," this is what makes those real. **Highest-value install.**

```
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```

### github/spec-kit — spec-driven feature building (~121k stars)
A toolkit for turning an idea into **spec → plan → tasks → implementation**. Complements inquisitor's *Frame* step and the deep-path *DEFINE* phase for greenfield and large features — the "on-ramp" scaffolding inquisitor's own method doesn't provide. Heavier; best when building a feature from scratch.

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init my-project --integration claude    # add --integration-options="--skills" for skills mode
```
(Run `specify init --help` for the supported agent names.)

### mvanhorn/last30days-skill — recency research (~52k stars)
Researches a topic across Reddit, X, YouTube, HN, and the web into a grounded summary. Complements `inquisitor_search` when the question is "what's the *current* state / recent discussion of X" rather than a doc lookup. (Credited as inspiration for inquisitor's multi-source research design.)

```
/plugin marketplace add mvanhorn/last30days-skill
/plugin install last30days@last30days-skill
```

### DietrichGebert/ponytail — always-on minimalism (optional, ~83k stars)
inquisitor already **embeds ponytail's decision ladder** (YAGNI → reuse → stdlib → native → dep → one line → minimum) for its own code output, so installing ponytail is **not required**. What it adds that inquisitor's embedded ladder can't: *always-on* enforcement across **all** your coding (a lifecycle hook keeps it active every turn, not just when inquisitor is invoked), intensity levels (`lite/full/ultra`), and audit sub-skills. Install it if you want minimalism enforced everywhere; expect some overlap in emphasis with inquisitor.

```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

### garrytan/gstack — opinionated all-in-one (à la carte, ~121k stars)
Garry Tan's full 23-skill setup (CEO / designer / eng-manager / release / QA roles, plus `/browse`, `/autoplan`, `/review`, `/ship`, …). It's a complete **opinionated environment**, not a single specialist — adopting all 23 alongside inquisitor + mattpocock risks overlapping roles and context bloat. Recommend **cherry-picking** individual skills (e.g. `/browse`, `/autoplan`) rather than wholesale adoption.

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack \
  && cd ~/.claude/skills/gstack && ./setup
```

---

## References (not skills)

These are **passive project content**, not capabilities. inquisitor's **tools** are always in the agent's tool list, and **skills** are invoked — but a reference is just a file the agent reads *if it lives in your project*. Nothing loads it automatically, and that's deliberate: you opt in per project rather than carry every design opinion into every repo.

### voltagent/awesome-design-md — design system `DESIGN.md` files (~101k stars)
A collection of `DESIGN.md` files distilled from popular brand design systems. **To use one:** copy the `DESIGN.md` you want into a project — commit it at the repo root, or point your `CLAUDE.md` / `AGENTS.md` at it — and the agent reads it as context, generating UI that matches that system. inquisitor can also *fetch* a relevant one via `inquisitor_search` during a UI task, but **you** decide which to commit.

<https://github.com/voltagent/awesome-design-md>

---

## How inquisitor uses these

It only *reaches for* a skill that is **installed and squarely fits** the task; it never installs one silently. When a specialist would help but isn't present, it says so and asks — that's Rung 0 ("delegate before you dig") in the [skill](../skills/inquisitor/SKILL.md). The concrete way to act on that prompt is `npx skills find <query>` (vercel-labs/skills, above); the decision to install stays yours. The stars above are approximate and drift over time.
