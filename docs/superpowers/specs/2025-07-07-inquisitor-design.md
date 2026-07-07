# Inquisitor: AI Agent Investigation & Research Tool

## Overview

Inquisitor is an MCP server + OpenCode skill that gives AI agents the power to investigate problems, research solutions, and set up projects with efficiency and precision. It combines:

- **Multi-source web search** (DuckDuckGo + optional Brave/SearXNG)
- **Structured problem-solving** (Newton's 7-phase Analysis-Synthesis method from *Opticks*)
- **Hard behavioral rules** (NASA/JPL Power of Ten, adapted for agents)
- **Efficiency guardrails** (Ponytail decision ladder + Karpathy principles)

## Architecture

```
AI Agent (OpenCode / Claude Code / Cursor)
├── Skill: inquisitor (SKILL.md)
│   ├── Newton 7-phase method (behavioral mandate)
│   ├── P10 hard rules (10 mechanically checkable rules)
│   ├── Ponytail ladder (7 rungs: YAGNI → stdlib → minimum code)
│   └── Karpathy principles (Think → Simple → Surgical → Goal-Driven)
│
└── MCP Server: inquisitor-mcp (Python, FastMCP, uv)
    ├── inquisitor_search   — Multi-source web search + content extraction
    ├── inquisitor_analyze  — Project structure overview
    ├── inquisitor_trace    — Code path tracing (callers, callees, data flow)
    ├── inquisitor_scaffold — Interactive project setup with best practices
    ├── inquisitor_phase    — Get/set current Newton phase + findings
    └── inquisitor_verify   — Verify findings against original definitions
```

### Separation of Concerns

- **`backend/`** — Pure Python, zero MCP or agent framework dependency. Importable standalone.
- **`tools/`** — Thin MCP adapters. Each tool calls the backend, formats output for LLM consumption.
- **`skills/`** — OpenCode skill spec. Behavioral axioms that drive the agent.

Pattern follows ayumi's clean architecture: swap MCP for another protocol → rewrite only `tools/`.

## Directory Structure

```
inquisitor/
├── pyproject.toml
├── src/
│   └── inquisitor/
│       ├── __init__.py
│       ├── server.py              # MCP server entry point
│       ├── config.py              # Environment configuration
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── search.py          # inquisitor_search
│       │   ├── analyze.py         # inquisitor_analyze
│       │   ├── trace.py           # inquisitor_trace
│       │   ├── scaffold.py        # inquisitor_scaffold
│       │   ├── phase.py           # inquisitor_phase
│       │   └── verify.py          # inquisitor_verify
│       └── backend/
│           ├── __init__.py
│           ├── search.py          # Search engine (DDG + fallbacks)
│           ├── extract.py         # Content extraction (trafilatura + readability)
│           ├── analyzer.py        # Project structure analysis
│           ├── tracer.py          # Code path tracing
│           └── phase_tracker.py   # Newton 7-phase state machine (SQLite)
├── skills/
│   └── inquisitor/
│       └── SKILL.md               # Behavioral axioms + tool reference
└── tests/
    └── ...
```

## Triage Layer (v0.2 revision)

The core operating principle is heuristic search with pruning (alpha-beta / MCTS analogy):
the agent cannot explore every branch, so it estimates problem complexity first and prunes
ceremony that adds no information.

| Class | Signal | Path |
|-------|--------|------|
| TRIVIAL | Fix is obvious and local | Fix → verify. No phases, no tools. |
| SIMPLE | Cause is clear, single component | Collapsed path: criteria → minimal evidence → fix → verify |
| COMPLEX | Root cause unknown, multi-component, or 2 failed attempts | Full Newton 7-phase with session tracking |

Escalation is allowed (TRIVIAL→SIMPLE→COMPLEX) when the heuristic proves wrong.
De-escalation of rigor (skipping VALIDATE on a COMPLEX problem) is not.
Search/analyze/trace are tools invoked when local evidence is insufficient — never mandatory rituals.

## Newton 7-Phase State Machine (COMPLEX path only)

For COMPLEX problems the agent progresses through these phases. Current phase tracked by `inquisitor_phase` in a SQLite-backed session store, which acts as persistent memory across turns.

```
  DEFINE ──► AXIOMS ──► ANALYSIS ──► EXPERIMENT
                                              │
      ┌───────────────────────────────────────┘
      ▼
  SYNTHESIS ──► VALIDATE ──► QUERY
      ▲              │
      └──────(fail)──┘
```

### Phase 1: DEFINE
Clarify scope, terms, constraints, success criteria. Karpathy Rule 1 enforced: surface assumptions, ask when unclear, present tradeoffs. No code before definitions are explicit.

### Phase 2: AXIOMS
Apply non-negotiable guardrails. Ponytail ladder active. P10 rules: bounded search scope, no hallucinated facts, evidence required, assumption caps. The axioms are the "constitution" of the investigation — they cannot be violated.

### Phase 3: ANALYSIS
Decompose the problem into smallest solvable units. Map dependencies. For a bug: what code paths are involved? For project setup: what components are needed? Output: a structured plan with verifiable sub-goals (Karpathy Rule 4).

### Phase 4: EXPERIMENT
Act: search web, trace code, run tests, query APIs. **Hypotheses non fingo** — observe results only, don't assume. Each experiment produces evidence that must be cited.

### Phase 5: SYNTHESIS
Reconstruct the solution from verified components. Ponytail: minimum code. No unrequested abstractions. No boilerplate. Every line traces to a verified finding.

### Phase 6: VALIDATE
Check the solution against the original definitions from Phase 1. Run test suite. Run `inquisitor_verify`. If validation fails, loop back to ANALYSIS or EXPERIMENT.

### Phase 7: QUERY
Surface remaining uncertainties, open questions, and next steps. Newton's Queries pattern: the agent MUST list what it doesn't know, what could be wrong, what should be verified next by a human.

## MCP Tools

### inquisitor_search
```python
search(
    query: str,
    max_results: int = 8,
    time_range: Optional[str] = None,  # "day", "week", "month", "year"
    include_domains: Optional[list[str]] = None,
    exclude_domains: Optional[list[str]] = None,
    fetch_content: bool = False,
) -> str
```

Multi-source web search. Keyless by default via DuckDuckGo. Optional Brave and SearXNG backends.

Architecture follows ayumi pattern:
- `backend/search.py` — Pure Python search engine, no MCP dep
- `backend/extract.py` — Two-tier content extraction (trafilatura → readability-lxml fallback)
- `tools/search.py` — MCP adapter, formats output for LLM consumption

Search results are scored positionally, domain-preference boosted, and deduplicated by URL. Content extraction is LLM-optimized markdown with source attribution.

### inquisitor_analyze
```python
analyze(project_path: Optional[str] = None) -> str
```

Scans a project directory and returns structured overview:
- File tree (top-level, key directories)
- Language/framework detection
- Dependency manifest (pyproject.toml, package.json, Cargo.toml, etc.)
- Test structure and runner
- Recent git log (last 20 commits)
- Codebase stats (file count, line count, language breakdown)

### inquisitor_trace
```python
trace(
    symbol: str,              # function/class/method name to trace
    project_path: Optional[str] = None,
    direction: str = "both",  # "callers", "callees", "both"
    max_depth: int = 2,
) -> str
```

Traces a code path through the codebase:
- Finds the symbol definition (file:line)
- Maps callers (who calls this)
- Maps callees (what does this call)
- Shows data flow through the path
- Returns a structured trace with file references

Uses grep + AST parsing (no language-server dependency — ponytail rung 5).

### inquisitor_scaffold
```python
scaffold(
    project_type: str,        # e.g. "fastapi", "react", "cli"
    requirements: list[str],  # user requirements
    output_path: Optional[str] = None,
) -> str
```

Interactive project setup:
1. Asks clarifying questions (Karpathy Rule 1): language, framework, features, constraints
2. Researches best practices for the chosen stack
3. Generates minimal boilerplate (ponytail: no unrequested configs)
4. Returns scaffolded file list and next steps

Does NOT generate until questions are answered. Does NOT add features not requested.

### inquisitor_phase
```python
phase_get() -> str     # Returns current phase + findings summary
phase_set(phase: str)  # Advances to a new phase
```

Manages the Newton 7-phase state machine. Each phase transition records:
- Phase name and timestamp
- Key findings from the phase
- Open questions carried forward
- Evidence collected

Backed by SQLite in `~/.inquisitor/sessions/`. Project-scoped: different sessions for different repos.

### inquisitor_verify
```python
verify(finding: Optional[str] = None) -> str
```

Checks current findings against the original definitions from Phase 1:
- All claims have evidence citations?
- All assumptions confirmed or flagged?
- Any contradictions between findings?
- Code changes match the verified plan?
- Phase validation: can we proceed to QUERY?

## SKILL.md Design

The skill (`skills/inquisitor/SKILL.md`) is the behavioral layer injected into the AI agent's reasoning context. It has five sections:

### 1. Newton Mandate (Non-Negotiable)
The agent must progress through the 7 phases. Must use `inquisitor_phase` to track state. Ending a phase without `phase_set` is a violation.

### 2. P10 Agency Rules (10 Hard Rules)
Adapted from NASA/JPL for AI agents:
1. **No hallucination**: Every factual claim must cite a source (tool output, file:line, URL)
2. **Bounded search**: Search queries must be explicit. No "explore the codebase" without a target.
3. **Return value checking**: Every tool call result must be read and considered before proceeding.
4. **Scope discipline**: No code generation outside the defined scope. No "while I'm here" refactors.
5. **Assumption density**: Minimum 2 assertions per finding. Assertions can't be tautologies.
6. **Minimal scope**: Changes must target the smallest possible scope (file, function, block).
7. **Error propagation**: Errors from tools must be handled, not ignored.
8. **Preprocessor restraint**: No hidden complexity. All code must be directly readable.
9. **Pointer restraint**: No more than one level of indirection (abstraction → implementation → deeper is banned without explicit justification).
10. **Zero warnings**: All generated code must pass the project's linter and typechecker before being declared done.

### 3. Ponytail Ladder (Decision Framework)
1. Does this need to exist at all? (YAGNI)
2. Already in this codebase?
3. Does stdlib do it?
4. Does native platform feature cover it?
5. Already-installed dependency solves it?
6. Can it be one line?
7. Only then: write minimum code.

### 4. Karpathy Principles (Behavioral)
- **Think Before Coding**: State assumptions. Surface tradeoffs. Ask when unclear.
- **Simplicity First**: No speculative features. No abstractions for single-use. If 200 lines could be 50, rewrite.
- **Surgical Changes**: Every changed line must trace to the request. Own your orphans.
- **Goal-Driven Execution**: Define success criteria before acting. Loop until verified.

### 5. Tool Reference
Quick reference for all 6 MCP tools: signatures, when to use, examples.

## Search Engine Design

### Backends (priority order)
1. DuckDuckGo (ddgs) — free, keyless, always available
2. Brave Search — BRAVE_API_KEY env var, 2k free/month, higher quality
3. SearXNG — SEARXNG_URL env var, self-hosted, full privacy

### Extraction Pipeline
1. trafilatura (primary, F1 0.958) — best for article content
2. readability-lxml (fallback) — handles non-article pages
3. Markdown output with source URL in header

### Scoring
- Positional decay: `max(0.05, 1.0 - i * 0.08)`
- Domain preference boost (configurable)
- Recency boost when `time_range` is set
- URL-based deduplication

## Configuration

All via environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `INQUISITOR_SESSION_DIR` | Where session state is stored | `~/.inquisitor/sessions/` |
| `BRAVE_API_KEY` | Brave Search API key | None (use DDG) |
| `SEARXNG_URL` | Self-hosted SearXNG instance | None (use DDG) |
| `INQUISITOR_SEARCH_TIMEOUT` | Search HTTP timeout (seconds) | 15 |
| `INQUISITOR_MAX_CONTENT_LENGTH` | Max chars for fetched content | 40000 |
| `INQUISITOR_DEFAULT_ENGINE` | Default search backend | "ddg" |
| `INQUISITOR_PREFERRED_DOMAINS` | Comma-separated domain boost list | "" |
| `INQUISITOR_LOG_LEVEL` | Logging level | "INFO" |

## Technology Choices

- **Python 3.12+**, **uv** package manager
- **FastMCP** for MCP server (lightweight, zero-boilerplate)
- **httpx** for HTTP (sync, with retries)
- **ddgs** for DuckDuckGo search
- **trafilatura** + **readability-lxml** for content extraction
- **SQLite** for session state
- **pytest** for tests

No async complexity. Sync throughout. Follows ayumi's successful pattern.

## Open Questions

1. Should `inquisitor_scaffold` integrate with `inquisitor_search` to research best practices before scaffolding?
   → **Decision**: Yes. Scaffold uses search to find current best practices for the chosen stack before generating code.
2. Should there be a `inquisitor_report` tool that generates a final summary document?
   → **Decision**: Not in v1. QUERY phase covers this. Add when users ask for exportable reports.
3. CI/CD integration — should inquisitor run in CI as a validation step?
   → **Decision**: Out of scope for v1. Add when someone asks.
