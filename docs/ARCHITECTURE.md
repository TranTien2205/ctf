# Argus architecture

One file is the spec: `argus/loop.py` drives the loop; everything else is a
tool, a guard, or a store.

## The loop

```
seed (target + goal + auth context + scope description)
   │
   ▼
ClaudeClient.chat(messages, TOOL_SCHEMAS, system)   ← Anthropic tool_use API
   │
   ├─ text blocks   → logged to agent.log (reasoning trace)
   └─ tool_use      → dispatch(ctx, name, args)
                        │
                        ├─ ScopeGuard.check(url)     ← hard boundary
                        ├─ RateLimiter.wait()
                        ├─ GuardedClient.send/raw()  ← the ONLY socket
                        └─ Session.record_exchange() ← evidence, r<n> id
                     result → tool_result → next turn
   │
   └─ finish(summary) or budget exhausted → report/markdown.py
```

Design choices and why:

- **Tool-calling, not free-text parsing.** Claude's `tool_use` gives typed,
  schema-validated calls; the loop never regexes commands out of prose.
- **One guarded client.** Every tool — `http_request`, `crawl`, probes,
  even `run_external` arg checking — funnels through `ScopeGuard` +
  `RateLimiter` + transcript recording. No tool opens its own socket;
  desync probes that httpx cannot express go through
  `GuardedClient.send_raw`, which keeps the same scope/budget/transcript
  guarantees on a controlled raw channel.
- **Evidence gating at write time.** `Session.add_finding` asserts the
  excerpt is a substring of a cited response. Same idea as a flag gate,
  generalized: the machine validates the *truth* of a claim, not its shape.
- **Baseline-diffed probes.** Each `probe_*` returns `verdict` +
  `request_ids`, never "you are vulnerable". The agent confirms and
  rates severity itself.
- **Skills as retrievable knowledge.** 27 methodology modules (~2KB each)
  load on demand via `load_skill`. Detection signals, first probes,
  confirmation criteria, bypasses, honest severity guidance.
- **Budget-aware autonomy.** max_turns / max_requests / max_time are real
  limits; the loop warns once near ~80% ("record now, prioritize"), nudges
  once at exhaustion, then stops. Measured on a real run: the early
  warning turned a deferred-finding loss into a 5x recording rate.
- **Cost-aware LLM calls.** `ClaudeClient` marks the static prefix
  (system + tools + conversation tail) with ephemeral cache breakpoints —
  billed input drops ~90% on cache hits. A 400 mentioning cache disables
  it transparently. The full 54-tool schema is ~30KB/call, so constrained
  auth paths can pass `--tools` (run) or rely on role-card subsets (team).
- **Bounded context.** Tool results older than the last 8 result-messages
  compact to a stub naming their request_ids (re-inspect via
  `read_response`), so an 80-turn run cannot silently overrun the context
  window.

## Trust boundaries

- The **model** can only act through tools; it cannot widen scope, spend
  past budgets, or write findings without verbatim evidence.
- The **transcript** is append-only JSONL; findings reference it by id.
  Each entry carries a hash-chain link and `summary.json` anchors the
  final link, so post-run edits, insertions and deletions are detectable
  with `argus verify`.
- **Web content is untrusted data.** The system prompt teaches the model
  to treat in-page instructions as prompt-injection attempts and keep
  working the assessment. MCP server output gets the same treatment —
  `mcp_call` results are flagged `untrusted` and logged as transcript
  events.

## Threat model (what each guard is for)

The agent is autonomous; the guards assume the model will eventually try
something outside the operator's intent - by mistake, by prompt injection,
or by over-eager tool use. Each boundary is enforced in code, so no
prompt wording can widen it.

| Attack / failure | Guard | Where |
|---|---|---|
| request to an unauthorized host | scope-check before any byte is sent; redirect `Location` re-checked per hop | `ScopeGuard.check`, `GuardedClient.send` |
| `file:`/`gopher:`/`ftp:` URL schemes | scheme allowlist `http`/`https` | `ScopeGuard.check` |
| loopback/private pivot to infra | private-address refusal (`--allow-private` opts in; auto-allowed only when the declared target is itself private) | `ScopeGuard` |
| flood the target | shared token bucket; redirect hops count too | `RateLimiter`, `GuardedClient` |
| invented finding | excerpt must be a verbatim substring of a cited transcript id | `Session.add_finding` |
| finding on an unauthorized asset | `record_finding` URL passes the same scope guard as requests | `tools/analysis.record_finding` |
| post-run transcript tampering | sha256 hash chain per entry + chain head anchored in `summary.json` | `verify_transcript`, `argus verify` |
| post-run findings tampering | `argus verify` re-validates every finding's evidence ids + verbatim excerpt against the chained transcript (the file itself is not hashed) | `verify_transcript` findings pass |
| post-run artifact tampering (meta/findings/notes/report.*/summary) | run-end `artifacts_digest` transcript entry stores per-file sha256; verify recomputes (summary digest skips mutable head/duration so legit re-renders stay clean) | `seal_artifacts`, `artifact_mismatch` |
| scanner output treated as proof | `run_external`/`mcp_call` output is a lead until an `http_request` re-verifies or a `proof_marker` matches | tool notes + evidence gate |
| exfiltrate local files to target | `-d/-F/-b/-T/--data-urlencode` file forms refused; `ffuf -w` confined to bundled/cwd `resources/wordlists`; bundled shorts parsed | `run_external` arg guards |
| smuggle options past the guards | `curl -K`, `sqlmap -c` config files refused | arg guards |
| redirect connection out of scope | `curl --resolve/--connect-to/-x/proxies`, `nmap --proxies`, `ffuf -x`, `sqlmap --proxy/--tor` refused | arg guards |
| foreign hosts inside arg files | `-iL`/`-r`/`-l`/`-m`/`--bulk-file`/nuclei `-l` contents scanned per host | `_file_target_check` |
| local code execution via tool | `sqlmap --eval`, `nmap --script <path>`, `nuclei -t <file>`, `-code` refused | arg guards |
| credential leak to subprocesses | `KEY/TOKEN/SECRET/PASSWORD/CREDENTIAL` env vars scrubbed for MCP servers and exploit PoCs | `MCPClient`, `run_exploit` |
| operator secrets in artifacts | auth/cookie/token request headers + `Set-Cookie` values recorded redacted (names + scheme/attrs kept); reports re-redact old transcripts; `--proxy` gives full-fidelity wire when needed | `GuardedClient`, `render_report` |
| exploit PoC escapes its dir / hits foreign host | relative manifest commands confined to the manifest dir under `resources/exploits/<id>` (cwd or bundled); `{args}` scope-scanned | `run_exploit` |
| worker exceeds its role | card `tools` set enforced at `dispatch`; only lead holds `spawn_worker`/`finish_engagement` | `cards.py`, `dispatch` |
| resume mixes two engagements | `--resume` refuses a session whose `meta.json` target differs | `Session._resume` |
| stalled target hangs a worker | explicit timeouts everywhere; `timeout=None` never reaches httpx | `GuardedClient`, `llm` retry |
| raw context pollution | workers exchange typed artifacts (leads, notes), never conversation | `LeadQueue`, `Board` |

Residuals accepted by design: DNS re-resolution between `check()` and
connect (cache per host); an MCP server is operator-configured and may
reach any URL itself - register only servers you trust; a model can still
waste budget inside scope.

## Extension points

- New probe: add a function in `tools/probes.py`, register in
  `tools/registry.py` (`_impl` + `_schema`). It must send via
  `ctx.client.send` — then scope, rate limit and evidence are free.
- New skill: drop `name.md` in `argus/skills/` + one row in `INDEX.md`.
- New report format: `argus/report/` takes `Session` + `Config`.
- External tool providers: drop a server into `mcp.json` — `argus/mcp.py`
  speaks stdio JSON-RPC, `mcp_list`/`mcp_call` expose it to every role.
- Different model: `ClaudeClient` is ~40 lines of HTTP; `llm.ScriptedClient`
  shows the duck-typed interface (`chat(messages, tools, system)`).

## Team mode (`argus team`)

A second plane over the same primitives: a **lead** agent coordinates
role-specialized **workers** through a shared blackboard.

```
        ┌─────────── lead (AgentLoop, LEAD card) ───────────┐
        │  read_board · spawn_worker · emit_lead · finish    │
        └──────┬─────────────────────────────┬──────────────┘
               │ spawn (thread, own loop)     │ steer notes
        ┌──────▼───────┐             ┌────────▼────────┐
        │ recon worker │ emit_lead  │ exploit worker  │
        │ crawl/js/fuzz├───────────►│ pull→probe→proof│
        └──────────────┘  LEADQUEUE └────────┬────────┘
                                             │ record_finding
                                  ┌──────────▼──────────┐
                                  │ report worker       │
                                  │ findings → summary  │
                                  └─────────────────────┘
            ━━━ shared, code-enforced, never prompt-level ━━━
        ScopeGuard · RateLimiter · Session(transcript) · Board
```

- **Two LLM levels, deliberately.** Lead → workers is the deepest the org
  chart gets. A worker that needs help posts a `request_worker` to the
  board; the lead decides whether to spawn. Sub-division inside a worker
  is tool fan-out (crawl + js_recon + fuzz in parallel calls), not another
  LLM tier - each extra tier is another place to re-interpret intent.
- **Leads are typed artifacts, not chat.** `emit_lead` pushes a deduped,
  prioritized `Lead{kind,url,params,method,tech,source}`. The exploit
  worker never receives "the recon guy said maybe SQLi" - it receives the
  exact URL, params and the request_id it was seen at. Shared artifacts
  beat shared conversation: no context pollution, no hearsay findings.
- **Streaming pipeline.** `pull_leads` blocks while recon runs and returns
  `closed` only when the queue is closed AND drained - exploit starts on
  the first lead, not after recon finishes.
- **Role gating is dispatch-level.** Each card's `tools` set is enforced in
  `dispatch`, not just advertised to the model: a recon worker literally
  cannot call `record_finding`; only the lead's card carries
  `spawn_worker`/`finish_engagement`.
- **Shared guardrails.** One `ScopeGuard`, one `RateLimiter`, one
  `Session`. N workers can't N-fold the request rate; every exchange is
  tagged with its agent name in the transcript.
- **`run_exploit` runs manifests, not magic.** `resources/exploits/<id>/`
  holds `manifest.json` (command template, `affects`, `proof_marker`
  regex) + script. Target URL is scope-checked before substitution; a
  `proof=True` run id is citable as finding evidence.
- **Findings dedup across workers.** `Session.add_finding` rejects a
  second finding with the same normalized bug class + endpoint + params —
  two exploit workers can't double-count the same bug.
- **Per-agent metrics.** `summary.json` carries each agent's turns,
  requests, LLM calls, token usage and credited findings, plus
  `time_to_first_finding_s` — the measurement surface for comparing
  single-agent `run` against the streaming `team` pipeline.

## What it deliberately does not do

- No exploit payloads that persist (no webshells, no shells period).
- No authentication-agnostic scanning of foreign hosts — scope is explicit.
- `run_external` and `run_exploit` output is a lead, not evidence:
  scanner claims are verified through `http_request` (or a manifest's
  `proof_marker`) before `record_finding` accepts them.
