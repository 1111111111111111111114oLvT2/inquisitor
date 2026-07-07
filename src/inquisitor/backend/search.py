"""Search engine — multi-backend web search with re-ranking."""

import time
from dataclasses import dataclass, field

from inquisitor.config import (
    BRAVE_API_KEY,
    SEARXNG_URL,
    SEARCH_TIMEOUT,
    SEARCH_RETRIES,
    DEFAULT_ENGINE,
    PREFERRED_DOMAINS,
)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float = 1.0


@dataclass
class SearchResponse:
    query: str = ""
    results: list[SearchResult] = field(default_factory=list)
    engine: str = ""
    error: str | None = None


def search(
    query: str,
    max_results: int = 8,
    time_range: str | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    engine: str | None = None,
    fetch_content: bool = False,
) -> SearchResponse:
    """Multi-backend web search. Falls back from preferred to keyless."""
    engine = engine or DEFAULT_ENGINE
    max_results = min(max_results, 20)

    q = _build_query(query, include_domains, exclude_domains)
    time_param = _time_param(time_range)

    # ponytail: try engines in priority order, first one that works wins
    engines = [engine]
    if engine != "ddg":
        engines.append("ddg")

    for eng in engines:
        response = _search_with(q, max_results, time_param, eng, fetch_content)
        if response.error is None:
            response.query = query
            return response

    return SearchResponse(query=query, error="All search backends failed")


def _build_query(query: str, include: list[str] | None, exclude: list[str] | None) -> str:
    q = query
    if include:
        for d in include:
            q += f" site:{d}"
    if exclude:
        for d in exclude:
            q += f" -site:{d}"
    return q


def _time_param(time_range: str | None) -> str | None:
    if not time_range:
        return None
    mapping = {"day": "d", "week": "w", "month": "m", "year": "y"}
    return mapping.get(time_range.lower(), None)


def _search_with(
    query: str,
    max_results: int,
    time_param: str | None,
    engine: str,
    fetch_content: bool,
) -> SearchResponse:
    if engine == "brave" and BRAVE_API_KEY:
        return _search_brave(query, max_results, time_param, fetch_content)
    if engine == "searxng" and SEARXNG_URL:
        return _search_searxng(query, max_results, time_param, fetch_content)
    return _search_ddg(query, max_results, time_param, fetch_content)


def _search_ddg(query: str, max_results: int, time_param: str | None, fetch_content: bool) -> SearchResponse:
    for attempt in range(SEARCH_RETRIES + 1):
        try:
            from ddgs import DDGS

            with DDGS() as ddgs:
                kwargs = {"max_results": max_results}
                if time_param:
                    kwargs["timelimit"] = time_param
                raw = list(ddgs.text(query, **kwargs))

            results = _score_and_rerank(raw, max_results, fetch_content)
            return SearchResponse(results=results, engine="ddg")

        except Exception as e:
            if attempt < SEARCH_RETRIES:
                time.sleep(1.5 * (attempt + 1))
            else:
                return SearchResponse(engine="ddg", error=f"DuckDuckGo: {e}")

    return SearchResponse(engine="ddg", error="DuckDuckGo: unexpected failure")


def _search_brave(query: str, max_results: int, time_param: str | None, fetch_content: bool) -> SearchResponse:
    # ponytail: basic implementation, add pagination/dates when needed

    import httpx

    try:
        resp = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": max_results},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": BRAVE_API_KEY,
            },
            timeout=SEARCH_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for i, item in enumerate(data.get("web", {}).get("results", [])[:max_results]):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    score=max(0.05, 1.0 - i * 0.08),
                )
            )

        _apply_domain_preference(results)
        return SearchResponse(results=results, engine="brave")

    except Exception as e:
        return SearchResponse(engine="brave", error=str(e))


def _search_searxng(query: str, max_results: int, time_param: str | None, fetch_content: bool) -> SearchResponse:

    import httpx

    try:
        params: dict = {"q": query, "format": "json", "categories": "general"}
        if time_param:
            params["time_range"] = time_param

        resp = httpx.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=SEARCH_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for i, item in enumerate(data.get("results", [])[:max_results]):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    score=max(0.05, 1.0 - i * 0.08),
                )
            )

        _apply_domain_preference(results)
        return SearchResponse(results=results, engine="searxng")

    except Exception as e:
        return SearchResponse(engine="searxng", error=str(e))


def _score_and_rerank(
    raw: list[dict], max_results: int, fetch_content: bool
) -> list[SearchResult]:
    results = []
    seen_urls: set[str] = set()

    for i, item in enumerate(raw):
        url = item.get("href", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        score = max(0.05, 1.0 - i * 0.08)
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=url,
                snippet=item.get("body", ""),
                score=score,
            )
        )

        if len(results) >= max_results:
            break

    _apply_domain_preference(results)

    if fetch_content:
        _enrich_content(results)

    return sorted(results, key=lambda r: r.score, reverse=True)


def _apply_domain_preference(results: list[SearchResult]) -> None:
    if not PREFERRED_DOMAINS:
        return
    for r in results:
        for domain in PREFERRED_DOMAINS:
            if domain in r.url:
                r.score = min(1.0, r.score + 0.15)
                break


def _enrich_content(results: list[SearchResult]) -> None:
    # ponytail: sequential fetches, add ThreadPoolExecutor if latency matters
    from inquisitor.backend.extract import extract

    for r in results:
        try:
            content = extract(r.url)
            r.snippet = content
        except Exception:
            pass
