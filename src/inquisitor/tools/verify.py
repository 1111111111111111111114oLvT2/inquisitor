"""inquisitor_verify tool — validate findings against original definitions."""

from inquisitor.backend.phase_tracker import PhaseTracker


def verify(
    project_path: str | None = None,
    session_name: str = "default",
    original_definitions: str = "",
) -> str:
    """Completeness check on the investigation record.

    Checks (mechanical):
    - Was each reached phase recorded with non-empty findings?
    - Is evidence cited in at least one phase entry?
    - Does a DEFINE phase entry exist?

    It does NOT check semantics: contradictions between findings, and whether
    the solution actually satisfies the Phase-1 definitions, are YOUR job in
    VALIDATE — re-read the DEFINE entry and compare, evidence line by line.

    Run this before declaring an investigation complete. If validation fails,
    loop back to ANALYSIS or EXPERIMENT phase to fill gaps.

    Args:
        project_path: Path to the project root (default: current directory).
        session_name: Session identifier (default: "default").
        original_definitions: The scope, terms, and success criteria from Phase 1.

    Returns validation results with pass/fail status and specific issues.
    """
    tracker = PhaseTracker(project_path, session_name)
    return tracker.validate_findings(original_definitions)
