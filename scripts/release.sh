#!/usr/bin/env bash
# Release inquisitor-mcp to PyPI, then register the new version with the MCP registry.
# Ordering matters: PyPI must be live before `mcp-publisher publish`, or the registry 404s.
set -euo pipefail
cd "$(dirname "$0")/.."

PKG="inquisitor-mcp"

# Version must match in all three places, or the registry validates the wrong artifact.
PYPROJECT_V=$(grep -m1 '^version = ' pyproject.toml | sed -E 's/.*"(.*)".*/\1/')
SERVER_VS=$(grep -oE '"version": "[^"]+"' server.json | sed -E 's/.*"([^"]+)"$/\1/' | sort -u)
if [[ "$SERVER_VS" != "$PYPROJECT_V" ]]; then
  echo "Version mismatch: pyproject=$PYPROJECT_V, server.json=[$SERVER_VS]. Fix before releasing." >&2
  exit 1
fi
V="$PYPROJECT_V"
echo "Releasing $PKG $V"

# Refuse to re-release an existing version (PyPI rejects overwrites; catch it early).
if curl -sf "https://pypi.org/pypi/$PKG/$V/json" >/dev/null 2>&1; then
  echo "$PKG $V is already on PyPI. Bump the version first." >&2
  exit 1
fi

rm -rf dist/
uv build
uv publish   # uses UV_PUBLISH_TOKEN or ~/.pypirc

echo "Waiting for PyPI to index $V ..."
for i in $(seq 1 30); do
  curl -sf "https://pypi.org/pypi/$PKG/$V/json?cb=$RANDOM$i" >/dev/null 2>&1 && break
  [[ $i == 30 ]] && { echo "$V never appeared on PyPI after 5min." >&2; exit 1; }
  sleep 10
done
echo "PyPI $V is live."

mcp-publisher publish
echo "Done: $PKG $V published to PyPI and the MCP registry."
