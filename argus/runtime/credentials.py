"""Where a key comes from, in one place, with the surprising source opt-in.

Order:

1. the environment (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`,
   `GEMINI_API_KEY` / `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`)
2. `~/.config/argus/credentials.json`, `{"anthropic": "sk-...", ...}`
3. opencode's own `auth.json`, **only** when `ARGUS_USE_OPENCODE_AUTH=1`

The third is deliberately opt-in. Reading another tool's credential store
without being asked is the kind of convenience that should never be a default,
even for the person who owns both tools.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG = Path(os.environ.get("ARGUS_CONFIG_DIR", Path.home() / ".config" / "argus"))
CREDENTIALS_FILE = CONFIG / "credentials.json"
OPENCODE_AUTH = Path.home() / ".local" / "share" / "opencode" / "auth.json"

ENV_NAMES = {
    "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"),
    "openai": ("OPENAI_API_KEY",),
    "deepseek": ("DEEPSEEK_API_KEY",),
    "google": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "openrouter": ("OPENROUTER_API_KEY",),
}


def _from_file() -> dict:
    try:
        with open(CREDENTIALS_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
        return {str(k).lower(): str(v) for k, v in data.items() if isinstance(v, str)}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _from_opencode() -> dict:
    if os.environ.get("ARGUS_USE_OPENCODE_AUTH") != "1":
        return {}
    try:
        with open(OPENCODE_AUTH, encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    out = {}
    for provider, entry in (data or {}).items():
        if isinstance(entry, dict) and entry.get("type") == "api" and entry.get("key"):
            out[str(provider).lower()] = str(entry["key"])
    return out


def get(provider: str) -> str | None:
    provider = (provider or "").lower()
    for name in ENV_NAMES.get(provider, ()):
        if os.environ.get(name):
            return os.environ[name]
    stored = _from_file()
    if provider in stored:
        return stored[provider]
    return _from_opencode().get(provider)


def available() -> dict:
    """Which providers have a key, without printing any of them."""
    out = {}
    for provider in ("anthropic", "openai", "deepseek", "google", "openrouter"):
        key = get(provider)
        out[provider] = {"present": bool(key),
                         "source": _source(provider) if key else None}
    return out


def _source(provider: str) -> str:
    for name in ENV_NAMES.get(provider, ()):
        if os.environ.get(name):
            return f"env:{name}"
    if provider in _from_file():
        return f"file:{CREDENTIALS_FILE}"
    if provider in _from_opencode():
        return f"opencode:{OPENCODE_AUTH} (opt-in)"
    return "unknown"
