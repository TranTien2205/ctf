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
and caps per-request size — the full 55-tool schema (~32KB) may be
rejected there. For constrained auth, run `run` with
`--tools fingerprint,crawl,http_request,probe_sqli,probe_cmdi,probe_ssti,probe_lfi,probe_idor,probe_reflection,probe_disclosure,record_finding,note,load_skill,read_response`

`probe_cmdi` is in that list deliberately: the planted-class list below
includes OS command injection, so a subset without it makes the class
unreachable while still counting in the recall denominator.

**This subset is not a measurement configuration.** It reaches seven classes;
the other twenty-two have no probe in it. Use it only to get a constrained
account running, and when you do, narrow the denominator to the classes its
tools can reach - or the recall figure measures the subset, not the agent. For
a measured run pass no `--tools` at all, or use `team`, where the role cards
subset per worker rather than per run.
or use `team` (role cards already subset tools per worker). Metered API
keys are unaffected.

The lab plants one bug per probe family (SQLi, NoSQLi, XSS, IDOR, SSRF,
XXE, CSRF, XFH/ACL-bypass, upload, race, deserialization, cache
poisoning+deception, prototype pollution, JWT weak secret, CORS,
open-redirect, CRLF, LFI, SSTI, OS command injection, time-based injection,
request smuggling, user-enum, login lockout, mass-assignment, GraphQL,
WebSocket, info disclosure, cross-site tracing via TRACE echo) plus recon
surface (robots, .git, sourcemap, hidden routes). Each run resets state at
`make_server`.

`/ping` executes for real — argv through a seven-command allowlist, never a
shell, bound to loopback — so `id` returns the host's own identity line and
the rce class is provable end to end. A destructive payload comes back
"command not found", which is also what a hardened target looks like.

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
| `findings`, `counts` | evidence-gated findings (full list + per-severity counts) |
| `grades` | per-grade counts: `proven` / `candidate` / `unproven`. Report this beside `findings` — a configuration that records more findings at a lower proven rate is not better, and a count alone cannot show that |
| `requests` | real wire requests spent (budget discipline) |
| `duration_s` | wall-clock length of the run |
| `time_to_first_finding_s` | speed to first confirmed result |
| `coverage.endpoints` | endpoints touched (method+path+param names) |
| `coverage.probes` | probe families exercised |
| `coverage.requests_by_tool` | wire requests per tool — shows where budget went |
| `llm_calls`, `llm_tokens` | cost — `in`/`out` are billed tokens; `cache_read`/`cache_write` show prompt-cached volume (~10% cost) |
| `agents` (team only) | per-worker turns/requests/tokens/findings |
| `transcript_chain_head`, `sealed` | integrity anchors — the hash-chain head and the sealed-artifact list `argus verify` checks |

## Compare

```bash
python -m argus compare exp/single-1/<dir> exp/team-1/<dir>
python -m argus compare --csv exp/single-*/2*/ exp/team-*/2*/   # N trials, one table
python -m argus sessions --session-dir exp/single-1
```

Report medians per configuration: **proven** findings, candidates,
requests, tokens, time-to-first-finding, endpoints covered. Proven count is
the primary measure; total findings without the grade split invites a
configuration to win by recording more leads. The offline check
`python -m argus demo` / `demo --team` reproduces the pipeline shape without
spending tokens: 6 findings on both paths, 5 of them `proven` and one an
honest `candidate`. `argus compare` prints the grade split - report the
proven count, not the total.

## Controls

- Same lab instance lifecycle per trial (fresh `vulnapp.py` port or a fresh
  `make_server`; counters/caches reset).
- Same `--goal`, `--max-turns`, `--rate`, `--max-requests` across A/B.
- Report findings as count AND categories found — the lab's planted classes
  are the recall denominator — and split each by grade. A class found but
  left a candidate is a partial result; say so rather than scoring it as a
  hit or discarding it.
- **Nine classes cannot reach `proven` in this system at all**, by
  construction and by their own requirement sentences: `xss` and the
  client-side half of prototype pollution need a browser; `ssrf` needs an
  out-of-band collector; `enum` and `method` and `upload` and `crlf` and
  `websocket` and `smuggle` and `race` are measured here as a difference
  where the artifact is a count, a header, an execution or an ordering.
  `dos` is refused outright. Score those classes as found-as-candidate, and
  state the ceiling in the table - a recall figure that counts them in the
  denominator while they can only ever be candidates is measuring the
  system's honesty as if it were the agent's failure.
  `python -m argus proof` prints each one's requirement and says what would
  settle it.
- Run each arm a second time with `--require-proof` to get the strict-mode
  numbers. The two conditions answer different questions: the default
  measures what the agent noticed, strict measures what it finished.
- Keep transcripts: they are the audit trail for every claimed finding.
  `python -m argus verify <dir>` proves the transcript was not altered,
  re-validates every finding's evidence against it, and recomputes the
  run-end `artifacts_digest` seal - a tampered `findings.json`,
  `meta.json`, `notes.md` or `summary.json` fails the check even when
  the chain itself is intact.
