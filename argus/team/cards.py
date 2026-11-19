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
        "graphql_introspect", "probe_disclosure",
        # The hybrid fan-out belongs to recon by definition: it runs the
        # scanners and hands back the shapes this role then writes a
        # wordlist from. A tool in the registry that no card grants is
        # unreachable in team mode, which is the same shape of missing as
        # one nothing imports.
        "recon_sweep",
        "run_external", "emit_lead", "finish",
    }),
    prompt_file="recon.md",
)

EXPLOIT = RoleCard(
    name="exploit",
    tools=_COMMON | frozenset({
        "pull_leads", "http_request", "probe_reflection", "probe_sqli",
        "probe_time", "probe_cmdi", "probe_ssti", "probe_lfi", "probe_redirect",
        "probe_cors", "probe_method", "probe_idor", "probe_ssrf",
        # The callback half belongs with the class it proves. A tool in the
        # registry that no card grants is unreachable in team mode - the
        # same shape of missing as a module nothing imports, and the second
        # time in this session that adding a tool stopped one step short.
        "probe_ssrf_oob",
        # The fan-out belongs to exploit by definition: recon finds the
        # endpoints, this works them. Third tool in this session, and the
        # first where the grant, the ledger attribution and the card were
        # done in the same edit as the registry entry instead of two gates
        # later.
        "fanout_sweep",
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
        "read_findings",
        # The view this role's job needs. `read_findings` is a dedup view
        # for workers deciding what to skip, and carries no evidence id, no
        # grade and no excerpt - so the role instructed by
        # `report-writing.md` that "every claim traces to an id" had no tool
        # that could show it one.
        "read_findings_full",
        "finish",
    }),
    prompt_file="report.md",
    turns=15,                 # report reads, summarizes, exits
)

LEAD = RoleCard(
    name="lead",
    tools=_COMMON | frozenset({
        "http_request", "fingerprint", "crawl", "js_recon",
        "spawn_worker", "list_workers", "read_findings",
        # the lead writes the executive summary when no report worker ran,
        # so it needs the same view for the same reason
        "read_findings_full",
        "emit_lead", "finish_engagement",
        # the ledger belongs to the role whose job is deciding what happens
        # next: it answers from recorded evidence rather than from the
        # conversation, which is what a coordinator needs - and which no
        # card granted to anyone, while the shared prompt told all four to
        # call it
        "next_action",
    }),
    prompt_file="lead.md",
    worker=False,
)

CARDS = {c.name: c for c in (RECON, EXPLOIT, REPORT, LEAD)}
