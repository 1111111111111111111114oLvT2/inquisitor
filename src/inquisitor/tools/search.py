"""inquisitor_search tool — multi-source web search."""

from inquisitor.backend import search as backend


def search(
    query: str,
    max_results: int = 8,
    time_range: str | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    engine: str | None = None,
    fetch_content: bool = False,
) -> str:
    """Search the web using DuckDuckGo (free), Brave, or SearXNG.

    Use this to research errors, find documentation, check best practices,
    or look up anything about libraries, frameworks, and code patterns.

    Args:
        query: The search query. Use quotes for exact phrases, site: for domain filtering.
        max_results: Number of results (max 20).
        time_range: Filter by recency: "day", "week", "month", "year".
        include_domains: Only show results from these domains.
        exclude_domains: Exclude results from these domains.
        engine: Search backend: "ddg" (default), "brave", or "searxng".
        fetch_content: If True, fetch full page content for each result.

    Returns formatted search results with scores and snippets.
    """
    response = backend.search(
        query=query,
        max_results=max_results,
        time_range=time_range,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        engine=engine,
        fetch_content=fetch_content,
    )

    if response.error and not response.results:
        return f"Search error: {response.error}"

    lines = [f"Search results for: '{response.query}'"]
    if response.engine:
        lines.append(f"Engine: {response.engine}")
    lines.append("")

    for i, r in enumerate(response.results, 1):
        lines.append(f"[{i}] {r.title}")
        lines.append(f"    URL: {r.url}")
        lines.append(f"    {r.snippet}")
        lines.append("")

    if response.error:
        lines.append(f"Note: {response.error}")

    if not response.results:
        return f"No results found for query: '{response.query}'"

    return "\n".join(lines)
