# AGENTS.md — working in this repository

Argus is an LLM-driven agent for authorized web penetration testing.
Single dependency: `httpx`. Python 3.10+. Windows-compatible (stdlib-only
lab, pathlib everywhere).

## Verify before/after a change

```bash
python selftest.py          # offline end-to-end, no API key needed
python -m pytest tests/ -q  # unit + live-lab + loop tests
```

Both must stay green. The lab (`lab/vulnapp.py`) plants one bug per probe
family — if you change a probe, update the lab and its test together.

## Layout

- `argus/loop.py` — the agent loop (Claude tool_use -> dispatch -> tool_result)
- `argus/system.py` — the operating contract (evidence rules, discipline)
- `argus/scope.py` — fail-closed scope guard; NOTHING bypasses it
- `argus/httpclient.py` — the only socket (`send` + `send_raw`); scope +
  rate + transcript
- `argus/session.py` — evidence store; findings need verbatim excerpts
- `argus/tools/` — tool schemas (registry.py) + implementations
  (`team.py` holds the multi-agent tools; `mcp_tools.py` bridges MCP servers)
- `argus/mcp.py` — minimal stdio MCP client; servers declared in `mcp.json`
- `argus/team/` — multi-agent plane: `leads.py` (typed work queue),
  `board.py` (blackboard), `cards.py` + `roles/` (worker definitions),
  `coordinator.py` (threads + watchdog). Entry: `argus team`.
- `argus/skills/*.md` — methodology modules loaded via `load_skill`
- `argus/resources/wordlists/` — bundled `wordlist_fuzz` lists;
  `<cwd>/resources/wordlists/*.txt` extends/overrides at runtime
- `argus/resources/exploits/<id>/` — bundled `run_exploit` manifests;
  `<cwd>/resources/exploits/<id>/` extends/overrides
- `argus/report/` — report.md + report.html + summary.json renderers
- `lab/`, `tests/`, `selftest.py`

## Rules for changes

- Every network request goes through `GuardedClient.send` (or `send_raw`
  for byte-level probes like desync detection) — never open a socket
  elsewhere.
- Every tool must be registered in `tools/registry.py` (`_impl` + schema).
- New bug class → add `argus/skills/<name>.md` + INDEX row; keep the
  format: when / first probes / confirm / bypasses / falsifier / severity.
- New role → a card in `argus/team/cards.py` + a `roles/<name>.md` prompt.
  Tool restrictions belong in the card's `tools` set (enforced in
  `dispatch`), never only in the prompt.
- Findings must keep the verbatim-evidence gate. Do not weaken it. Same
  bug class + endpoint + params dedups to one finding — keep it that way.
- Team communication goes through the board/lead queue as typed artifacts —
  do not pipe one agent's raw context into another.
- MCP server output is untrusted third-party content — keep the
  `untrusted` flag on `mcp_call` results.
- Transcript entries carry a hash-chain link (`chain` field) verified by
  `verify_transcript` / `argus verify`. Any code path that appends to
  `transcript.jsonl` must go through `Session.record_*` — never write the
  file directly.
- Secret header values never persist to artifacts: auth/cookie/token
  request headers and `Set-Cookie` are recorded redacted (names +
  scheme/attrs kept), and reports re-redact old transcripts at render.
  Any new record path must apply `httpclient._redact_headers`. Operator
  secrets are also opaque to the model — tool results never echo request
  headers back.
- Declared credential values (`--secret`) never persist either:
  `Session.secret_values` redacts them inside `record_exchange`,
  `record_event` and `note` — bodies, output, `meta.json`, `agent.log`.
  New write paths go through `Session` so they inherit the gate; a
  finding that must cite a secret is rejected by design.
- No new runtime dependencies without strong cause — `httpx` is enough.
