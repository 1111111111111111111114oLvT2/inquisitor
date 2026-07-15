"""Project analyzer — scans a codebase and returns structured overview."""

import os
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    "target",
    "vendor",
}

LANGUAGE_DETECT = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".jsx": "JavaScript (React)",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++ Header",
    ".rb": "Ruby",
    ".php": "PHP",
    ".scala": "Scala",
    ".cs": "C#",
    ".fs": "F#",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".json": "JSON",
    ".md": "Markdown",
    ".css": "CSS",
    ".scss": "SCSS",
    ".html": "HTML",
}

FRAMEWORK_DETECT = {
    "fastapi": {
        "files": ["pyproject.toml", "requirements.txt", "setup.py"],
        "marker": "fastapi",
    },
    "flask": {
        "files": ["pyproject.toml", "requirements.txt", "setup.py"],
        "marker": "flask",
    },
    "django": {
        "files": ["pyproject.toml", "requirements.txt", "manage.py"],
        "marker": "django",
    },
    "next.js": {"files": ["package.json"], "marker": "next"},
    "react": {"files": ["package.json"], "marker": "react"},
    "vue": {"files": ["package.json"], "marker": "vue"},
    "express": {"files": ["package.json"], "marker": "express"},
    "fastify": {"files": ["package.json"], "marker": "fastify"},
}


def analyze(project_path: str | None = None) -> str:
    """Analyze a project directory and return a structured overview."""
    root = Path(project_path) if project_path else Path.cwd()
    if not root.exists():
        return f"Project path does not exist: {root}"

    lines: list[str] = [f"# Project Analysis: {root.name}\n"]

    lines.append(_tree_section(root))
    lines.append(_language_section(root))
    lines.append(_framework_section(root))
    lines.append(_test_section(root))
    lines.append(_git_section(root))
    lines.append(_dependency_section(root))

    return "\n".join(lines)


def _tree_section(root: Path) -> str:
    lines: list[str] = ["## File Tree (top-level)"]
    try:
        entries = sorted(root.iterdir())
    except PermissionError:
        return "## File Tree\n\nPermission denied.\n"

    for entry in entries:
        if entry.name.startswith(".") and entry.name not in (
            ".github",
            ".gitignore",
            ".env",
        ):
            continue
        if entry.is_dir():
            if entry.name in IGNORE_DIRS:
                continue
            lines.append(f"  {entry.name}/")
            try:
                children = sorted(entry.iterdir())
            except PermissionError:
                continue
            for child in children[:10]:
                suffix = "/" if child.is_dir() else ""
                lines.append(f"      {child.name}{suffix}")
            if len(children) > 10:
                lines.append(f"    ... ({len(children) - 10} more)")
        else:
            lines.append(f"  {entry.name}")

    return "\n".join(lines) + "\n"


def _language_section(root: Path) -> str:
    counts: dict[str, int] = {}
    total = 0

    for file in root.rglob("*"):
        if file.is_dir():
            continue
        part = str(file).split(os.sep)
        if any(ignored in part for ignored in IGNORE_DIRS):
            continue
        ext = file.suffix.lower()
        lang = LANGUAGE_DETECT.get(ext)
        if lang:
            counts[lang] = counts.get(lang, 0) + 1
            total += 1

    if not counts:
        return "## Languages\n\nNo source files detected.\n"

    lines = ["## Languages"]
    for lang, count in sorted(counts.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        lines.append(f"  {lang}: {count} files ({pct:.1f}%)")
    return "\n".join(lines) + "\n"


def _framework_section(root: Path) -> str:
    lines = ["## Frameworks & Tools"]
    found = False

    for fw_name, cfg in FRAMEWORK_DETECT.items():
        for fname in cfg["files"]:
            path = root / fname
            if path.exists():
                try:
                    content = path.read_text()
                except Exception:
                    continue
                if cfg["marker"].lower() in content.lower():
                    lines.append(f"  {fw_name}")
                    found = True
                    break

    if not found:
        lines.append("  No known framework detected.")

    return "\n".join(lines) + "\n"


def _test_section(root: Path) -> str:
    lines = ["## Test Structure"]
    test_dirs = ["tests", "test", "spec", "__tests__"]
    found = False

    for td in test_dirs:
        p = root / td
        if p.exists() and p.is_dir():
            test_count = sum(1 for _ in p.rglob("*.py")) + sum(1 for _ in p.rglob("*.ts")) + sum(1 for _ in p.rglob("*.js"))
            lines.append(f"  {td}/ ({test_count} test files)")
            found = True

    if not found:
        lines.append("  No test directory found.")

    for pattern in [
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "Makefile",
        "Makefile.am",
    ]:
        p = root / pattern
        if p.exists():
            content = p.read_text()
            for runner in ["pytest", "vitest", "jest", "mocha", "cargo test", "go test"]:
                if runner in content.lower():
                    lines.append(f"  Runner: {runner}")
            break

    return "\n".join(lines) + "\n"


def _git_section(root: Path) -> str:
    import subprocess

    git_dir = root / ".git"
    if not git_dir.exists():
        return "## Git\n\nNo git repository.\n"

    lines = ["## Recent Git History"]

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "20"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            for commit in result.stdout.strip().split("\n"):
                lines.append(f"  {commit}")
        else:
            lines.append("  No commits yet.")
    except Exception:
        lines.append("  Could not read git history.")

    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
            if branches:
                lines.append("\n  Branches:")
                for b in branches[:10]:
                    lines.append(f"    {b}")
    except Exception:
        pass

    return "\n".join(lines) + "\n"


def _dependency_section(root: Path) -> str:
    lines = ["## Dependencies"]

    dep_files = {
        "pyproject.toml": "Python",
        "requirements.txt": "Python",
        "package.json": "Node.js",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "Gemfile": "Ruby",
    }

    found = False
    for fname, lang in dep_files.items():
        path = root / fname
        if path.exists():
            lines.append(f"  {fname} ({lang})")
            found = True

    if not found:
        lines.append("  No dependency manifest found.")

    return "\n".join(lines) + "\n"
