# Argus — agent for web penetration testing

Argus is an autonomous, LLM-driven agent for **authorized** web penetration
testing. You give it a target URL and a scope; it runs the assessment —
recon, surface mapping, hypothesis-driven probing, verification — and writes
an evidence-backed report. Built for real engagements: every finding must
cite verbatim bytes from a recorded request/response transcript.

```
pip install -e .            # one dependency: httpx
export ANTHROPIC_API_KEY=...
python -m argus run https://app.example --scope api.example \
    --header "Cookie: session=..." --goal "focus on /api"
```

The agent is **fully autonomous inside scope**. Scope itself is not a
suggestion — `argus/scope.py` refuses out-of-scope requests before they are
sent, and the model cannot widen it.

## Try it in 30 seconds (offline)

```bash
python lab/vulnapp.py 8777          # deliberately vulnerable app, stdlib only
python -m argus run http://127.0.0.1:8777 --goal "map and test everything"
python selftest.py                  # offline check, no API key needed
```

## Architecture

```
CLI (argus run)
  └── loop.py        messages -> Claude tool_use -> tool_result -> finish
      ├── system.py      the pentest operating contract
      ├── llm.py         Anthropic Messages API (httpx, retries, budgets)
      ├── tools/         the agent's hands (20 tools, JSON-schema'd)
      │   ├── web.py         http_request, crawl, js_recon, fingerprint
      │   ├── probes.py      matched-pair checks: sqli, time, ssti, lfi,
      │   │                  redirect, cors, methods, reflection
      │   └── analysis.py    jwt_decode, load_skill, notes, record_finding,
      │                      run_external (sqlmap/nuclei/nmap/ffuf), finish
      ├── scope.py       fail-closed host/path/private-IP guard
      ├── httpclient.py  one guarded client: scope + rate limit + transcript
      ├── session.py     evidence store: transcript.jsonl + findings.json
      ├── skills/        19 loadable methodology modules (sqli, ssrf, idor…)
      └── report/        report.md + summary.json, evidence embedded
```

## Design rules that make it usable

- **Evidence gate** — `record_finding` rejects any finding whose
  `evidence_excerpt` is not a verbatim substring of a cited recorded
  response. The agent cannot claim what it cannot quote.
- **Matched-pair probing** — `probe_*` tools always baseline-diff
  (true/false, benign/payload, controlled/uncontrolled URL). A single
  200 OK is never treated as signal.
- **Full transcript** — every request lands in `transcript.jsonl` with an
  id; reports embed the proving exchange under each finding.
- **Honesty under budget** — budgets (turns/requests/wall-clock) and a
  `note()` ledger keep the agent from payload-spamming one hypothesis.
- **Knowledge on demand** — `load_skill("sqli")` pulls one focused
  methodology module; the model never swallows a 600k-token corpus.

## Sessions

Each run writes `sessions/<ts>-<host>/`:

| file | content |
|---|---|
| `transcript.jsonl` | every request/response + tool events |
| `findings.json` | confirmed findings (evidence-gated) |
| `notes.md` | the agent's working reasoning |
| `report.md` | final human report, generated on finish |
| `summary.json` | machine-readable result |
| `agent.log` | tool calls + agent text, for audit |

## Authorization

Argus is for targets you are permitted to test: your own apps, labs, bug
bounties where automation is allowed, engagements with written scope.
Declare scope precisely (`--scope`, `--exclude`) — the guard enforces it
technically, but the legal obligation is yours.

See `docs/ARCHITECTURE.md` for the design and `docs/USAGE.md` for flags,
auth, external tools, and reading a report.
