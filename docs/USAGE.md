# Usage

## Install

```bash
pip install -e .          # needs Python 3.10+, one dep: httpx
export ANTHROPIC_API_KEY=sk-ant-...
# optional: ANTHROPIC_BASE_URL for a gateway, ARGUS_MODEL to change default
```

## Credentials

Checked in this order - first hit wins:

1. `--api-key` / `ANTHROPIC_API_KEY` - direct API key (metered billing)
2. `--auth-token` / `ANTHROPIC_AUTH_TOKEN` / `CLAUDE_CODE_OAUTH_TOKEN`
3. Claude Code OAuth store `~/.claude/.credentials.json` - your Pro/Max
   subscription, refreshed automatically when stale
4. OpenCode auth store (`~/.local/share/opencode/auth.json` or
   `%LOCALAPPDATA%\opencode\auth.json`)

`python -m argus check` performs a real tiny API call and tells you which
source resolved. Note: OAuth (subscription) auth bills calls to your
account's "extra usage" budget, not plan limits - on a constrained
account the full 54-tool schema may be rejected (`--tools` shrinks it;
team mode splits tools across role cards and fits under the cap).

## Run

```bash
python -m argus run https://app.example
python -m argus run https://app.example \
    --scope api.example,cdn.example \   # extra in-scope hosts
    --exclude /logout --exclude /admin/reset \
    --header "Cookie: session=abc" \    # auth'd session (repeatable)
    --header "Authorization: Bearer x" \
    --goal "prioritize /api and the checkout flow" \
    --rate 3 --max-requests 600 --max-time 3600
```

| Flag | Default | Meaning |
|---|---|---|
| `--scope` | target host only | extra allowed hosts; subdomains included |
| `--exclude` | none | path prefixes never touched |
| `--header` | none | applied to every request (auth, custom UA) |
| `--header-file` | none | headers from a file, one `Name: value` per line (Burp copy) |
| `--model` | `claude-sonnet-4-5` | any Anthropic model id |
| `--max-turns` | 80 | LLM tool-call turns |
| `--max-requests` | 400 | HTTP request budget |
| `--max-time` | 2400 | wall-clock seconds |
| `--rate` | 5 | requests/second cap |
| `--goal` | full assessment | operator goal, injected into the system contract |
| `--operator` | none | tester/org attribution written into meta + reports |
| `--proxy` | none | route via Burp/ZAP for inspection |
| `--llm-max-tokens` | 4096 | per-call response cap for the LLM |
| `--mcp-config` | none | extra MCP servers config file |
| `--tools` | all | `run` only: comma tool allowlist (finish always included) — shrinks the per-call schema payload, needed when auth rejects large requests |
| `--resume` | none | session dir to continue from |
| `--allow-private` | auto if target private | permit RFC1918/loopback |
| `--tls-verify` | off | verify certs (self-signed labs need off) |
| `--no-external` | off | disable sqlmap/nmap/nuclei/ffuf/curl |
| `--quiet` | off | suppress console trace |

## Offline demo

```bash
python -m argus check         # preflight: verify auth before a real run
python -m argus demo          # scripted run on the bundled lab, no API key
python -m argus demo --team   # same, through the lead/worker pipeline
```

Spins up `lab/vulnapp.py`, runs a canned probe sequence through the real
agent loop, and lands four evidence-gated findings (SQLi, XSS, IDOR,
info-disclosure) in a
normal session dir - use it to demo the pipeline at a defense without
spending tokens. `--team` runs the same assessment through TeamRun: a lead
seeds the lead queue, a recon worker maps the surface, and an exploit worker
pulls and verifies each lead, so the whole multi-agent flow is visible.

## Team mode

```bash
python -m argus team https://app.example \
    --recon 1 --exploit 2 --max-workers 6 \
    --goal "focus on /api" --rate 3
```

A lead agent steers role workers over a shared board: recon emits typed
leads the moment it finds surface, exploit workers pull and verify them in
parallel, and the lead spawns more workers (or a report writer) as needed.
All `run` flags apply; per-worker turn/request budgets come from
`--max-turns`/`--max-requests`, and `--max-time` bounds the engagement.

Team-only flags:

| Flag | Default | Meaning |
|---|---|---|
| `--recon` | 1 | initial recon workers |
| `--exploit` | 1 | initial exploit workers |
| `--report-workers` | 0 | report writers at start (the lead can still spawn one) |
| `--max-workers` | 6 | concurrent worker cap |

The session dir gains `agent-<name>.log` per member plus the shared
`transcript.jsonl` (each entry tagged with its agent), `findings.json`,
and `report.md`.

## Probe coverage

Every probe baseline-diffs or uses a matched pair — the verdict is a
signal to verify, never a declared bug. `record_finding` still requires
verbatim evidence from a cited response.

| Bug class | Tool | Detection approach |
|---|---|---|
| Reflected XSS | `probe_reflection` | canary reflection, context detection |
| SQL injection | `probe_sqli` | AND/OR pairs quoted+numeric, error/xpath exfil, opt-in UNION col count |
| NoSQL injection | `probe_nosqli` | `$ne`/`$gt`/`$regex` JSON + urlencoded `param[$op]` carrier |
| Command injection | `probe_time` | sleep separators vs measured baseline latency |
| SSTI | `probe_ssti` | `{{7*7}}`-family eval per engine syntax |
| File read / LFI | `probe_lfi` | traversal/absolute/encoded/null-byte + `file://`, `php://filter` decode |
| Open redirect | `probe_redirect` | canonical + //host, backslash, userinfo, suffix-confuse; meta/JS hops |
| CORS | `probe_cors` | foreign/null/subdomain/prefix origins x credentials flag |
| HTTP methods | `probe_method` | OPTIONS + PUT canary/cleanup + TRACE echo check |
| IDOR | `probe_idor` | id +/-1 and id=0 in path/query/JSON body |
| SSRF | `probe_ssrf` | self-fetch + short/decimal/hex/octal/ipv6 encodings + metadata |
| XXE | `probe_xxe` | external entity file/http resolution |
| CSRF | `probe_csrf` | token/SameSite audit + `text/plain` replay + GET state-change leads |
| Host-header | `probe_xfh` | XFH canary + X-Original-URL/X-Rewrite-URL ACL bypass |
| File upload | `probe_upload` | php/phtml/jsp/aspx/svg/htaccess/double-ext/spoof/traversal, served check |
| Race condition | `probe_race` | concurrent burst + serial baseline + overlap check |
| Deserialization | `probe_deserialize` | java/php/pickle/node/yaml/dotnet/ruby magic bytes vs parser errors |
| Cache poisoning | `probe_cache` | unkeyed XFH poison + .css-suffix deception path confusion |
| Prototype pollution | `probe_ppoll` | `__proto__` + `constructor.prototype` carriers, cross-object read |
| Request smuggling | `probe_smuggle` | CL.TE + TE.CL + obfuscated-TE raw sends; 'G'/'GPOST' poison own next request only |
| Info disclosure | `probe_disclosure` | sensitive-path sweep w/ artifact signatures |
| WebSocket | `probe_websocket` | RFC 6455 upgrade handshake (101 + accept check) |
| CRLF/response split | `probe_crlf` | CRLF canary in header-context params (redirect/cookie) |
| User enumeration | `probe_enum` | bogus vs real usernames - error text/status + timing differential |
| Login rate-limit | `probe_lockout` | bounded bad-cred burst: 429/lockout text/latency = throttled |
| Mass assignment | `probe_massassign` | injected privilege fields echoed/stored = server binds untrusted input |
| JWT/session | `jwt_decode`, `jwt_forge` | decode, alg weaknesses, weak-secret crack, forge+verify chain |
| GraphQL | `graphql_introspect` | POST introspection + GET ?query= fallback |
| Recon | `fingerprint` `crawl` `js_recon` `wordlist_fuzz` | stack/links/forms/endpoints/secrets/sourcemaps |

Methodology-only classes (auth-session flows, logic flaws, triage order)
are covered by `load_skill` modules rather than a fixed probe.

Utility tools: `read_response` re-reads any recorded response (or external
tool output) from the transcript — bodies are stored at 200k chars while
tool results truncate at 12k, so long pages are paged through here instead
of re-requested. `note`/`read_notes` keep the working narrative.

## Resources

`resources/wordlists/<name>.txt` — wordlists for `wordlist_fuzz` (path/param/POST-body modes); add a
file to add a list. `resources/exploits/<id>/` — PoC manifests
(`command`, `affects`, `proof_marker`) for `run_exploit`; add a directory
to add an exploit. Both are data, not code — extending coverage needs no
code change. Lookup order is `resources/` in your working directory first,
then the bundled `argus/resources/` (a cwd file shadows a bundled one),
so the same mechanism works from a pip-installed `argus`.

## Reading a run

```
sessions/20261106-101500-app.example/
  report.md        ← start here
  report.html      ← same report for browsers/slides
  report.sarif     ← SARIF 2.1.0: upload to GitHub code scanning / CI
  findings.json    ← same data, machine-readable
  transcript.jsonl ← every request/response, cited by request_id
  notes.md         ← the agent's working reasoning
  agent.log        ← tool calls and agent text
  summary.json     ← counts, severities, per-agent metrics,
                     time_to_first_finding_s, llm token totals
```

In team mode `summary.json` also carries `agents` — each worker's turns,
requests, LLM calls, token usage and credited findings — the data needed to
compare `run` vs `team` on speed, coverage and cost.

Each finding carries `severity`, optional `cvss`, and an auto-mapped `cwe`
(the named bug class resolves to the canonical CWE identifier, e.g.
`sqli` -> CWE-89; unknown categories simply omit it), plus verbatim
`evidence_excerpt` and cited `evidence_ids`.

`python -m argus findings <session_dir>` reprints the table;
`python -m argus report <session_dir>` re-renders `report.md`;
`python -m argus sessions` lists every session dir with mode, finding and
request counts (`--json` for scripts); `python -m argus compare <dirA> <dirB>`
prints a side-by-side metrics table (mode, findings, requests,
time-to-first-finding, endpoints touched, llm calls, workers, tokens
incl. cache read/write) for run-vs-team experiments.
`python -m argus skills` lists the bundled methodology modules;
`python -m argus skills <name>` prints one, which is useful when auditing
exactly what guidance the model loads.

Every `transcript.jsonl` entry carries a `chain` field - a sha256 hash of
the previous entry's link plus the entry itself, so edits, insertions and
mid-file deletions are detectable after the fact. `python -m argus verify
<session_dir>` recomputes the chain and reports any mismatch; `summary.json`
anchors the last link, so even tail truncation is caught once a report has
been rendered (a mismatch there means truncation OR post-report appends).
`findings.json` is not chained itself, so verify also re-validates every
recorded finding against the immutable transcript: edited excerpts or
invented evidence ids surface as `TAMPERED: findings [...]`.

## Resuming a run

`--resume <session_dir>` continues an earlier session: transcript,
findings, request ids and finding ids all carry over, so the evidence
chain and findings dedup stay intact across the boundary. The new seed
lists prior findings so the agent builds on them instead of re-verifying.
Works for both `run` and `team`.

## External tools

If installed, the agent may call `sqlmap`, `nuclei`, `nmap`, `ffuf`, `curl`
through `run_external` — args are scope-checked, runs are timeout-bounded
(≤600s), output is truncated. Scanner claims are treated as *leads*: the
agent must reproduce the issue via `http_request` to record a finding.

Some flags are refused outright (the full table is in
`docs/ARCHITECTURE.md` → *Threat model*): local-file reads (`curl -d/-F/-b/-T`,
`ffuf -w` outside `resources/wordlists`), config injection (`curl -K`,
`sqlmap -c`), connection redirection (`--resolve`, `--connect-to`,
proxies), target lists inside files (`nmap -iL`, `sqlmap -r`, nuclei `-l`
— the hosts *inside* the file are scope-checked), local code exec
(`sqlmap --eval`, `nmap --script <path>`), and file writes outside the
working directory. If a run is refused, pick the in-scope equivalent —
e.g. `-b name=value` instead of a cookie-jar path.

## MCP tool servers

`mcp_list` / `mcp_call` bridge external MCP servers (search, fetch, CVE
data) declared in `mcp.json`, `--mcp-config`, or `ARGUS_MCP_CONFIG`:

```json
{"servers": {"search": {"command": ["npx", "-y", "some-search-mcp"]}}}
```

Servers spawn lazily, one subprocess each, shared across workers. Output is
flagged untrusted and logged as `mcp_call` transcript events.

## The lab

`lab/vulnapp.py` is a stdlib-only vulnerable app planting one bug per probe
family (XSS, SQLi error+bool, auth bypass, cmd injection, SSTI, LFI, open
redirect, IDOR, bad CORS, weak JWT, .git disclosure). It's the fastest way
to evaluate whether the agent finds what it should:

```bash
python lab/vulnapp.py 8777
python -m argus run http://127.0.0.1:8777
```

`python selftest.py` does the whole thing offline with a scripted model —
useful in CI or to verify a fresh checkout without an API key.

## Interpreting severity

The agent is instructed to rate honestly: confirmed RCE / auth bypass /
sensitive data read → high-critical; verified primitives with unclear
reach → medium; hygiene issues → low/info. A finding only exists if the
excerpt proving it is inside a recorded response — if `report.md` says
it, `transcript.jsonl` shows it.
