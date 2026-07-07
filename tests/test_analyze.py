"""Tests for the project analyzer."""

import tempfile
from pathlib import Path


def test_analyze_empty_project():
    from inquisitor.backend import analyzer

    with tempfile.TemporaryDirectory() as tmp:
        result = analyzer.analyze(tmp)
        assert "Project Analysis" in result
        assert "Languages" in result
        assert "No source files" in result or "No known framework" in result


def test_analyze_detects_python():
    from inquisitor.backend import analyzer

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "pyproject.toml").write_text("[project]\nname = 'test'\ndependencies = ['fastapi']\n")
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("def hello(): pass\n")
        result = analyzer.analyze(tmp)
        assert "Python" in result
        assert "fastapi" in result.lower()


def test_analyze_nonexistent_path():
    from inquisitor.backend import analyzer

    result = analyzer.analyze("/nonexistent/path/xyz")
    assert "does not exist" in result


def test_analyze_detects_tests():
    from inquisitor.backend import analyzer

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "tests").mkdir()
        (root / "tests" / "test_main.py").write_text("def test(): pass\n")
        result = analyzer.analyze(tmp)
        assert "tests/" in result
