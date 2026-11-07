"""Configuration for an Argus run."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-5"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
OAUTH_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"
# Public client id used by the Claude Code CLI for token refresh.
OAUTH_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"


@dataclass
class Config:
    target: str
    model: str = DEFAULT_MODEL
    api_key: str = ""
    auth_token: str = ""
    api_base: str = API_URL
    max_turns: int = 80
    max_requests: int = 400
    max_time_s: float = 2400.0
    rate_rps: float = 5.0
    session_dir: Path = Path("sessions")
    scope_hosts: list[str] = field(default_factory=list)
    exclude_paths: list[str] = field(default_factory=list)
    allow_private: bool = False
    tls_verify: bool = False
    extra_headers: dict[str, str] = field(default_factory=dict)
    external_tools: bool = True
    goal: str = ""
    max_response_bytes: int = 200_000
    llm_max_tokens: int = 4096
    mcp_config: str = ""
    resume: str = ""

    def resolved_headers(self) -> dict[str, str]:
        base = {"User-Agent": "Argus/1.0 (authorized pentest)"}
        base.update(self.extra_headers)
        return base


def _claude_code_token() -> str:
    """OAuth token from Claude Code (Pro/Max subscription), refreshed if stale."""
    path = Path.home() / ".claude" / ".credentials.json"
    if not path.exists():
        return ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        oauth = data.get("claudeAiOauth") or {}
        token = oauth.get("accessToken") or ""
        expires = int(oauth.get("expiresAt") or 0)
        if token and expires > time.time() * 1000:
            return token
        refresh = oauth.get("refreshToken") or ""
        if not (token and refresh):
            return ""
        import urllib.request
        body = json.dumps({
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": OAUTH_CLIENT_ID,
        }).encode()
        resp = urllib.request.urlopen(urllib.request.Request(
            OAUTH_TOKEN_URL, data=body,
            headers={"content-type": "application/json"}), timeout=15)
        fresh = json.loads(resp.read())
        oauth["accessToken"] = fresh.get("access_token", token)
        oauth["refreshToken"] = fresh.get("refresh_token", refresh)
        if fresh.get("expires_in"):
            oauth["expiresAt"] = int(time.time() * 1000) + fresh["expires_in"] * 1000
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return oauth["accessToken"]
    except Exception:
        return ""


def _opencode_credential() -> tuple[str, str]:
    """(api_key, auth_token) from OpenCode's auth store."""
    candidates = [
        Path.home() / ".local" / "share" / "opencode" / "auth.json",
        Path(os.environ.get("LOCALAPPDATA", "")) / "opencode" / "auth.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            entry = (json.loads(path.read_text(encoding="utf-8")).get("anthropic") or {})
        except Exception:
            continue
        if entry.get("type") == "oauth" and entry.get("access"):
            return "", entry["access"]
        key = entry.get("key") or ""
        # OpenCode may store a gateway-scoped key rather than a raw
        # Anthropic key; only trust non-sk-ant keys when the user also
        # pointed the API base at a gateway.
        if key and (key.startswith("sk-ant-")
                    or os.environ.get("ANTHROPIC_BASE_URL")):
            return key, ""
    return "", ""


def resolve_auth(args) -> tuple[str, str]:
    """(api_key, auth_token) — first source wins: CLI arg, env, Claude Code, OpenCode."""
    key = getattr(args, "api_key", None) or os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key, ""
    token = (getattr(args, "auth_token", None)
             or os.environ.get("ANTHROPIC_AUTH_TOKEN")
             or os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
             or _claude_code_token())
    if token:
        return "", token
    return _opencode_credential()


def load_config(args) -> Config:
    """Build a Config from argparse args + environment."""
    api_key, auth_token = resolve_auth(args)
    api_base = os.environ.get("ANTHROPIC_BASE_URL", API_URL).rstrip("/") + "/messages" \
        if os.environ.get("ANTHROPIC_BASE_URL") else API_URL

    headers: dict[str, str] = {}
    for raw in getattr(args, "header", None) or []:
        if ":" not in raw:
            raise SystemExit(f"--header must be 'Name: value', got: {raw!r}")
        name, value = raw.split(":", 1)
        headers[name.strip()] = value.strip()

    scope_hosts = []
    for raw in getattr(args, "scope", None) or []:
        scope_hosts.extend(h.strip() for h in raw.split(",") if h.strip())

    return Config(
        target=args.target,
        model=getattr(args, "model", None) or os.environ.get("ARGUS_MODEL", DEFAULT_MODEL),
        api_key=api_key,
        auth_token=auth_token,
        api_base=api_base,
        max_turns=args.max_turns,
        max_requests=args.max_requests,
        max_time_s=args.max_time,
        rate_rps=args.rate,
        session_dir=Path(args.session_dir),
        scope_hosts=scope_hosts,
        exclude_paths=[p for p in (getattr(args, "exclude", None) or [])],
        allow_private=args.allow_private,
        tls_verify=args.tls_verify,
        extra_headers=headers,
        external_tools=not args.no_external,
        goal=getattr(args, "goal", "") or "",
        llm_max_tokens=args.llm_max_tokens,
        mcp_config=getattr(args, "mcp_config", "") or "",
        resume=getattr(args, "resume", "") or "",
    )
