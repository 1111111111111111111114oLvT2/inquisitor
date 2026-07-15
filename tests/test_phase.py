"""Tests for phase tracker — the Newton 7-phase state machine."""

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


def test_initial_phase_is_define():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    assert t.current_phase() == "define"


def test_advance_to_next_phase():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    result = t.set_phase("axioms", findings="scope defined")
    assert "AXIOMS" in result
    assert t.current_phase() == "axioms"


def test_advance_through_all_phases():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    phases = ["define", "axioms", "analysis", "experiment", "synthesis", "validate", "query"]
    for p in phases[1:]:
        t.set_phase(p, findings=f"results for {p}")
    assert t.current_phase() == "query"


def test_invalid_phase_rejected():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    result = t.set_phase("banana")
    assert "Invalid phase" in result
    assert t.current_phase() == "define"


def test_go_backwards():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    t.set_phase("analysis", findings="analyzed")
    t.set_phase("define", findings="re-defining")
    assert t.current_phase() == "define"


def test_summary_includes_completed_phases():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    t.set_phase("define", findings="problem: authentication bug", evidence="issue #42:500")
    t.set_phase("axioms", findings="rules applied", evidence="P10 rules active")
    summary = t.summary()
    assert "AUTHENTICATION BUG" in summary.upper() or "authentication bug" in summary.lower()
    assert "DEFINE" in summary.upper()
    assert "AXIOMS" in summary.upper()


def test_validate_with_evidence_passes():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    t.set_phase("define", findings="scope", evidence="user report at github.com/issue/42")
    t.set_phase("axioms", findings="rules OK", evidence="checked")
    t.set_phase("analysis", findings="traced", evidence="trace output: src/auth.py:15")
    result = t.validate_findings()
    assert "validations passed" in result.lower()


def test_validate_empty_phases_warns():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t = PhaseTracker()
    t.set_phase("define")  # no findings, no evidence
    result = t.validate_findings()
    assert "issue" in result.lower()


def test_session_isolation():
    from inquisitor.backend.phase_tracker import PhaseTracker

    t1 = PhaseTracker(session_name="bug-42")
    t2 = PhaseTracker(session_name="feature-7")
    t1.set_phase("analysis")
    assert t1.current_phase() == "analysis"
    assert t2.current_phase() == "define"


def test_project_scoped_sessions():
    # ponytail: two different project paths should get different sessions
    from inquisitor.backend.phase_tracker import PhaseTracker

    t1 = PhaseTracker(project_path="/tmp/project-a")
    t2 = PhaseTracker(project_path="/tmp/project-b")
    t1.set_phase("experiment", findings="different session")
    assert t1.current_phase() == "experiment"
    assert t2.current_phase() == "define"
