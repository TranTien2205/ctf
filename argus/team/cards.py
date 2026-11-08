"""Role cards: what a worker IS - its tools, budget defaults, and prompt.

A card is the unit of specialization: the lead spawns a worker by role, the
card decides which tools exist for that role (enforced in dispatch, not just
advertised in the schema list) and which role prompt is appended to the
shared system prompt.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROLES_DIR = Path(__file__).parent / "roles"


@dataclass(frozen=True)
class RoleCard:
    name: str
    tools: frozenset          # tool names this role may call
    prompt_file: str          # under roles/
    worker: bool = True       # False for the lead itself
    turns: int = 0            # per-worker turn cap; 0 = inherit --max-turns
    requests: int = 0         # per-worker request cap; 0 = inherit

    def prompt(self) -> str:
        path = ROLES_DIR / self.prompt_file
        return path.read_text(encoding="utf-8") if path.exists() else ""


_COMMON = frozenset({
    "note", "read_notes", "load_skill", "read_board", "post_board_note",
    "request_worker", "mcp_list", "mcp_call", "read_response",
    "read_findings",          # see what's already proven - don't retest it
})

RECON = RoleCard(
    name="recon",
    tools=_COMMON | frozenset({
        "http_request", "fingerprint", "crawl", "js_recon", "wordlist_fuzz",
        "run_external", "emit_lead", "finish",
    }),
    prompt_file="recon.md",
)

EXPLOIT = RoleCard(
    name="exploit",
    tools=_COMMON | frozenset({
        "pull_leads", "http_request", "probe_reflection", "probe_sqli",
        "probe_time", "probe_ssti", "probe_lfi", "probe_redirect",
        "probe_cors", "probe_method", "probe_idor", "probe_ssrf",
        "probe_xxe", "probe_csrf", "probe_xfh", "probe_nosqli",
        "probe_upload", "probe_race", "probe_deserialize", "probe_cache",
        "probe_ppoll", "probe_smuggle", "probe_disclosure", "probe_websocket",
        "probe_crlf", "probe_enum", "probe_lockout", "probe_massassign",
        "graphql_introspect", "jwt_decode", "jwt_forge", "run_external",
        "run_exploit", "list_exploits", "emit_lead", "record_finding", "finish",
    }),
    prompt_file="exploit.md",
)

REPORT = RoleCard(
    name="report",
    tools=_COMMON | frozenset({
        "read_findings", "finish",
    }),
    prompt_file="report.md",
    turns=15,                 # report reads, summarizes, exits
)

LEAD = RoleCard(
    name="lead",
    tools=_COMMON | frozenset({
        "http_request", "fingerprint", "crawl", "js_recon",
        "spawn_worker", "list_workers", "read_findings",
        "emit_lead", "finish_engagement",
    }),
    prompt_file="lead.md",
    worker=False,
)

CARDS = {c.name: c for c in (RECON, EXPLOIT, REPORT, LEAD)}
