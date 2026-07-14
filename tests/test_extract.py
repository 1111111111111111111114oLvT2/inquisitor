"""PDF detection, backend selection, and fallback for content extraction."""

import inquisitor.backend.extract as ex


# --- content-type / suffix detection ---------------------------------------


def test_is_pdf_by_content_type():
    assert ex._is_pdf("application/pdf", "http://x/doc")
    assert ex._is_pdf("application/pdf; charset=binary", "http://x/doc")


def test_is_pdf_by_suffix():
    assert ex._is_pdf("application/octet-stream", "http://x/report.PDF")
    assert ex._is_pdf("", "http://x/a/b/spec.pdf?v=1")


def test_is_pdf_negative():
    assert not ex._is_pdf("text/html", "http://x/page.html")
    assert not ex._is_pdf("text/html", "http://x/notpdf")


def test_is_texty():
    assert ex._is_texty("text/html; charset=utf-8")
    assert ex._is_texty("application/xml")
    assert ex._is_texty("")  # unknown → treat as texty (old behavior)
    assert not ex._is_texty("image/png")


# --- backend selection policy ----------------------------------------------


def test_backend_forced_pypdf(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "pypdf")
    assert ex._pdf_backend() == "pypdf"


def test_backend_forced_docling_falls_back_when_absent(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "docling")
    monkeypatch.setattr(ex, "_docling_available", lambda: False)
    assert ex._pdf_backend() == "pypdf"


def test_backend_forced_docling_when_present(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "docling")
    monkeypatch.setattr(ex, "_docling_available", lambda: True)
    assert ex._pdf_backend() == "docling"


def test_backend_auto_without_docling(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "auto")
    monkeypatch.setattr(ex, "_docling_available", lambda: False)
    assert ex._pdf_backend() == "pypdf"


def test_backend_auto_docling_but_no_gpu_prefers_pypdf(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "auto")
    monkeypatch.setattr(ex, "_docling_available", lambda: True)
    monkeypatch.setattr(ex, "_gpu_available", lambda: False)
    assert ex._pdf_backend() == "pypdf"


def test_backend_auto_docling_with_gpu(monkeypatch):
    monkeypatch.setattr("inquisitor.config.PDF_BACKEND", "auto")
    monkeypatch.setattr(ex, "_docling_available", lambda: True)
    monkeypatch.setattr(ex, "_gpu_available", lambda: True)
    assert ex._pdf_backend() == "docling"


# --- routing and fallback ---------------------------------------------------


def test_extract_pdf_uses_pypdf(monkeypatch):
    monkeypatch.setattr(ex, "_pdf_backend", lambda: "pypdf")
    monkeypatch.setattr(ex, "_extract_pypdf", lambda data: "PYPDF")
    monkeypatch.setattr(ex, "_extract_docling", lambda data, url: "DOCLING")
    assert ex.extract_pdf(b"%PDF", "http://x/a.pdf") == "PYPDF"


def test_extract_pdf_docling_falls_back_to_pypdf(monkeypatch):
    monkeypatch.setattr(ex, "_pdf_backend", lambda: "docling")
    monkeypatch.setattr(ex, "_extract_docling", lambda data, url: None)  # docling failed
    monkeypatch.setattr(ex, "_extract_pypdf", lambda data: "PYPDF")
    assert ex.extract_pdf(b"%PDF", "http://x/a.pdf") == "PYPDF"


def test_extract_pdf_docling_used_when_it_succeeds(monkeypatch):
    monkeypatch.setattr(ex, "_pdf_backend", lambda: "docling")
    monkeypatch.setattr(ex, "_extract_docling", lambda data, url: "DOCLING")
    monkeypatch.setattr(ex, "_extract_pypdf", lambda data: "PYPDF")
    assert ex.extract_pdf(b"%PDF", "http://x/a.pdf") == "DOCLING"


def test_extract_pypdf_on_garbage_returns_none():
    assert ex._extract_pypdf(b"not a real pdf") is None
