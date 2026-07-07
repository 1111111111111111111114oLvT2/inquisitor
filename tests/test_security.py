"""Security tests — path traversal and SSRF guards."""

import tempfile
import shutil
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def temp_session_dir(monkeypatch):
    d = Path(tempfile.mkdtemp())
    monkeypatch.setattr("inquisitor.config.SESSION_DIR", d)
    yield d
    shutil.rmtree(d)


def test_session_name_path_traversal_blocked(temp_session_dir):
    from inquisitor.backend.phase_tracker import PhaseTracker

    PhaseTracker(session_name="../../../tmp/evil")
    # db file must be inside SESSION_DIR, nothing written outside
    files = list(temp_session_dir.iterdir())
    assert len(files) == 1
    assert files[0].parent == temp_session_dir
    assert ".." not in files[0].name
    assert "/" not in files[0].name


def test_session_name_sanitized_to_default_when_empty():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker(session_name="")
    assert t.current_phase() == "define"  # works, no crash


def test_ssrf_blocks_localhost():
    from inquisitor.backend.extract import is_safe_url

    assert not is_safe_url("http://localhost/admin")
    assert not is_safe_url("http://localhost:8080/")
    assert not is_safe_url("http://foo.localhost/")


def test_ssrf_blocks_private_ips():
    from inquisitor.backend.extract import is_safe_url

    assert not is_safe_url("http://127.0.0.1/")
    assert not is_safe_url("http://10.0.0.1/")
    assert not is_safe_url("http://192.168.1.1/router")
    assert not is_safe_url("http://169.254.169.254/latest/meta-data/")  # cloud metadata
    assert not is_safe_url("http://[::1]/")


def test_ssrf_blocks_non_http_schemes():
    from inquisitor.backend.extract import is_safe_url

    assert not is_safe_url("file:///etc/passwd")
    assert not is_safe_url("ftp://example.com/")
    assert not is_safe_url("gopher://example.com/")


def test_ssrf_allows_public_urls():
    from inquisitor.backend.extract import is_safe_url

    assert is_safe_url("https://docs.python.org/3/")
    assert is_safe_url("http://example.com/page")


def test_extract_refuses_unsafe_url():
    from inquisitor.backend.extract import extract

    result = extract("http://169.254.169.254/latest/meta-data/")
    assert "Blocked unsafe URL" in result
