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
    # `--policy` is recorded even when `--role` was not used, because team
    # mode reads it to pick a model per role
    policy: str = "cheap"
    role_models: bool = False
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
    # Strict admission: refuse a finding whose evidence does not meet the proof
    # requirement for its class. Off by default because a candidate is worth
    # recording and re-testing; on, the findings file holds only what was
    # proven, which is the condition an evaluation wants to be able to state.
    require_proof: bool = False
    # HMAC key for the transcript chain. Unkeyed, the chain proves the file was
    # not edited; keyed, it proves the run happened - only a holder of the key
    # can produce a chain that verifies. Never written to an artifact.
    seal_key: str = ""

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
        try:
            expires = int(oauth.get("expiresAt") or 0)
        except (TypeError, ValueError):
            expires = 0
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
        try:
            expires_in = int(fresh.get("expires_in") or 0)
        except (TypeError, ValueError):
            expires_in = 0
        if expires_in:
            oauth["expiresAt"] = int(time.time() * 1000) + expires_in * 1000
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
        for line in path.read_text(
                encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k in _DOTENV_ALLOWED and k not in os.environ:
                os.environ[k] = v
    except OSError:
        pass


def _validate_proxy(proxy: str) -> str:
    """Reject proxy URLs httpx would fail on at client init (ValueError
    traceback) or at connect time - an operator typo should be a clean
    startup error. socks5 is valid httpx but needs the 'socksio' extra
    which is not an Argus dependency."""
    if not proxy:
        return ""
    if proxy.startswith(("socks4://", "socks5://")):
        raise SystemExit(
            f"--proxy {proxy}: SOCKS needs httpx[socks] (socksio) - "
            "not an Argus dependency; use an http:// proxy")
    if not proxy.startswith(("http://", "https://")):
        raise SystemExit(
            f"--proxy {proxy!r}: expected http:// or https:// URL")
    return proxy


def _validate_resume(resume: str) -> str:
    """Fail fast on a --resume path that cannot be a session dir - a
    typo'd path currently surfaces as a FileNotFoundError traceback
    deep inside Session.__init__."""
    if not resume:
        return ""
    p = Path(resume)
    if not p.is_dir() or not (
            (p / "meta.json").is_file()
            or (p / "transcript.jsonl").is_file()):
        raise SystemExit(
            f"--resume {resume!r}: not a session dir "
            "(needs meta.json or transcript.jsonl)")
    return resume


def _validate_session_dir(p: Path) -> Path:
    """--session-dir pointing at an existing FILE surfaces as a
    FileExistsError traceback when the session dir is created."""
    if p.exists() and not p.is_dir():
        raise SystemExit(
            f"--session-dir {p}: exists and is not a directory")
    return p


def _resolve_model(args) -> str:
    """The model to run: an explicit name, or the table's pick for a role.

    `--role depth --policy cheap` is the point of the table: the operator says
    what the task needs and the cheapest model the table says can do it is
    chosen. An explicit `--model` always wins, because an operator naming a
    model has a reason the table does not know.
    """
    named = getattr(args, "model", None) or os.environ.get("ARGUS_MODEL", "")
    if named:
        return named
    role = str(getattr(args, "role", "") or "")
    if role:
        from . import models as models_mod
        pick = models_mod.for_role(
            role, str(getattr(args, "policy", "") or "cheap"))
        if pick is None:
            raise SystemExit(
                f"no model in models.json serves role {role!r}; roles are: "
                f"{', '.join(sorted(models_mod.roles()))}")
        return pick.key
    return DEFAULT_MODEL


def _seal_key(args) -> str:
    """The chain key, from --seal-key or ARGUS_SEAL_KEY. A path is read as a
    key file so the key need not appear in a process listing."""
    raw = str(getattr(args, "seal_key", "") or
              os.environ.get("ARGUS_SEAL_KEY", "") or "")
    if not raw:
        return ""
    candidate = Path(raw).expanduser()
    try:
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    return raw


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
                encoding="utf-8", errors="replace").splitlines()
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
                try:
                    h = urllib.parse.urlparse(h).hostname or h
                except ValueError:
                    raise SystemExit(f"invalid --scope entry {h!r}")
            scope_hosts.append(h)

    exclude_paths = []
    for p in (getattr(args, "exclude", None) or []):
        p = p.strip()
        if not p:
            continue
        exclude_paths.append(p if p.startswith("/") else "/" + p)

    import math
    # non-finite floats slip past '< 0' comparisons (nan < 0 is False) and
    # silently disable the cap the flag exists to set - reject them loud
    for flag, val in (("--rate", args.rate), ("--max-time", args.max_time)):
        if not math.isfinite(val):
            raise SystemExit(f"{flag} must be a finite number, got {val!r}")
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
        model=_resolve_model(args),
        policy=str(getattr(args, "policy", "") or "cheap"),
        role_models=bool(getattr(args, "role_models", False)),
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
        session_dir=_validate_session_dir(Path(args.session_dir)),
        scope_hosts=scope_hosts,
        exclude_paths=exclude_paths,
        allow_private=args.allow_private,
        tls_verify=args.tls_verify,
        extra_headers=headers,
        external_tools=not args.no_external,
        require_proof=bool(getattr(args, "require_proof", False)),
        seal_key=_seal_key(args),
        goal=getattr(args, "goal", "") or "",
        operator=getattr(args, "operator", "") or "",
        llm_max_tokens=args.llm_max_tokens,
        mcp_config=getattr(args, "mcp_config", "") or "",
        resume=_validate_resume(getattr(args, "resume", "") or ""),
        proxy=_validate_proxy(getattr(args, "proxy", "") or ""),
        # >=4 chars: a shorter 'secret' would redact innocent bytes all over
        # the transcript (the same floor is enforced in Session for direct
        # construction)
        secret_values=[
            s for s in (getattr(args, "secret", None) or [])
            + (os.environ.get("ARGUS_SECRETS") or "").split(";")
            if len(s) >= 4],
    )
