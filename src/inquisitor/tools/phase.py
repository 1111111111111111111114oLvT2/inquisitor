"""inquisitor_phase tool — Newton 7-phase state management."""

from inquisitor.backend.phase_tracker import PhaseTracker, PHASES


def phase_get(project_path: str | None = None, session_name: str = "default") -> str:
    """Get the current phase of the Newton investigation.

    Returns the current phase and a summary of all phases completed so far.

    Use this at the start of any turn to understand where we are in the process.
    Use before advancing phases to confirm readiness.

    Args:
        project_path: Path to the project root (default: current directory).
        session_name: Session identifier (default: "default").

    Returns current phase and investigation summary.
    """
    tracker = PhaseTracker(project_path, session_name)
    return tracker.summary()


def phase_set(
    target_phase: str,
    findings: str = "",
    evidence: str = "",
    open_questions: str = "",
    project_path: str | None = None,
    session_name: str = "default",
) -> str:
    """Advance to a new phase in the Newton investigation process.

    The 7 phases must be traversed in order:
      DEFINE → AXIOMS → ANALYSIS → EXPERIMENT → SYNTHESIS → VALIDATE → QUERY

    Forward moves advance one phase at a time — skipping ahead is rejected.
    Backward moves (e.g. VALIDATE → ANALYSIS after a failed check) are always
    allowed. Re-setting the current phase appends another entry to it.

    You MUST record findings and evidence before advancing — advancing past
    a phase with no recorded findings/evidence is rejected, not just flagged.
    Record the current phase (set_phase to the SAME phase appends an entry),
    then advance.

    Args:
        target_phase: The phase to advance to (one of: define, axioms, analysis,
                     experiment, synthesis, validate, query).
        findings: Key discoveries from the current phase.
        evidence: Citations for findings (tool output, file:line, URL).
        open_questions: What's still unknown after this phase.
        project_path: Path to the project root (default: current directory).
        session_name: Session identifier (default: "default").

    Returns confirmation of the phase transition.
    """
    if target_phase not in PHASES:
        return f"Invalid phase: '{target_phase}'. Valid: {', '.join(PHASES)}"

    tracker = PhaseTracker(project_path, session_name)
    return tracker.set_phase(
        target=target_phase,
        findings=findings,
        evidence=evidence,
        open_questions=open_questions,
    )
