"""Code path tracer — maps callers and callees for a symbol."""

import re
from pathlib import Path


def trace(
    symbol: str,
    project_path: str | None = None,
    direction: str = "both",
    max_depth: int = 2,
) -> str:
    """Trace a symbol through the codebase: find definition, callers, callees."""
    root = Path(project_path) if project_path else Path.cwd()
    if not root.exists():
        return f"Project path does not exist: {root}"

    definition = _find_definition(root, symbol)
    if not definition:
        return f"Symbol '{symbol}' not found in {root}"

    lines: list[str] = [f"# Trace: {symbol}\n"]
    lines.append(f"**Definition**: {definition['file']}:{definition['line']}\n")

    if direction in ("callers", "both"):
        callers = _find_callers(root, symbol, definition, max_depth)
        lines.append(f"## Callers ({len(callers)})\n")
        for c in callers:
            lines.append(f"  `{c['name']}` → {c['file']}:{c['line']}")

    if direction in ("callees", "both"):
        callees = _find_callees(definition)
        lines.append(f"\n## Callees ({len(callees)})\n")
        for c in callees:
            lines.append(f"  → `{c['name']}` at {c['file']}:{c['line']}")

    return "\n".join(lines)


def _find_definition(root: Path, symbol: str) -> dict | None:
    """Find the definition of a symbol in the codebase."""
    patterns = [
        rf"def\s+{re.escape(symbol)}\s*\(",     # Python function
        rf"class\s+{re.escape(symbol)}\s*[:(]",  # Python class
        rf"(async\s+)?function\s+{re.escape(symbol)}\s*\(",  # JS/TS function
        rf"(const|let|var)\s+{re.escape(symbol)}\s*=",       # JS/TS variable
        rf"fn\s+{re.escape(symbol)}\s*[<(]",    # Rust function
        rf"func\s+{re.escape(symbol)}\s*\(",    # Go function
        rf"export\s+(const\s+)?function\s+{re.escape(symbol)}\s*\(",  # JS export
        rf"export\s+(const|let|var)\s+{re.escape(symbol)}\s*=",
    ]

    extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".rb", ".java", ".kt", ".swift", ".cs", ".c", ".cpp", ".h"}

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() not in extensions:
            continue

        try:
            content = file.read_text()
        except Exception:
            continue

        for pat in patterns:
            m = re.search(pat, content)
            if m:
                line_no = content[: m.start()].count("\n") + 1
                return {
                    "name": symbol,
                    "file": str(file.relative_to(root)),
                    "line": line_no,
                    "content": content,
                }

    return None


def _find_callers(root: Path, symbol: str, definition: dict, max_depth: int) -> list[dict]:
    """Find all locations that call this symbol."""
    callers: list[dict] = []
    # ponytail: simple text search, add AST parsing if precision matters
    pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")

    extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".rb", ".java", ".kt", ".swift", ".cs"}

    for file in root.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() not in extensions:
            continue

        rel = str(file.relative_to(root))
        if rel == definition["file"]:
            continue

        try:
            content = file.read_text()
        except Exception:
            continue

        for m in pattern.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            callers.append({"name": symbol, "file": rel, "line": line_no})

    return callers[:30]  # ponytail: cap at 30, add pagination if needed


def _find_callees(definition: dict) -> list[dict]:
    """Find all functions/classes called within the definition's body."""
    callees: list[dict] = []

    # ponytail: function call pattern extraction, add cross-file resolution if needed
    try:
        content = definition["content"]
    except KeyError:
        return callees

    lines = content.split("\n")
    start = definition["line"] - 1
    # ponytail: rough scope detection based on indentation
    if start < 0:
        start = 0
    end = min(start + 60, len(lines))  # P10 Rule 4: max 60 lines per function

    body = "\n".join(lines[start:end])

    # Find function calls: name(args)
    call_pattern = re.compile(r"\b([a-zA-Z_]\w*)\s*\(")
    seen: set[str] = set()
    for m in call_pattern.finditer(body):
        name = m.group(1)
        if name in seen or name == definition["name"]:
            continue
        if name in {"if", "for", "while", "with", "print", "len", "range", "int", "str", "list", "dict", "set", "tuple"}:
            continue
        seen.add(name)
        callees.append({"name": name, "file": definition["file"], "line": -1})  # -1 = same file, not resolved

    return callees[:20]
