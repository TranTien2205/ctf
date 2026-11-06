"""Configuration for an Argus run."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-4-5"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


@dataclass
class Config:
    target: str
    model: str = DEFAULT_MODEL
    api_key: str = ""
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

    def resolved_headers(self) -> dict[str, str]:
        base = {"User-Agent": "Argus/1.0 (authorized pentest)"}
        base.update(self.extra_headers)
        return base


def load_config(args) -> Config:
    """Build a Config from argparse args + environment."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
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
        api_key=getattr(args, "api_key", None) or api_key,
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
    )
