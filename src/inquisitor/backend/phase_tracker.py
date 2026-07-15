"""Newton 7-phase state machine — tracks investigation progress.

Phases must be traversed in order:
  DEFINE → AXIOMS → ANALYSIS → EXPERIMENT → SYNTHESIS → VALIDATE → QUERY

Backed by SQLite. Each session is project-scoped by git root + session name.
"""

import sqlite3
import time
from pathlib import Path

PHASES = ["define", "axioms", "analysis", "experiment", "synthesis", "validate", "query"]
PHASE_ORDER = {p: i for i, p in enumerate(PHASES)}

NEXT_PHASE = {
    "define": "axioms",
    "axioms": "analysis",
    "analysis": "experiment",
    "experiment": "synthesis",
    "synthesis": "validate",
    "validate": "query",
    "query": None,
}


class PhaseTracker:
    """Manages Newton 7-phase state for an investigation session."""

    def __init__(self, project_path: str | None = None, session_name: str = "default"):
        import re

        from inquisitor.config import SESSION_DIR

        # security: sanitize session_name — it flows into a filename (path traversal)
        session_name = re.sub(r"[^A-Za-z0-9_-]", "_", session_name) or "default"

        root = Path(project_path).resolve() if project_path else Path.cwd().resolve()
        project_id = self._project_id(root)
        db_path = SESSION_DIR / f"{project_id}_{session_name}.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = sqlite3.connect(str(db_path))
        self._db.row_factory = sqlite3.Row
        self._init_schema()

    def _project_id(self, root: Path) -> str:
        """Create a stable project identifier from path."""
        import hashlib

        return hashlib.sha256(str(root).encode()).hexdigest()[:12]

    def _init_schema(self) -> None:
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS phase_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase TEXT NOT NULL,
                direction TEXT NOT NULL DEFAULT 'forward',
                timestamp REAL NOT NULL,
                findings TEXT DEFAULT '',
                evidence TEXT DEFAULT '',
                open_questions TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS current_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self._db.commit()

    def current_phase(self) -> str:
        row = self._db.execute(
            "SELECT value FROM current_state WHERE key = 'phase'"
        ).fetchone()
        return row["value"] if row else "define"

    def set_phase(self, target: str, findings: str = "", evidence: str = "", open_questions: str = "") -> str:
        """Advance to a target phase. Returns validation message."""
        target = target.lower().strip()
        if target not in PHASES:
            return f"Invalid phase: '{target}'. Valid phases: {', '.join(PHASES)}"

        current = self.current_phase()
        current_idx = PHASE_ORDER[current]
        target_idx = PHASE_ORDER[target]

        if target_idx < current_idx:
            direction = "backward"
        else:
            direction = "forward"

        self._db.execute(
            """INSERT INTO phase_log (phase, direction, timestamp, findings, evidence, open_questions)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (target, direction, time.time(), findings, evidence, open_questions),
        )
        self._db.execute(
            "INSERT OR REPLACE INTO current_state (key, value) VALUES ('phase', ?)",
            (target,),
        )
        self._db.commit()

        next_phase = NEXT_PHASE[target]
        msg = f"Phase advanced to: **{target.upper()}**"
        if next_phase:
            msg += f" → next: {next_phase.upper()}"
        else:
            msg += " (investigation complete)"
        return msg

    def summary(self) -> str:
        """Return a summary of the current investigation state."""
        phase = self.current_phase()
        rows = self._db.execute(
            "SELECT * FROM phase_log ORDER BY timestamp ASC"
        ).fetchall()

        lines = ["# Investigation Summary\n"]
        lines.append(f"**Current phase**: {phase.upper()}\n")

        for row in rows:
            lines.append(f"## Phase: {row['phase'].upper()}")
            if row["findings"]:
                lines.append(f"\nFindings:\n{row['findings']}")
            if row["evidence"]:
                lines.append(f"\nEvidence:\n{row['evidence']}")
            if row["open_questions"]:
                lines.append(f"\nOpen questions:\n{row['open_questions']}")
            lines.append("")

        lines.append(f"\n## Remaining phases: {', '.join(p.upper() for p in PHASES if PHASE_ORDER[p] > PHASE_ORDER[phase])}")
        lines.append(f"\n## Completed phases: {', '.join(p.upper() for p in PHASES if PHASE_ORDER[p] <= PHASE_ORDER[phase])}")

        return "\n".join(lines)

    def validate_findings(self, original_definitions: str = "") -> str:
        """Check current findings against Phase 1 definitions."""
        phase = self.current_phase()
        log = self._db.execute(
            "SELECT * FROM phase_log ORDER BY timestamp ASC"
        ).fetchall()

        lines = ["# Validation Results\n"]
        issues = 0

        # Check: do we have a DEFINE phase?
        define_phase = [r for r in log if r["phase"] == "define"]
        if not define_phase:
            lines.append("**Missing DEFINE phase**. No definitions recorded.")
            issues += 1
        elif original_definitions:
            lines.append("DEFINE phase exists.")

        # Check: each phase has findings
        for p in PHASES:
            if PHASE_ORDER[p] > PHASE_ORDER[phase]:
                continue
            p_log = [r for r in log if r["phase"] == p]
            if not p_log:
                lines.append(f"**No findings in {p.upper()} phase**.")
                issues += 1
                continue
            for entry in p_log:
                if not entry["findings"] and not entry["evidence"]:
                    lines.append(f"**Empty entry in {p.upper()} phase**.")
                    issues += 1

        # Check: evidence cited
        evidence_count = sum(1 for r in log if r["evidence"])
        if evidence_count == 0:
            lines.append("**No evidence cited** in any phase.")
            issues += 1
        else:
            lines.append(f"Evidence cited in {evidence_count} phase entries.")

        # Check: open questions in final phase
        query_phase = [r for r in log if r["phase"] == "query"]
        if phase == "query" and not query_phase:
            lines.append("QUERY phase reached but no entries yet.")

        if issues == 0:
            lines.insert(1, "All validations passed.\n")
        else:
            lines.insert(1, f"Found {issues} issue(s).\n")

        return "\n".join(lines)
