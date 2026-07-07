"""Inquisitor MCP server — AI agent investigation and research tool."""

from mcp.server.fastmcp import FastMCP

from inquisitor.tools import analyze, phase, scaffold, search, trace, verify

mcp = FastMCP(
    "inquisitor",
    instructions=(
        "Inquisitor — AI agent investigation and research tool. "
        "Follows Newton's 7-phase Analysis-Synthesis method for structured problem solving. "
        "Use inquisitor_phase to track phases, inquisitor_search for web research, "
        "inquisitor_analyze for project overview, inquisitor_trace for code flow, "
        "inquisitor_verify to validate findings."
    ),
)


@mcp.tool()
def inquisitor_search(
    query: str,
    max_results: int = 8,
    time_range: str | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    engine: str | None = None,
    fetch_content: bool = False,
) -> str:
    """Search the web using DuckDuckGo (free), Brave, or SearXNG."""
    return search.search(
        query=query,
        max_results=max_results,
        time_range=time_range,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        engine=engine,
        fetch_content=fetch_content,
    )


@mcp.tool()
def inquisitor_analyze(project_path: str | None = None) -> str:
    """Scan a project directory and return a structured overview."""
    return analyze.analyze(project_path)


@mcp.tool()
def inquisitor_trace(
    symbol: str,
    project_path: str | None = None,
    direction: str = "both",
    max_depth: int = 2,
) -> str:
    """Trace a function, class, or method through the codebase."""
    return trace.trace(
        symbol=symbol,
        project_path=project_path,
        direction=direction,
        max_depth=max_depth,
    )


@mcp.tool()
def inquisitor_scaffold(
    project_type: str,
    requirements: list[str],
    output_path: str | None = None,
) -> str:
    """Set up a new project with best practices and minimal boilerplate."""
    return scaffold.scaffold(project_type, requirements, output_path)


@mcp.tool()
def inquisitor_phase_get(
    project_path: str | None = None,
    session_name: str = "default",
) -> str:
    """Get the current phase of the Newton investigation."""
    return phase.phase_get(project_path, session_name)


@mcp.tool()
def inquisitor_phase_set(
    target_phase: str,
    findings: str = "",
    evidence: str = "",
    open_questions: str = "",
    project_path: str | None = None,
    session_name: str = "default",
) -> str:
    """Advance to a new phase in the Newton investigation process."""
    return phase.phase_set(
        target_phase=target_phase,
        findings=findings,
        evidence=evidence,
        open_questions=open_questions,
        project_path=project_path,
        session_name=session_name,
    )


@mcp.tool()
def inquisitor_verify(
    project_path: str | None = None,
    session_name: str = "default",
    original_definitions: str = "",
) -> str:
    """Validate investigation findings against the original problem definitions."""
    return verify.verify(project_path, session_name, original_definitions)


def main():
    """Entry point for inquisitor-mcp CLI."""
    import sys

    print(
        "inquisitor-mcp ready (stdio) — this server is spawned by your MCP client, "
        "not used directly. Waiting for client on stdin... (Ctrl+C to exit)",
        file=sys.stderr,
    )
    mcp.run()


if __name__ == "__main__":
    main()
