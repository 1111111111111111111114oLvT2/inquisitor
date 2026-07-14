"""Content extraction — HTML (trafilatura → readability) and PDF (pypdf default; docling optional)."""

import importlib.util
import ipaddress
import os
import re
import sys
from urllib.parse import urlparse

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


def is_safe_url(url: str) -> bool:
    """SSRF guard: only http(s), no loopback/private/link-local targets.

    ponytail: name-level check; DNS-rebinding defense would need resolve-then-pin,
    add if this ever runs server-side with untrusted multi-tenant input.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname or ""
        if not host or host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            return False
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
        except ValueError:
            pass  # hostname, not a literal IP
        return True
    except Exception:
        return False


def extract(url: str, html: str | None = None) -> str:
    """Extract readable content from a URL. Returns markdown-formatted text.

    HTML goes through trafilatura → readability. PDFs (by content-type or `.pdf`
    suffix) use the configured PDF backend (pypdf by default; docling optional with pypdf fallback).
    """
    if html is not None:
        content = _extract_html(html, url)
    else:
        if not is_safe_url(url):
            return f"Blocked unsafe URL (non-http or private/internal target): {url}"
        fetched = _fetch(url)
        if fetched is None:
            return f"Failed to fetch content from {url}"
        content_type, data = fetched
        if _is_pdf(content_type, url):
            content = extract_pdf(data, url)
        elif _is_texty(content_type):
            m = re.search(r"charset=([^\s;]+)", content_type, flags=re.I)
            enc = m.group(1).strip("\"'") if m else "utf-8"
            try:
                text = data.decode(enc, errors="replace")
            except LookupError:
                text = data.decode("utf-8", errors="replace")
            content = _extract_html(text, url)
        else:
            return f"Unsupported content type '{content_type or 'unknown'}' at {url}"

    if not content or len(content.strip()) < 50:
        return f"No meaningful content extracted from {url}"

    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated]"

    return content


def _fetch(url: str) -> tuple[str, bytes] | None:
    """Fetch a URL, returning (content_type, body_bytes) or None on failure."""
    try:
        with httpx.Client(
            timeout=SEARCH_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": _random_ua(),
                "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.headers.get("content-type", ""), resp.content
    except Exception:
        return None


def _is_pdf(content_type: str, url: str) -> bool:
    return "pdf" in content_type.lower() or urlparse(url).path.lower().endswith(".pdf")


def _is_texty(content_type: str) -> bool:
    ct = content_type.lower()
    return "html" in ct or "text" in ct or "xml" in ct or not ct


def _extract_html(html: str, url: str) -> str | None:
    return _extract_trafilatura(html) or _extract_readability(html, url)


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


# --- PDF extraction ---------------------------------------------------------
#
# pypdf (pure-Python, always installed) handles text PDFs — the common case.
# docling (optional `[docling]` extra) handles complex tables / scanned OCR, but
# drags in torch + ML models and is slow on CPU, so `auto` only reaches for it
# when a GPU is present. Same two-tier fallback shape as HTML above.

_notes_emitted: set[str] = set()


def _note_once(msg: str) -> None:
    if msg not in _notes_emitted:
        _notes_emitted.add(msg)
        print(msg, file=sys.stderr)


def _docling_available() -> bool:
    return importlib.util.find_spec("docling") is not None


def _gpu_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _pdf_backend() -> str:
    """Resolve INQUISITOR_PDF_BACKEND (auto|docling|pypdf) to the backend to use."""
    from inquisitor.config import PDF_BACKEND

    if PDF_BACKEND == "pypdf":
        return "pypdf"
    if PDF_BACKEND == "docling":
        return "docling" if _docling_available() else "pypdf"
    # auto: docling only when installed AND a GPU is present — CPU docling is too
    # slow for the agent loop; pypdf keeps reads fast and universal.
    if _docling_available():
        if _gpu_available():
            return "docling"
        _note_once(
            "pdf: using pypdf (docling installed but no GPU detected); "
            "set INQUISITOR_PDF_BACKEND=docling to force docling on CPU"
        )
    return "pypdf"


def extract_pdf(data: bytes, url: str) -> str | None:
    """Convert PDF bytes to text/markdown via the configured backend, pypdf fallback."""
    if _pdf_backend() == "docling":
        return _extract_docling(data, url) or _extract_pypdf(data)
    return _extract_pypdf(data)


def _extract_pypdf(data: bytes) -> str | None:
    try:
        import io

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        parts = [(page.extract_text() or "").strip() for page in reader.pages]
        text = "\n\n".join(p for p in parts if p)
        return text or None
    except Exception:
        return None


def _extract_docling(data: bytes, url: str) -> str | None:
    tmp_path = None
    try:
        import tempfile

        from docling.document_converter import DocumentConverter

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        result = DocumentConverter().convert(tmp_path)
        return result.document.export_to_markdown() or None
    except Exception:
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
