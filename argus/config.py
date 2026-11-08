"""Configuration for an Argus run."""
from __future__ import annotations

import json
import os
import time
import urllib.parse
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
    operator: str = ""
    max_response_bytes: int = 200_000
    llm_max_tokens: int = 4096
    mcp_config: str = ""
    resume: str = ""
    proxy: str = ""
    # operator-declared credential values (login passwords, session tokens
    # typed by hand): redacted verbatim from every persisted artifact -
    # transcript bodies, event output, notes, logs - while the model still
    # sees the real bytes it needs to work
    secret_values: list[str] = field(default_factory=list)

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
        # atomic write: a crash mid-write would corrupt the user's
        # Claude Code credentials file; keep the original file mode so a
        # 0600 credentials file does not silently widen
        tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        try:
            os.chmod(tmp, path.stat().st_mode)
        except OSError:
            pass
        os.replace(tmp, path)
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


# .env may carry credentials and tuning - never trust-redirecting keys.
# ANTHROPIC_BASE_URL would send the API key to a hostile gateway, and
# ARGUS_MCP_CONFIG names subprocesses to run: a .env inside an untrusted
# project dir must not be able to set either.
_DOTENV_ALLOWED = {
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
    "ARGUS_MODEL", "ARGUS_SECRETS",
}


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Populate os.environ from a .env file (KEY=VALUE lines, # comments,
    optional quotes). Never overrides variables already set."""
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k in _DOTENV_ALLOWED and k not in os.environ:
                os.environ[k] = v
    except OSError:
        pass


def load_config(args) -> Config:
    """Build a Config from argparse args + environment."""
    _load_dotenv()
    api_key, auth_token = resolve_auth(args)
    api_base = os.environ.get("ANTHROPIC_BASE_URL", API_URL).rstrip("/") + "/messages" \
        if os.environ.get("ANTHROPIC_BASE_URL") else API_URL

    headers: dict[str, str] = {}
    header_lines: list[str] = []
    hf = getattr(args, "header_file", None)
    if hf:
        try:
            header_lines += [l.strip() for l in Path(hf).read_text(
                encoding="utf-8").splitlines()
                if l.strip() and not l.strip().startswith("#")]
        except OSError as exc:
            raise SystemExit(f"--header-file unreadable: {exc}")
    header_lines += list(getattr(args, "header", None) or [])
    # framing headers must stay wire-computed: a Burp-copied file always
    # carries Host:/Content-Length:, and honoring them would desync the wire
    # from what ScopeGuard checked (and break every request's framing)
    framing = {"host", "content-length", "transfer-encoding", "connection"}
    dropped = []
    for raw in header_lines:
        if ":" not in raw:
            raise SystemExit(f"--header must be 'Name: value', got: {raw!r}")
        name, value = raw.split(":", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            raise SystemExit(f"--header has an empty name: {raw!r}")
        # control chars would smuggle header lines onto the wire: httpx
        # validates at send time but send_raw concatenates its wire text
        # by hand, so a pasted 'X: a\r\nInjected: y' becomes real framing
        if any(ord(ch) < 32 or ord(ch) == 127 for ch in name + value):
            raise SystemExit(
                f"--header contains control characters: {raw!r}")
        if name.lower() in framing:
            dropped.append(name)
            continue
        headers[name] = value
    if dropped:
        import sys as _sys
        print(f"note: dropped framing header(s) {sorted(set(dropped))} - "
              "the wire computes them from the scoped URL", file=_sys.stderr)

    scope_hosts = []
    for raw in getattr(args, "scope", None) or []:
        for h in raw.split(","):
            h = h.strip().rstrip("/")
            if not h:
                continue
            # tolerate URLs and bare hosts alike: --scope api.example.com
            # and --scope https://api.example.com mean the same host
            if "://" in h:
                h = urllib.parse.urlparse(h).hostname or h
            scope_hosts.append(h)

    exclude_paths = []
    for p in (getattr(args, "exclude", None) or []):
        p = p.strip()
        if not p:
            continue
        exclude_paths.append(p if p.startswith("/") else "/" + p)

    if args.rate < 0:
        # a negative rate silently disables the safety cap (interval 0) -
        # a typo must fail loud, not turn the tool loose on the target
        raise SystemExit("--rate must be >= 0 (0 = no rate cap)")
    for flag, val in (("--max-turns", args.max_turns),
                      ("--max-requests", args.max_requests),
                      ("--max-time", args.max_time)):
        if val < 0:
            raise SystemExit(f"{flag} must be >= 0 (0 = no cap)")
    if getattr(args, "llm_max_tokens", 1) <= 0:
        raise SystemExit("--llm-max-tokens must be > 0")
    mc = getattr(args, "mcp_config", "") or os.environ.get(
        "ARGUS_MCP_CONFIG", "")
    if mc and not Path(mc).exists():
        raise SystemExit(f"MCP config not found: {mc}")
    return Config(
        target=args.target,
        model=getattr(args, "model", None) or os.environ.get("ARGUS_MODEL", DEFAULT_MODEL),
        api_key=api_key,
        auth_token=auth_token,
        api_base=api_base,
        # 0 means "no cap" (explicit operator choice), not "end instantly":
        # the loop compares turns>=max_turns so an unlimited value must be
        # a large number, not 0
        max_turns=args.max_turns if args.max_turns > 0 else 10**9,
        max_requests=args.max_requests if args.max_requests > 0 else 10**9,
        max_time_s=args.max_time if args.max_time > 0 else 10**12,
        rate_rps=args.rate,
        session_dir=Path(args.session_dir),
        scope_hosts=scope_hosts,
        exclude_paths=exclude_paths,
        allow_private=args.allow_private,
        tls_verify=args.tls_verify,
        extra_headers=headers,
        external_tools=not args.no_external,
        goal=getattr(args, "goal", "") or "",
        operator=getattr(args, "operator", "") or "",
        llm_max_tokens=args.llm_max_tokens,
        mcp_config=getattr(args, "mcp_config", "") or "",
        resume=getattr(args, "resume", "") or "",
        proxy=getattr(args, "proxy", "") or "",
        # >=4 chars: a shorter 'secret' would redact innocent bytes all over
        # the transcript (the same floor is enforced in Session for direct
        # construction)
        secret_values=[
            s for s in (getattr(args, "secret", None) or [])
            + (os.environ.get("ARGUS_SECRETS") or "").split(";")
            if len(s) >= 4],
    )
