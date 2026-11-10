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

record_finding(...) is the one tool with a second gate behind it:

    excerpt verbatim in a cited response?   → no: rejected
                │ yes
    proof.grade(class, excerpt, cited)      → proven / candidate /
                │                              unproven / refused
    refused class?                          → rejected, always
    --require-proof and not proven?         → rejected
                │
    recorded, carrying vuln_class + grade + every check
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
- **Evidence gating at write time, in two layers.** `Session.add_finding`
  asserts the excerpt is a substring of a cited response. That is necessary
  and not sufficient: it proves the bytes were observed, not that the class
  was demonstrated, and a benign page reading `uid=1 selected` satisfies it
  for a claimed critical RCE. So the claim is then graded by
  `argus/proof.py` against a requirement written per class — read from the
  cited request *and* response, never from a probe's self-report, so a probe
  cannot grade itself. Four grades: `proven`, `candidate`, `unproven`,
  `refused`. The grade does not block the record; it comes back with the
  names of the checks that did not pass, and re-recording with the missing
  evidence upgrades the finding in place. `--require-proof` refuses anything
  below `proven`.
- **Baseline-diffed probes.** Each `probe_*` returns `verdict` +
  `request_ids`, never "you are vulnerable". The agent confirms and
  rates severity itself.
- **Skills as retrievable knowledge.** 27 methodology modules (~2KB each)
  load on demand via `load_skill`. Detection signals, first probes,
  confirmation criteria, bypasses, honest severity guidance.
- **Budget-aware autonomy.** max_turns / max_requests / max_time are real
  limits; the loop warns once near ~80% ("record now, prioritize"), nudges
  once at exhaustion, then stops. Measured on a real run: the early
  warning turned a deferred-finding loss into a 5x recording rate. That
  number is from a development run whose session was not kept, so treat it as
  the reason the warning exists rather than as a measurement - the research
  measurements have not been run.
- **Cost-aware LLM calls.** `ClaudeClient` marks the static prefix
  (system + tools + conversation tail) with ephemeral cache breakpoints —
  billed input drops ~90% on cache hits. A 400 mentioning cache disables
  it transparently. The tool schema alone is ~32KB; a call also carries the
  system prompt and the conversation, so the request is larger than that and
  the figure is a floor, not the payload. Constrained auth paths can pass
  `--tools` (run and mcp-serve) or rely on role-card subsets (team) - the
  exploit card is the largest, so measure it rather than assuming it fits.
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
| loopback/private pivot to infra | private-address refusal over ALL resolved records (v4+v6 via `getaddrinfo` - one private answer denies) plus a **connect-time peer check**: `send()` inspects `network_stream.server_addr` and `send_raw()` inspects `sock.getpeername()`, so a DNS answer that flips between check and connect (rebinding) is refused on the real peer IP; `--allow-private` opts in, auto-allowed only when the declared target is itself private. Residual: external scanners run their own sockets and re-resolve independently - their args are vetted against scope but the wire itself is the tool's | `ScopeGuard`, `GuardedClient` |
| flood the target | shared token bucket; redirect hops count too | `RateLimiter`, `GuardedClient` |
| invented finding | excerpt must be a verbatim substring of a cited transcript id | `Session.add_finding` |
| a claim stronger than its evidence | the class requirement is re-checked against the cited request/response; a shortfall grades `candidate`/`unproven` and names the missing check, and `--require-proof` refuses it | `proof.grade`, `Session.add_finding` |
| a class this system cannot prove | `dos` is `refused` by construction and cannot be recorded at all, at any grade | `proof.verify_refused` |
| a proof grade raised by hand after the run | `argus verify` recomputes every grade from the chained transcript; an inflated grade fails even after a legitimate `argus report` re-render has recomputed the artifact seal | `findings_overgraded` |
| finding on an unauthorized asset | `record_finding` URL passes the same scope guard as requests | `tools/analysis.record_finding` |
| post-run transcript tampering | sha256 hash chain per entry + chain head anchored in `summary.json` | `verify_transcript`, `argus verify` |
| a session forged from nothing | the unkeyed chain does NOT stop this: sha256(prev+entry) is computable by anyone, so it proves the file was not edited after the run and nothing more. `--seal-key` makes each link HMAC-SHA256, and then only a holder of the key can produce a chain that verifies; `argus verify` reports `key_required` rather than calling every line tampered | `_chain`, `verify_transcript` |
| post-run findings tampering | `argus verify` re-validates every finding's evidence ids + verbatim excerpt against the chained transcript, AND recomputes its grade; `findings.json` is also in the run-end seal, so an edit is caught twice over - except after a legitimate `argus report` re-render recomputes the seal, which is why the re-grade is not redundant | `verify_transcript` findings pass, `findings_overgraded` |
| post-run artifact tampering (meta/findings/notes/report.*/summary) | run-end `artifacts_digest` transcript entry stores per-file sha256; verify recomputes (summary digest skips mutable head/duration so legit re-renders stay clean) | `seal_artifacts`, `artifact_mismatch` |
| scanner output treated as proof | enforced, not advised: `run_external`/`mcp_call` record events carrying `output` and no `response`, and a claim citing only those fails the wire check for every class. A `proof_marker` match is recorded as a `run_exploit` event and is subject to the same rule - what makes a lead citable is an `http_request` that reproduces it on the wire | `proof._wire_check` |
| exfiltrate local files to target | `-d/-F/-b/-T/--data-urlencode` file forms refused; `ffuf -w` must name a stem under the bundled or cwd `resources/wordlists` tree, so an arbitrary path is refused - but any file placed in that tree is readable, and the cwd tree is operator-controlled | `run_external` arg guards |
| smuggle options past the guards | `curl -K`, `sqlmap -c` config files refused | arg guards |
| redirect connection out of scope | `curl --resolve/--connect-to/-x/proxies`, `nmap --proxies`, `ffuf -x`, `sqlmap --proxy/--tor` refused | arg guards |
| foreign hosts inside arg files | `-iL`/`-r`/`-l`/`-m`/`--bulk-file`/nuclei `-l` contents scanned per host | `_file_target_check` |
| local code execution via tool | `sqlmap --eval`, `nmap --script <path>`, `nuclei -t <file>`, `-code` refused | arg guards |
| credential leak to subprocesses | `KEY/TOKEN/SECRET/PASSWORD/CREDENTIAL` env vars scrubbed for MCP servers and exploit PoCs | `MCPClient`, `run_exploit` |
| operator secrets in artifacts | auth/cookie/token request headers + `Set-Cookie` values recorded redacted (names + scheme/attrs kept); credentials used outside headers (form bodies, tokens) are declared via `--secret VALUE`/`ARGUS_SECRETS` (>=4 chars) and scrubbed from every persisted object at write time - model sees real bytes, artifacts get `REDACTED:` markers; reports re-redact old transcripts; `--proxy` gives full-fidelity wire when needed | `GuardedClient`, `session._redact_obj`, `render_report` |
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
- New skill: drop `name.md` in `argus/skills/` + one row in `INDEX.md`. Name
  it after a proof-matrix class and `load_skill` attaches the requirement to
  it automatically.
- New proof class: a `ProofSpec` in `argus/proof.py` — a requirement
  sentence, the named checks, a verifier, and `floor`/`veto` where they
  apply. It needs a test in BOTH directions: an evidence set that must grade
  `proven`, and one that must not. The second is the one that matters. Watch
  for a check that passes trivially — three of them shipped and had to be
  fixed, because the verbatim gate already guarantees the excerpt exists, so
  "the quoted bytes are in a response" carries no information.
- New report format: `argus/report/` takes `Session` + `Config`.
- External tool providers: drop a server into `mcp.json` — `argus/mcp.py`
  speaks stdio JSON-RPC, `mcp_list`/`mcp_call` expose it to every role.
- Different model: `ClaudeClient` is ~130 lines of HTTP; `llm.ScriptedClient`
  shows the duck-typed interface (`chat(messages, tools, system)`).

## Served mode (`argus mcp-serve`)

A third plane, and the one that spells out the chain the project is built
against — `user -> LLM -> MCP -> tool`. `argus/mcpserver.py` exposes 45 of
the 56 tools over newline-delimited stdio JSON-RPC, symmetric with the client
in `argus/mcp.py`, so the two halves of the protocol are testable against
each other rather than against a mock.

```
   MCP host (Claude Code / IDE / agent runtime)
        │  tools/list · tools/call          stdio JSON-RPC
        ▼
   ArgusMCPServer ── dispatch(ctx, name, args)
        │
        └─ the same ScopeGuard · RateLimiter · Session · proof matrix
```

The driver moves outside; the guards do not. A host LLM gets argus's hands,
not argus's permissions: it cannot widen scope, cannot send a byte that is
not recorded, and a finding it records is graded exactly as `argus run` would
grade it. `initialize` hands back `build_system(cfg, scope)` as
`instructions`, so a host that never read argus's system prompt still
receives the scope and the evidence rules.

Withheld: every board tool — `spawn_worker`, `request_worker`,
`list_workers`, `finish_engagement`, `read_board`, `post_board_note`,
`emit_lead`, `pull_leads`. They are team orchestration, the host LLM is the
orchestrator here, and outside team mode there is no Board for them to reach,
so advertising them would put entries in the catalogue that can only raise.
Plus `mcp_list`/`mcp_call`, which would let argus call out to other servers
while serving as one.

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
- **Findings dedup across workers.** `Session.add_finding` keys on the
  canonical class + endpoint + params, so two exploit workers cannot
  double-count the same bug and two spellings of one class are one finding.
  A second record with evidence that grades HIGHER upgrades the finding in
  place rather than being refused - otherwise the grading would tell a worker
  which checks it was missing and leave it nowhere to put them. The original
  citation is kept under `superseded_evidence_ids` and `ts` stays the first
  record's.
- **Per-agent metrics.** `summary.json` carries each agent's turns,
  requests, LLM calls, token usage and credited findings, plus
  `time_to_first_finding_s` — the measurement surface for comparing
  single-agent `run` against the streaming `team` pipeline.

## The decision controller (`argus next`)

```
transcript.jsonl ─┐
                  ├─► argus/decide.py ─► Action{action, why, target, class, tool, detail}
findings.json ────┘        (7 ordered rules, fail-closed)
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
             `argus next <session>`   next_action tool
             (operator)               (the agent, mid-run)
```

The loop chooses the *content* of the next move. This module computes its
*shape*, and it reads only what was recorded. That split is the point: a model
given a transcript and an open question usually picks a sensible next probe,
but one whose context has rolled over instead re-sends the last payload with a
new separator, or writes a confident paragraph about a bug it never showed.
From the outside those two are indistinguishable — unless the next action is
derived from the bytes on disk.

It is advice, not a rail. Nothing refuses a tool call because the controller
suggested something else; the contract in `argus/system.py` is only that a
departure is stated in one line. Three properties keep it from inventing work:

* an endpoint with **no named input** is never recommended for probing, because
  there is nowhere to put a payload;
* rule 1 re-grades a probe's output **only under that probe's own class** —
  re-grading every exchange against all 29 would turn any page that echoes its
  query into a recommendation to record `sqli`, which is exactly what the proof
  matrix exists to prevent;
* `probe_time` is deliberately unmapped. A latency measurement is consistent
  with `sqli`, with `rce` and with a slow database, so counting it as "this
  class was tested" would let a timing run stand in for a proof it cannot
  produce.

Rule 1 is also how the controller earns its keep as a reviewer of this system
rather than of the target: re-grading recorded transcripts found that `nosqli`
graded `proven` on a page that merely echoed `{"$ne": null}` back. See
`CHANGELOG.md`.

## Cross-family verification (`argus judge`)

```
findings.json + the cited records ──► judge (a family the author is NOT in)
                                          │
                                          ▼
                             {agrees, reason, severity, class, missing}
                                          │
                                   apply_verdict()
                                          │
              ┌───────────────────────────┼───────────────────────┐
              ▼                           ▼                       ▼
       disputed = true          severity may go DOWN         grade: untouched
       (never cleared)          (original kept)              (the matrix owns it)
```

The one-way doors are the design. The matrix is deterministic and auditable; a
model's opinion is neither. If an opinion could raise a `candidate` to
`proven`, the strongest claim this system makes would rest on its weakest
check — so the judge writes to its own fields and the report prints them next
to the grade they dispute.

That leaves the judge doing the thing the matrix cannot: the matrix grades
whether the cited bytes meet a class's requirement, and has no view on whether
the finding is filed under the right class, whether the title claims more than
the bytes support, or whether the severity is defensible.

Three replies are recorded as *no verdict* rather than assent — prose with no
JSON object carrying `agrees`, two objects that contradict each other, and a
transport failure. And if no model outside the author's family is
credentialed, the command exits saying so: the author's own family reviewing
itself is not cross-verification, which is why `--judge-model` is refused on
those grounds too.

## Known residuals

Two adversarial audits - the second against a frozen tree, with every finding
put to three independent skeptics - produced the fixes recorded in
`CHANGELOG.md`. What follows is what they found and this system does NOT fix,
written down so it is a decision rather than an omission. `argus proof <class>`
prints each class's own version of this.

**A judge is one call and one opinion.** There is no panel, no majority, and
no second round: a single model from one other family reads each finding once.
That is enough to catch a misfiled class or an indefensible severity and not
enough to call anything settled. It also costs one call per finding on a
second provider, which is why it is a separate command rather than a step in
every run.

**The decision controller reads the transcript, not the target.** It can only
recommend surface that some recorded request already reached, so an endpoint
nothing ever requested is invisible to it - it will say `report` on a run whose
crawl missed half the application. It also treats one `(endpoint, class)` pair
as the budget unit, so five probes spread over five endpoints never trigger
`park_and_switch`. Neither is a soundness problem - it never claims a proof -
but both are reasons the ladder is advice and not a plan.

**Six classes are capped at `candidate` and the cap is a missing
implementation, not a law of nature.** `crlf` is decided on bodies while the
artifact is a response header; `method` would be settled by a TRACE echo or a
PUT that lands; `upload` by the served content-type; `websocket` by a real
client; `smuggle` by the desync response on the wire; `race` by a serial
control. Each is checkable from what the transcript already records, and each
needs a verifier written. `lockout` and `enum` were in this list and came out
of it - the pattern works, the rest is labour. Until then the requirement
sentence says what would settle the class, and
`tests/test_proof.py::CANNOT_BE_PROVEN_HERE` is asserted against the code so
the list cannot grow in silence.

**`xss`, client-side `ppoll` and `ssrf` are capped for a real reason.** The
first two need a browser and the third needs an out-of-band collector; this
system has neither. Driving one over `mcp_call` is the path, and nothing here
does it yet.

**`probe_csrf` cannot produce evidence its own class accepts, by design.** The
proof needs a state-changing write, and the probe is read-only. The agent
reaches `proven` with `http_request`; the probe's job ends at detection.

**A re-render re-seals.** `argus report` recomputes the artifact digests,
which is what makes a legitimate re-render verify - and therefore what lets an
edit made before the re-render come out the other side digest-valid. The grade
is recomputed and corrected, and `--seal-key` closes the forgery case, but an
edit to `notes.md` before a re-render is not detectable by the seal alone.

**`argus compare` and `argus sessions` read `summary.json` as given.** They
are reporting tools over a file `argus verify` is the check for; a tampered
summary misreports there until you verify.

**The doc gate checks what it can name.** Tools, subcommands, flags, proof
classes, `ARGUS_*` variables, and the stated counts of tools, classes, skills,
tests and selftest checks - all against the code. It does not check prose
claims, and `_NOT_TOOLS` is a hand-maintained allowlist of identifiers that
look like tools and are not.

**Windows is checked, not run, on this host.** `tests/test_windows.py`
exercises the path and separator logic through `ntpath` and `os.name`, which
is the half that differs; CI runs the real thing on windows-latest.

**The research measurements have not been run.** `docs/EXPERIMENTS.md` is a
protocol. Every number in this repository is a test count, a tool count or a
measurement of the system on its own lab - none is a result about agent
performance.

## What it deliberately does not do

- No exploit payloads that persist (no webshells, no shells period). Code
  execution is proven with `id; echo <nonce>` and stops there: the matrix
  vetoes an rce claim whose cited request carries a destructive payload, so
  the evidence is void even when the command ran.
- No authentication-agnostic scanning of foreign hosts — scope is explicit.
- `run_external` and `run_exploit` output is a lead, not evidence:
  scanner claims are verified through `http_request` (or a manifest's
  `proof_marker`) before `record_finding` accepts them.
