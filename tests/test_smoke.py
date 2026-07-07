"""Smoke test — basic importability."""


def test_import_backend():
    from inquisitor.backend import search, extract, analyzer, tracer, phase_tracker

    assert search
    assert extract
    assert analyzer
    assert tracer
    assert phase_tracker


def test_import_tools():
    from inquisitor.tools import search, analyze, trace, scaffold, phase, verify

    assert search
    assert analyze
    assert trace
    assert scaffold
    assert phase
    assert verify


def test_version():
    from inquisitor import __version__

    assert __version__ == "0.1.0"
