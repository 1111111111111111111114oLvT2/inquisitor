"""Tests for the search engine backend."""

from inquisitor.backend.search import _build_query, _time_param, SearchResult, SearchResponse


def test_build_query_adds_include_domains():
    q = _build_query("python", ["docs.python.org"], None)
    assert "site:docs.python.org" in q


def test_build_query_adds_exclude_domains():
    q = _build_query("python", None, ["reddit.com"])
    assert "-site:reddit.com" in q


def test_build_query_combines_include_and_exclude():
    q = _build_query("python", ["docs.python.org"], ["reddit.com", "youtube.com"])
    assert "site:docs.python.org" in q
    assert "-site:reddit.com" in q
    assert "-site:youtube.com" in q


def test_build_query_plain():
    q = _build_query("hello world", None, None)
    assert q == "hello world"


def test_time_param_mapping():
    assert _time_param("day") == "d"
    assert _time_param("week") == "w"
    assert _time_param("month") == "m"
    assert _time_param("year") == "y"
    assert _time_param(None) is None
    assert _time_param("century") is None


def test_search_response_creation():
    r = SearchResponse(
        query="test",
        results=[SearchResult(title="T", url="http://t.com", snippet="s", score=0.95)],
        engine="ddg",
    )
    assert len(r.results) == 1
    assert r.results[0].score == 0.95
    assert r.engine == "ddg"


def test_max_results_clamped():
    from inquisitor.backend.search import search

    resp = search("test", max_results=999)
    assert len(resp.results) <= 20


def test_search_returns_results():
    from inquisitor.backend.search import search

    resp = search("python programming", max_results=3)
    if resp.error:
        # DDG might be down — test the error path
        assert resp.engine == "ddg"
    else:
        assert len(resp.results) > 0
        for r in resp.results:
            assert r.title
            assert r.url
