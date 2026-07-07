"""Content extraction — trafilatura with readability-lxml fallback."""

import re

import httpx
from readability import Document

from inquisitor.config import SEARCH_TIMEOUT, MAX_CONTENT_LENGTH

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


def _random_ua() -> str:
    import random

    return random.choice(USER_AGENTS)


def extract(url: str, html: str | None = None) -> str:
    """Extract readable content from a URL. Returns markdown-formatted text."""
    if html is None:
        html = _fetch_html(url)

    if not html:
        return f"Failed to fetch content from {url}"

    content = _extract_trafilatura(html) or _extract_readability(html, url)

    if not content or len(content.strip()) < 50:
        return f"No meaningful content extracted from {url}"

    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated]"

    return content


def _fetch_html(url: str) -> str | None:
    try:
        with httpx.Client(
            timeout=SEARCH_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": _random_ua(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "")
            if "html" not in ct.lower() and "text" not in ct.lower():
                return None
            return resp.text
    except Exception:
        return None


def _extract_trafilatura(html: str) -> str | None:
    try:
        import trafilatura

        result = trafilatura.extract(
            html,
            favor_recall=True,
            include_tables=True,
            output_format="markdown",
        )
        return result.strip() if result else None
    except Exception:
        return None


def _extract_readability(html: str, url: str) -> str | None:
    try:
        doc = Document(html)
        title = doc.title() or url
        body = doc.summary()
        text = re.sub(r"<[^>]+>", "", body)
        text = re.sub(r"\s{3,}", "\n\n", text)
        text = text.strip()
        if not text:
            return None
        return f"# {title}\n\nSource: {url}\n\n---\n\n{text}"
    except Exception:
        return None
