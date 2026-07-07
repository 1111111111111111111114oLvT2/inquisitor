"""inquisitor_trace tool — code path tracing."""

from inquisitor.backend import tracer


def trace(
    symbol: str,
    project_path: str | None = None,
    direction: str = "both",
    max_depth: int = 2,
) -> str:
    """Trace a function, class, or method through the codebase.

    Finds the definition, all callers (who calls this), and all callees
    (what does this call). Essential for understanding data flow and
    debugging complex issues.

    Use this during bug investigations to map the path from entry point to failure.
    Use during analysis to understand how components connect.

    Args:
        symbol: The function/class/method name to trace.
        project_path: Path to the project root (default: current directory).
        direction: "callers" (who calls this), "callees" (what this calls), or "both".
        max_depth: How deep to trace callees (1-3, default 2).

    Returns a formatted trace with file:line references.
    """
    return tracer.trace(
        symbol=symbol,
        project_path=project_path,
        direction=direction,
        max_depth=max_depth,
    )
