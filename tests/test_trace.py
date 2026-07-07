"""Tests for the code path tracer."""

import tempfile
from pathlib import Path


def test_trace_finds_definition():
    from inquisitor.backend import tracer

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "app.py").write_text("def my_function():\n    pass\n")
        result = tracer.trace("my_function", project_path=tmp)
        assert "my_function" in result
        assert "app.py" in result
        assert "Definition" in result


def test_trace_finds_callers():
    from inquisitor.backend import tracer

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "app.py").write_text("def my_function():\n    pass\n")
        (root / "caller.py").write_text("from app import my_function\nmy_function()\n")
        result = tracer.trace("my_function", project_path=tmp)
        assert "caller.py" in result


def test_trace_not_found():
    from inquisitor.backend import tracer

    with tempfile.TemporaryDirectory() as tmp:
        result = tracer.trace("nonexistent_function_xyz", project_path=tmp)
        assert "not found" in result


def test_trace_nonexistent_path():
    from inquisitor.backend import tracer

    result = tracer.trace("foo", project_path="/nonexistent")
    assert "does not exist" in result
