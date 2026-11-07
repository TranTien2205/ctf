# Usage

## Install

```bash
pip install -e .          # needs Python 3.10+, one dep: httpx
export ANTHROPIC_API_KEY=sk-ant-...
# optional: ANTHROPIC_BASE_URL for a gateway, ARGUS_MODEL to change default
```

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
| `--model` | `claude-sonnet-4-5` | any Anthropic model id |
| `--max-turns` | 80 | LLM tool-call turns |
| `--max-requests` | 400 | HTTP request budget |
| `--max-time` | 2400 | wall-clock seconds |
| `--rate` | 5 | requests/second cap |
| `--allow-private` | auto if target private | permit RFC1918/loopback |
| `--tls-verify` | off | verify certs (self-signed labs need off) |
| `--no-external` | off | disable sqlmap/nmap/nuclei/ffuf/curl |
| `--quiet` | off | suppress console trace |

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

## Resources

`resources/wordlists/<name>.txt` — wordlists for `wordlist_fuzz`; add a
file to add a list. `resources/exploits/<id>/` — PoC manifests
(`command`, `affects`, `proof_marker`) for `run_exploit`; add a directory
to add an exploit. Both are data, not code — extending coverage needs no
code change.

## Reading a run

```
sessions/20261106-101500-app.example/
  report.md        ← start here
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

`python -m argus findings <session_dir>` reprints the table;
`python -m argus report <session_dir>` re-renders `report.md`.

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
