# Experiment protocol — single-agent vs team mode

Protocol for the evaluation chapter: run the same target under `run` and
`team`, collect the metrics `summary.json` already records, and compare with
`argus compare`. Repeatable and automatable.

## Setup

```bash
pip install -e .
export ANTHROPIC_API_KEY=...          # or rely on Claude Code OAuth
python lab/vulnapp.py 8777            # deterministic vulnerable app
```

Auth note: subscription OAuth bills to the account's "extra usage" pool
and caps per-request size — the full 54-tool schema (~30KB) may be
rejected there. For constrained auth, run `run` with
`--tools fingerprint,crawl,http_request,probe_sqli,probe_idor,probe_reflection,probe_disclosure,record_finding,note,load_skill,read_response`
or use `team` (role cards already subset tools per worker). Metered API
keys are unaffected.

The lab plants one bug per probe family (SQLi, NoSQLi, XSS, IDOR, SSRF,
XXE, CSRF, XFH/ACL-bypass, upload, race, deserialization, cache
poisoning+deception, prototype pollution, JWT weak secret, CORS,
open-redirect, CRLF, LFI, SSTI, time-based injection, request smuggling,
user-enum, login lockout, mass-assignment, GraphQL, WebSocket, info
disclosure, cross-site tracing via TRACE echo) plus recon surface (robots, .git, sourcemap, hidden routes).
Each run resets state at `make_server`.

## Procedure

For each configuration, run N identical trials (suggest N=5; LLM output is
non-deterministic, so report median):

```bash
# A: single agent
for i in 1 2 3 4 5; do
  python -m argus run http://127.0.0.1:8777 --allow-private \
      --goal "map the surface and confirm real vulnerabilities" \
      --max-turns 40 --session-dir "exp/single-$i" --quiet
done

# B: team (1 lead + 1 recon + 2 exploit)
for i in 1 2 3 4 5; do
  python -m argus team http://127.0.0.1:8777 --allow-private \
      --recon 1 --exploit 2 --session-dir "exp/team-$i" --quiet
done
```

## Metrics (all in `sessions/<run>/summary.json`)

| metric | meaning |
|---|---|
| `findings` (count) | evidence-gated findings recorded |
| `requests` | real wire requests spent (budget discipline) |
| `time_to_first_finding_s` | speed to first confirmed result |
| `coverage.endpoints` | endpoints touched (method+path+param names) |
| `coverage.probes` | probe families exercised |
| `llm_calls`, `llm_tokens` | cost — `in`/`out` are billed tokens; `cache_read`/`cache_write` show prompt-cached volume (~10% cost) |
| `agents` (team only) | per-worker turns/requests/tokens/findings |

## Compare

```bash
python -m argus compare exp/single-1/<dir> exp/team-1/<dir>
python -m argus compare --csv exp/single-*/2*/ exp/team-*/2*/   # N trials, one table
python -m argus sessions --session-dir exp/single-1
```

Report medians per configuration: findings count, requests, tokens,
time-to-first-finding, endpoints covered. The offline check
`python -m argus demo` / `demo --team` reproduces the pipeline shape without
spending tokens (5 seeded findings on both paths).

## Controls

- Same lab instance lifecycle per trial (fresh `vulnapp.py` port or a fresh
  `make_server`; counters/caches reset).
- Same `--goal`, `--max-turns`, `--rate`, `--max-requests` across A/B.
- Report findings as count AND categories found — the lab's planted classes
  are the recall denominator.
- Keep transcripts: they are the audit trail for every claimed finding.
  `python -m argus verify <dir>` proves the transcript was not altered,
  re-validates every finding's evidence against it, and recomputes the
  run-end `artifacts_digest` seal - a tampered `findings.json`,
  `meta.json`, `notes.md` or `summary.json` fails the check even when
  the chain itself is intact.
