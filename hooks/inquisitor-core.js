#!/usr/bin/env node
// Inquisitor SessionStart hook: injects the always-on Core (skills/inquisitor/CORE.md)
// as hidden session context — the lightweight triage router + gate. The full
// 7-phase SKILL.md stays load-on-demand (CORE escalates to it only at Deep).
// Best-effort: any failure exits 0 so a session never fails to start.
const fs = require("fs");
const path = require("path");

let core;
try {
  core = fs.readFileSync(
    path.join(__dirname, "..", "skills", "inquisitor", "CORE.md"),
    "utf8",
  );
} catch {
  process.exit(0);
}

process.stdout.write(
  JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: core,
    },
  }),
);
