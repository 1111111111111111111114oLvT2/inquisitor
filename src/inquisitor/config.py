import os
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


SESSION_DIR = Path(_env("INQUISITOR_SESSION_DIR", str(Path.home() / ".inquisitor" / "sessions")))

BRAVE_API_KEY = _env("BRAVE_API_KEY")
SEARXNG_URL = _env("SEARXNG_URL")

SEARCH_TIMEOUT = int(_env("INQUISITOR_SEARCH_TIMEOUT", "15"))
SEARCH_RETRIES = int(_env("INQUISITOR_SEARCH_RETRIES", "2"))
MAX_CONTENT_LENGTH = int(_env("INQUISITOR_MAX_CONTENT_LENGTH", "40000"))
DEFAULT_ENGINE = _env("INQUISITOR_DEFAULT_ENGINE", "ddg")

PREFERRED_DOMAINS = [d.strip() for d in _env("INQUISITOR_PREFERRED_DOMAINS").split(",") if d.strip()]

LOG_LEVEL = _env("INQUISITOR_LOG_LEVEL", "INFO")
