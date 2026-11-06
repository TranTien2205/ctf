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
- `argus/httpclient.py` — the only socket; scope + rate + transcript
- `argus/session.py` — evidence store; findings need verbatim excerpts
- `argus/tools/` — tool schemas (registry.py) + implementations
- `argus/skills/*.md` — methodology modules loaded via `load_skill`
- `argus/report/` — report.md renderer
- `lab/`, `tests/`, `selftest.py`

## Rules for changes

- Every network request goes through `GuardedClient.send` — never open a
  socket elsewhere.
- Every tool must be registered in `tools/registry.py` (`_impl` + schema).
- New bug class → add `argus/skills/<name>.md` + INDEX row; keep the
  format: when / first probes / confirm / bypasses / falsifier / severity.
- Findings must keep the verbatim-evidence gate. Do not weaken it.
- No new runtime dependencies without strong cause — `httpx` is enough.
