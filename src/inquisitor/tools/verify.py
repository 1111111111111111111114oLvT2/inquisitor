"""inquisitor_verify tool — validate findings against original definitions."""

from inquisitor.backend.phase_tracker import PhaseTracker


def verify(
    project_path: str | None = None,
    session_name: str = "default",
    original_definitions: str = "",
) -> str:
    """Validate investigation findings against the original problem definitions.

    Checks:
    - Were all phases completed with findings?
    - Is evidence cited for each finding?
    - Are there contradictions between findings?
    - Does the solution trace back to Phase 1 definitions?
    - Are open questions documented?

    Run this before declaring an investigation complete. If validation fails,
    loop back to ANALYSIS or EXPERIMENT phase to fill gaps.

    Use during Phase 6 (VALIDATE) to confirm readiness for Phase 7 (QUERY).
    Use before submitting code changes to ensure all claims are grounded.

    Args:
        project_path: Path to the project root (default: current directory).
        session_name: Session identifier (default: "default").
        original_definitions: The scope, terms, and success criteria from Phase 1.

    Returns validation results with pass/fail status and specific issues.
    """
    tracker = PhaseTracker(project_path, session_name)
    return tracker.validate_findings(original_definitions)
