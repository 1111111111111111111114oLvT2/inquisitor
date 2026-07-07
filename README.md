<div align="center">

# inquisitor

**Optimal-path problem solving for AI agents**
Triage · Prune · Investigate — never overcomplicate

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-server-8A2BE2?style=flat-square)](https://modelcontextprotocol.io)
[![uv](https://img.shields.io/badge/uv-package-6A3C8E?style=flat-square)](https://github.com/astral-sh/uv)
[![Tests](https://img.shields.io/badge/tests-36_passing-brightgreen?style=flat-square)]()
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)]()

</div>

---

## Overview

**inquisitor** makes AI agents solve problems the way a chess engine plays chess: it cannot explore every branch, so it **estimates complexity first, prunes paths that add no information, and spends its search budget only where the problem actually is**.

It ships as two coordinated layers:

- **MCP server** (`inquisitor-mcp`) — the engine. Web search, project analysis, code tracing, project scaffolding, and a persistent investigation state machine. Works with any MCP-compatible agent: OpenCode, Claude Code, Claude Desktop, Cursor.
- **Agent skill** (`skills/inquisitor/SKILL.md`) — the behavioral layer. Injects the triage heuristic, the pruning rules, and the full methodology into the agent's reasoning.

The methodology synthesizes four sources:

| Source | Contribution |
|--------|--------------|
| Newton's *Opticks* (1704) | Analysis→Synthesis method: define, decompose, experiment, reconstruct, and end with open Queries — *hypotheses non fingo* |
| NASA/JPL *Power of Ten* | 10 hard rules, few enough to remember, strict enough to check mechanically |
| Karpathy's LLM coding guidelines | Think before coding · simplicity first · surgical changes · goal-driven execution |
| Ponytail decision ladder | YAGNI → reuse → stdlib → native → installed dep → one line → minimum code |

> Web search, codebase scans, and code tracing are **tools invoked when local evidence is insufficient — never mandatory rituals**.

---

## How it decides

Every problem goes through 10-second triage before anything else:

```
                        ┌─────────────┐
                        │   TRIAGE    │  heuristic complexity estimate
                        └──────┬──────┘
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
     ┌─────────┐          ┌─────────┐          ┌─────────┐
     │ TRIVIAL │          │ SIMPLE  │          │ COMPLEX │
     └────┬────┘          └────┬────┘          └────┬────┘
          │                    │                    │
     fix → verify      criteria → minimal      full Newton 7-phase
     (no ceremony)     evidence → fix →        DEFINE → AXIOMS →
                       verify                  ANALYSIS → EXPERIMENT →
                                               SYNTHESIS → VALIDATE →
                                               QUERY (with session
                                               tracking as memory)
```

**Escalation is allowed** — two failed fix attempts or contradicting evidence bumps the class up. **Inflated ceremony is not** — a 7-phase investigation of a typo is as wrong as a blind guess at a race condition.

---

## Quick Start

```bash
git clone https://github.com/0x2fycy3/inquisitor.git
cd inquisitor
uv sync
uv run inquisitor-mcp        # starts the MCP server (stdio)
```

### Register with your agent

**Claude Code / Claude Desktop** (`.mcp.json` or settings):

```json
{
  "mcpServers": {
    "inquisitor": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/inquisitor", "inquisitor-mcp"]
    }
  }
}
```

**OpenCode** (`opencode.json`):

```json
{
  "mcp": {
    "inquisitor": {
      "type": "local",
      "command": ["uv", "run", "--directory", "/path/to/inquisitor", "inquisitor-mcp"]
    }
  }
}
```

Then install the skill by copying (or symlinking) `skills/inquisitor/` into your agent's skill directory (e.g. `~/.config/opencode/skills/` or `~/.claude/skills/`).

---

## Tools

| Tool | Purpose | When |
|------|---------|------|
| `inquisitor_search` | Multi-backend web search (DuckDuckGo free/keyless, Brave, SearXNG) with content extraction | Local evidence insufficient: unknown errors, unfamiliar libraries, current best practices |
| `inquisitor_analyze` | Project overview: languages, frameworks, tests, deps, git history | Entering an unfamiliar codebase |
| `inquisitor_trace` | Symbol tracing: definition, callers, callees with `file:line` refs | Bug spans multiple functions/files |
| `inquisitor_phase_get` / `_set` | Newton 7-phase state machine, SQLite-backed per project | COMPLEX investigations — persistent memory across turns |
| `inquisitor_verify` | Validates findings: evidence cited? phases complete? contradictions? | Before declaring a COMPLEX investigation done |
| `inquisitor_scaffold` | Minimal project scaffolding with researched best practices | New project setup, after requirements are clarified |

### Example: `inquisitor_search`

```python
inquisitor_search(
    query="httpx ConnectTimeout retry pattern",
    max_results=8,
    time_range="year",              # day | week | month | year
    include_domains=["github.com"], # optional site: filter
    fetch_content=True,             # full page text, not just snippets
)
```

### Example: phase tracking (COMPLEX path)

```python
inquisitor_phase_set(
    target_phase="experiment",
    findings="500 only occurs when session token > 4KB",
    evidence="repro script output; nginx.conf:34 large_client_header_buffers",
    open_questions="why did token size grow after v2.3 deploy?",
)
```

---

## Project Structure

```
inquisitor/
├── src/inquisitor/
│   ├── server.py                # MCP entry point (FastMCP, 6 tools)
│   ├── config.py                # env configuration
│   ├── tools/                   # thin MCP adapters
│   │   └── search / analyze / trace / scaffold / phase / verify
│   └── backend/                 # pure Python, zero MCP dependency
│       ├── search.py            # DDG / Brave / SearXNG + re-ranking
│       ├── extract.py           # trafilatura → readability fallback, SSRF guard
│       ├── analyzer.py          # project structure scan
│       ├── tracer.py            # callers / callees mapping
│       └── phase_tracker.py     # Newton state machine (SQLite)
├── skills/inquisitor/SKILL.md   # behavioral layer for the agent
├── tests/                       # 36 tests
└── docs/superpowers/specs/      # design spec
```

The `backend/` package is importable standalone — no MCP required:

```python
from inquisitor.backend.search import search
results = search("python asyncio best practices", max_results=5)
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `INQUISITOR_SESSION_DIR` | no | `~/.inquisitor/sessions/` | Investigation state storage |
| `BRAVE_API_KEY` | no | — | Brave Search backend (2k free/month) |
| `SEARXNG_URL` | no | — | Self-hosted SearXNG instance |
| `INQUISITOR_DEFAULT_ENGINE` | no | `ddg` | `ddg` \| `brave` \| `searxng` |
| `INQUISITOR_SEARCH_TIMEOUT` | no | `15` | HTTP timeout (seconds) |
| `INQUISITOR_MAX_CONTENT_LENGTH` | no | `40000` | Max chars per fetched page |
| `INQUISITOR_PREFERRED_DOMAINS` | no | — | Comma-separated domains to boost in ranking |

No API key is required — DuckDuckGo works out of the box.

---

## Security

- **SSRF guard**: content fetching refuses non-http(s) schemes and loopback / private / link-local / metadata targets (`localhost`, `127.0.0.1`, `10.x`, `192.168.x`, `169.254.169.254`, …).
- **Path traversal guard**: session names are sanitized before touching the filesystem.
- **No shell execution**: subprocess calls use argument lists, never `shell=True`.
- **Parameterized SQL** throughout the session store.
- The server runs locally over stdio with your user's privileges — it does not listen on the network.

---

## Development

```bash
uv sync                  # install deps
uv run pytest tests/ -v  # run tests
uv run ruff check .      # lint
```

## Tech

- **uv** — package manager
- **FastMCP** — MCP server framework
- **ddgs / httpx** — search + HTTP
- **trafilatura + readability-lxml** — content extraction (two-tier fallback)
- **SQLite** — investigation state
- **pytest / ruff** — tests and lint

---

## Acknowledgments

The methodology and architecture stand on these shoulders:

- **Sir Isaac Newton — [*Opticks* (1704)](https://www.gutenberg.org/ebooks/33504)** — the Analysis→Synthesis method and the closing Queries pattern. Public domain via Project Gutenberg.
- **Gerard J. Holzmann (NASA/JPL) — [*The Power of Ten: Rules for Developing Safety Critical Code*](https://spinroot.com/gerard/pdf/P10.pdf)** — the template for a rule set small enough to remember and strict enough to check mechanically.
- **[andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)** (forrestchang) — behavioral guidelines derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.
- **[ponytail](https://github.com/dietrichgebert/ponytail)** (Dietrich Gebert) — the decision ladder and the lazy-senior-dev discipline.
- **ayumi** — the clean backend/adapter separation and the keyless DuckDuckGo + trafilatura search pattern.
- **[last30days-skill](https://github.com/mvanhorn/last30days-skill)** (mvanhorn) — inspiration for multi-source research design and the SKILL.md-as-contract pattern.

Licensed under [MIT](LICENSE).
