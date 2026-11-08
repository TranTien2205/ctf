# Argus — agent for web penetration testing

[![test](https://github.com/TranTien2205/ctf/actions/workflows/test.yml/badge.svg?branch=agent-v2)](https://github.com/TranTien2205/ctf/actions/workflows/test.yml)

Argus is an autonomous, LLM-driven agent for **authorized** web penetration
testing. You give it a target URL and a scope; it runs the assessment —
recon, surface mapping, hypothesis-driven probing, verification — and writes
an evidence-backed report. Built for real engagements: every finding must
cite verbatim bytes from a recorded request/response transcript.

```
pip install -e .            # one dependency: httpx
export ANTHROPIC_API_KEY=...       # or just sign in to Claude Code — see below
python -m argus run https://app.example --scope api.example \
    --header "Cookie: session=..." --goal "focus on /api"
```

**Auth — no API key required.** Argus picks the first available credential:
`--api-key`/`ANTHROPIC_API_KEY`, then `--auth-token`/`ANTHROPIC_AUTH_TOKEN`
(Claude Pro/Max OAuth), then a signed-in **Claude Code**
(`~/.claude/.credentials.json`, refreshed automatically), then **OpenCode**'s
auth store. If you can run `claude` or `opencode`, `argus` just works.
Calls are prompt-cached (the ~30KB tool schema + system prefix reads back
at ~10% cost per turn). On constrained OAuth tiers that cap per-request
size, `argus run --tools <comma-list>` shrinks the tool surface, or use
`team` — each role card already carries a smaller subset.

Or as a **team** — a lead agent coordinating role-specialized workers over a
shared, typed lead queue:

```
python -m argus team https://app.example --recon 1 --exploit 2
```

The agent is **fully autonomous inside scope**. Scope itself is not a
suggestion — `argus/scope.py` refuses out-of-scope requests before they are
sent, and the model cannot widen it.

## Try it in 30 seconds (offline)

```bash
python -m argus demo                # scripted full run on the lab - no API key
python selftest.py                  # offline check, no API key needed
# or point it at the lab yourself:
python lab/vulnapp.py 8777          # deliberately vulnerable app, stdlib only
python -m argus run http://127.0.0.1:8777 --goal "map and test everything"
```

## Architecture

### System diagram

```
                    ┌──────────────────────────────────────────┐
                    │                OPERATOR                  │
                    │   argus run <target> | argus team <t>    │
                    └─────────────────────┬────────────────────┘
                                          │
┌─────────────────────────────────────────▼─────────────────────┐
│                  LLM LAYER (Claude tool_use)                  │
│                                                               │
│   run mode:                                                   │
│   ┌─────────────────────────────────────────────────────┐     │
│   │ single AgentLoop: think -> tool_call -> observe     │     │
│   └─────────────────────────────────────────────────────┘     │
│                                                               │
│   team mode:                                                  │
│   ┌──────────┐  spawn/steer  ┌─────────┐                      │
│   │   LEAD   │──────────────▶│ workers │                      │
│   │strategist│◀────board─────┤ recon   │                      │
│   └──────────┘   requests    │ exploit │                      │
│                              │ report  │                      │
│                              └────┬────┘                      │
└───────────────────────────────────┼───────────────────────────┘
              emit_lead             │          pull_leads
        ┌───────────────────────────▼───────────────────────────┐
        │         SHARED BLACKBOARD  (team/board.py)            │
        │  LeadQueue: typed + deduped + prioritized leads       │
        │  notes · agent status · spawn requests · findings     │
        └───────────────────────────┬───────────────────────────┘
                                    │ dispatch (role-gated)
        ┌───────────────────────────▼───────────────────────────┐
        │              TOOL LAYER  (tools/registry.py)          │
        │                                                       │
        │  web.py      http_request · crawl · js_recon ·        │
        │              fingerprint · graphql_introspect         │
        │  probes.py   sqli · nosqli · time · ssti · lfi ·      │
        │              redirect · cors · method · reflection ·  │
        │              idor · ssrf · xxe · csrf · xfh ·         │
        │              upload · race · deserialize · cache ·    │
        │              ppoll · smuggle · disclosure · websocket │
        │              crlf · enum · lockout · massassign       │
        │  analysis.py jwt_decode · jwt_forge · load_skill ·    │
        │              notes · record_finding · run_external ·  │
        │              read_response · finish                   │
        │  mcp_tools.py  mcp_list · mcp_call (external servers) │
        │  team.py     emit_lead · pull_leads · board ·         │
        │              spawn_worker · wordlist_fuzz ·           │
        │              run_exploit                              │
        └───────────────────────────┬───────────────────────────┘
                                    │ every request funnels through
        ┌───────────────────────────▼───────────────────────────┐
        │            GuardedClient  (httpclient.py)             │
        │  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐  │
        │  │ ScopeGuard  │ │ RateLimiter  │ │  Transcript    │  │
        │  │ (fail-      │ │ (shared rps) │ │  recording     │  │
        │  │  closed)    │ │              │ │                │  │
        │  └─────────────┘ └──────────────┘ └────────────────┘  │
        └───────────────────────────┬───────────────────────────┘
                                    ▼
                          TARGET (in-scope only)
                                    │
        ┌───────────────────────────▼───────────────────────────┐
        │   SESSION OUTPUT  (sessions/<ts>-<host>/)             │
        │   transcript.jsonl · findings.json · notes.md ·       │
        │   report.md/.html · summary.json · agent.log          │
        └───────────────────────────────────────────────────────┘

        ┌───────────────────────────────────────────────────────┐
        │   RESOURCES (extend without code changes)             │
        │   <cwd>/resources/wordlists/*.txt   -> wordlist_fuzz  │
        │   <cwd>/resources/exploits/<id>/    -> run_exploit    │
        │   (bundled defaults: argus/resources/; cwd overrides) │
        │     manifest.json + script    (scope-checked,         │
        │                               timeout, proof_marker)  │
        └───────────────────────────────────────────────────────┘
```

### Data flow — a request never escapes the guardrails

```
agent proposes http_request {url, method}
        │
        ▼
dispatcher (role card allows this tool?)
        │
        ▼
ScopeGuard ── host in allowlist? path not excluded? private ok?
        │  (NO  -> request refused before it is sent)
        ▼
RateLimiter ── global rps budget shared by ALL workers
        │
        ▼
send + record -> transcript.jsonl (request_id)
        │
        ▼
response truncated, returned to agent as tool_result
        │
        ▼
record_finding {evidence_excerpt} -> verbatim substring check
against the recorded response -- otherwise rejected
```

### File map

```
CLI (argus run | argus team)
  ├── run:  loop.py     messages -> Claude tool_use -> tool_result -> finish
  │   ├── system.py      the pentest operating contract
  │   ├── llm.py         Anthropic Messages API (httpx, retries, budgets)
  │   ├── tools/         the agent's hands (JSON-schema'd)
  │   │   ├── web.py         http_request, crawl, js_recon, fingerprint,
  │   │   │                  graphql_introspect
  │   │   ├── probes.py      matched-pair checks: sqli, nosqli, time, ssti,
  │   │   │                  lfi, redirect, cors, methods, reflection, idor,
  │   │   │                  ssrf, xxe, csrf, xfh, upload, race, deserialize,
  │   │   │                  cache, prototype-pollution, request-smuggling
  │   │   │                  (CL.TE/TE.CL/obf raw sends), info-disclosure,
  │   │   │                  websocket, crlf, enum, lockout, mass-assign
  │   │   ├── analysis.py    jwt_decode, load_skill, notes, record_finding,
  │   │   │                  run_external (sqlmap/nuclei/nmap/ffuf), finish
  │   │   ├── mcp_tools.py   mcp_list, mcp_call -> external MCP servers
  │   │   └── team.py        emit_lead/pull_leads, board, spawn_worker,
  │   │                      wordlist_fuzz, run_exploit
  │   ├── mcp.py         minimal stdio MCP client (newline JSON-RPC)
  │   ├── scope.py       fail-closed host/path/private-IP guard
  │   ├── httpclient.py  one guarded client: scope + rate limit + transcript
  │   ├── session.py     evidence store: transcript.jsonl + findings.json
  │   ├── skills/        27 loadable methodology modules (sqli, ssrf, idor…)
  │   └── report/        report.md + .html + .sarif + summary.json,
  │                      CWE/OWASP mapped, evidence embedded
  │
  └── team: team/coordinator.py   lead + role workers on shared infra
      ├── leads.py       typed, deduped, prioritized work queue
      ├── board.py       the blackboard: leads, notes, agents, requests
      ├── cards.py       role = tool subset + prompt + spawnability
      └── roles/*.md     lead / recon / exploit / report contracts
```

Team mode streams work: recon `emit_lead`s the moment surface is found,
exploit workers `pull_leads` and verify in parallel — the pipeline never
waits for recon to finish. Workers share ONE scope guard, rate limiter and
transcript; role cards restrict each worker's toolset at the dispatcher,
not just in the prompt.

## Design rules that make it usable

- **Evidence gate** — `record_finding` rejects any finding whose
  `evidence_excerpt` is not a verbatim substring of a cited recorded
  response. The agent cannot claim what it cannot quote.
- **Matched-pair probing** — `probe_*` tools always baseline-diff
  (true/false, benign/payload, controlled/uncontrolled URL). A single
  200 OK is never treated as signal.
- **Full transcript** — every request lands in `transcript.jsonl` with an
  id; reports embed the proving exchange under each finding. Each entry
  carries a hash-chain link, so `argus verify <session>` can prove nothing
  was edited or deleted after the run — it also re-validates every finding
  against the chained transcript, catching edited findings.json too.
- **Scope-checked findings** — `record_finding` runs the finding URL
  through the scope guard, so the report cannot claim a bug on a host the
  engagement never authorized.
- **Honesty under budget** — budgets (turns/requests/wall-clock) and a
  `note()` ledger keep the agent from payload-spamming one hypothesis.
- **Knowledge on demand** — `load_skill("sqli")` pulls one focused
  methodology module; the model never swallows a 600k-token corpus.
- **Extensible resources** — drop files into `resources/` in your working
  directory (or extend the bundled `argus/resources/`):
  `resources/wordlists/*.txt` feeds `wordlist_fuzz`;
  `resources/exploits/<id>/manifest.json` describes a PoC
  script (command template, affected fingerprints, `proof_marker` regex)
  that `run_exploit` executes scope-checked and timeout-bounded.
- **Findings dedup** — the same bug class on the same endpoint+params can
  only be recorded once (per-category normalization), even across workers.
- **Per-agent metrics** — `summary.json` carries per-worker
  turns/requests/tokens/LLM-calls/findings plus `time_to_first_finding_s`,
  so `run` vs `team` can be compared on speed, coverage and cost.

## MCP tool servers (optional)

Argus can call external MCP (Model Context Protocol) servers — search,
fetchers, CVE databases — through `mcp_list` / `mcp_call`. Declare them in
`mcp.json` (or `--mcp-config` / `ARGUS_MCP_CONFIG`):

```json
{"servers": {
  "search": {"command": ["npx", "-y", "some-search-mcp"],
             "env": {"API_KEY": "..."}},
  "cvelist": {"command": ["python", "tools/cve_server.py"]}
}}
```

Each server is spawned lazily on first call and shared by every worker.
Output is marked untrusted and recorded as an `mcp_call` transcript event —
data to analyze, never instructions to follow.

## Sessions

Each run writes `sessions/<ts>-<host>/`:

| file | content |
|---|---|
| `transcript.jsonl` | every request/response + tool events (operator
secrets redacted: auth/cookie/token headers keep names, not values) |
| `findings.json` | confirmed findings (evidence-gated, deduped) |
| `notes.md` | the agent's working reasoning |
| `report.md` | final human report, generated on finish |
| `report.html` | the same report styled for browsers/slides |
| `report.sarif` | SARIF 2.1.0 for CI/GitHub code scanning |
| `summary.json` | machine-readable result |
| `agent.log` | tool calls + agent text, for audit |

## Authorization

Argus is for targets you are permitted to test: your own apps, labs, bug
bounties where automation is allowed, engagements with written scope.
Declare scope precisely (`--scope`, `--exclude`) — the guard enforces it
technically, but the legal obligation is yours.

See `docs/ARCHITECTURE.md` for the design, `docs/USAGE.md` for flags,
auth, external tools, and reading a report, and `docs/EXPERIMENTS.md` for
the run-vs-team evaluation protocol.
