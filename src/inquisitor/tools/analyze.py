"""inquisitor_analyze tool — project structure overview."""

from inquisitor.backend import analyzer


def analyze(project_path: str | None = None) -> str:
    """Scan a project directory and return a structured overview.

    Shows: file tree, languages, frameworks, test structure,
    recent git history, and dependencies.

    Use this at the start of any investigation to understand the project landscape.
    Use during project setup to verify the scaffolded structure.

    Args:
        project_path: Path to the project root (default: current directory).

    Returns a formatted project overview.
    """
    return analyzer.analyze(project_path)
