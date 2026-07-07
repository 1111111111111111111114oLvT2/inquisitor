"""inquisitor_scaffold tool — interactive project setup."""

from inquisitor.backend import search as search_backend

TEMPLATES: dict[str, str] = {
    "python-cli": """# {name} — {description}

[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27.0"]

[project.scripts]
{name} = "{name}.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""",
    "fastapi": """# {name} — {description}

[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.110.0", "uvicorn>=0.29.0"]

[project.scripts]
dev = "uvicorn {name}.app:app --reload"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""",
}


def scaffold(project_type: str, requirements: list[str], output_path: str | None = None) -> str:
    """Set up a new project with best practices and minimal boilerplate.

    Before calling this, you MUST clarify with the user:
    - Project name and description
    - Language and framework choices
    - Required features (only what's asked — no speculation)
    - Constraints (existing codebase, CI, deployment targets)

    This tool generates the minimum viable scaffold. No unrequested configs,
    no speculative features, no boilerplate-for-later.

    Args:
        project_type: Type of project: "python-cli", "fastapi", "react", etc.
        requirements: List of requirements gathered from user.
        output_path: Where to create the project (default: current directory).

    Returns the scaffolded structure and next steps.
    """
    template = TEMPLATES.get(project_type)
    if not template:
        return f"Unknown project type: '{project_type}'. Available: {', '.join(TEMPLATES)}"

    lines = [
        f"# Scaffolding: {project_type}",
        f"\nRequirements: {', '.join(requirements)}",
        f"\nOutput path: {output_path or '<current directory>'}",
        "\n## Template",
        template.format(name="myproject", description="A new project"),
        "\n## Recommended best practices",
    ]

    try:
        results = search_backend.search(
            f"{project_type} project setup best practices 2025",
            max_results=5,
        )
        for i, r in enumerate(results.results, 1):
            lines.append(f"  [{i}] {r.title}: {r.url}")
    except Exception:
        lines.append("  (Search unavailable — using defaults)")

    lines.append("\n## Next Steps")
    lines.append("1. Review and customize the generated template")
    lines.append("2. Run `uv sync` or equivalent to install dependencies")
    lines.append("3. Run initial tests to verify setup")
    lines.append("4. Initialize git repository")

    return "\n".join(lines)
