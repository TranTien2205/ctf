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
source resolved, then retries with the full tool schema. Exit codes:
0 = auth works and the full surface is accepted; 1 = no credentials or
auth rejected; 2 = auth works but the tool surface was rejected
(degraded - constrain it). Note: OAuth (subscription) auth bills calls
to your account's "extra usage" budget, not plan limits - on a
constrained account the full ~56-tool schema may be rejected
(`--tools` shrinks it; team mode splits tools across role cards and
fits under the cap).

## Run

```bash
python -m argus run https://app.example
# --scope adds in-scope hosts, --header repeats, --require-proof refuses
# anything the proof matrix does not settle
python -m argus run https://app.example \
    --scope api.example,cdn.example \
    --exclude /logout --exclude /admin/reset \
    --header "Cookie: session=abc" \
    --header "Authorization: Bearer x" \
    --goal "prioritize /api and the checkout flow" \
    --require-proof \
    --rate 3 --max-requests 600 --max-time 3600
```

| Flag | Default | Meaning |
|---|---|---|
| `--scope` | target host only | extra allowed hosts; subdomains included |
| `--exclude` | none | path prefixes never touched |
| `--header` | none | applied to every request (auth, custom UA) |
| `--secret` | none | credential value to redact from all artifacts (repeatable) |
| `--header-file` | none | headers from a file, one `Name: value` per line (Burp copy); framing headers (Host, Content-Length, Transfer-Encoding, Connection) dropped - the wire computes them |
| `--model` | `claude-sonnet-4-5` | any Anthropic model id |
| `--max-turns` | 80 | LLM tool-call turns |
| `--max-requests` | 400 | HTTP request budget |
| `--max-time` | 2400 | wall-clock seconds |
| `--rate` | 5 | requests/second cap |
| `--goal` | full assessment | operator goal, injected into the system contract |
| `--operator` | none | tester/org attribution written into meta + reports |
| `--proxy` | none | route via Burp/ZAP for inspection — the only proxy path; env `HTTP(S)_PROXY` and `~/.netrc` are ignored for target traffic (LLM API calls still honor env proxies) |
| `--llm-max-tokens` | 4096 | per-call response cap for the LLM |
| `--mcp-config` | none | extra MCP servers config file |
| `--tools` | all | `run` and `mcp-serve`: comma tool allowlist (finish always included) — shrinks the per-call schema payload, needed when auth rejects large requests. `team` refuses it: role cards already subset tools per worker |
| `--seal-key` | none | HMAC key, or a path to a file holding one, for the transcript chain (also `ARGUS_SEAL_KEY`). Unkeyed the chain proves the file was not edited after the run; keyed, only a holder of the key can produce a chain that verifies. Never written to an artifact — `argus verify --seal-key ...` checks it |
| `--require-proof` | off | refuse a finding whose evidence does not meet the proof requirement for its class. Off by default: a candidate is worth recording and re-testing. On, `findings.json` holds only what was proven — the condition an evaluation wants to be able to state |
| `--resume` | none | session dir to continue from |
| `--allow-private` | auto if target private | permit RFC1918/loopback |
| `--tls-verify` | off | verify certs (self-signed labs need off) |
| `--no-external` | off | disable sqlmap/nmap/nuclei/ffuf/curl |
| `--session-dir` | `sessions` | where run artifacts land |
| `--quiet` | off | suppress console trace |
| `--version` | — | print the argus build and exit |

## Offline demo

```bash
python -m argus check         # preflight: verify auth before a real run
python -m argus demo          # scripted run on the bundled lab, no API key
python -m argus demo --team   # same, through the lead/worker pipeline
```

Spins up `lab/vulnapp.py`, runs a canned probe sequence through the real
agent loop, and lands six graded findings (SQLi, OS command injection,
XSS, IDOR,
info-disclosure, weak-JWT forge) in a
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

### A model per role

```bash
python -m argus team <target> --role-models            # cheapest per job
python -m argus team <target> --role-models --policy strong
```

Off by default. The four cards want different things - the lead holds the
plan, recon makes many cheap calls over a wide surface, exploit holds one long
chain of reasoning about one target, the writer turns recorded findings into
prose - so `--role-models` gives each the model `argus models` lists for that
job. A pick whose credential is not set falls back to `--model` and says which
variable to set, rather than letting that agent die on its first call.

`summary.json` then carries `llm_cost.per_agent`, each line naming the model
that agent ran on: one rate cannot describe a run that spanned providers, and
an agent on a model with no line in the table reports `null` rather than a
zero that would read as free.

## Probe coverage

Every probe baseline-diffs or uses a matched pair — the verdict is a
signal to verify, never a declared bug. `record_finding` still requires
verbatim evidence from a cited response.

| Bug class | Tool | Detection approach |
|---|---|---|
| Reflected XSS | `probe_reflection` | canary reflection, context detection |
| SQL injection | `probe_sqli` | AND/OR pairs quoted+numeric, error/xpath exfil, opt-in UNION col count, opt-in bounded read (`extract_table`/`extract_columns`, LIMIT applied in the tool) |
| NoSQL injection | `probe_nosqli` | `$ne`/`$gt`/`$regex` JSON + urlencoded `param[$op]` carrier |
| Command injection | `probe_cmdi` | `id; echo <nonce>` across 8 separator families, reads the OUTPUT; reports a reflection as a reflection; falls back to the timing oracle, measured twice against two baselines. A delay alone is **not recordable as an rce finding** - the class floor is the identity line, so it grades `unproven`. Put it in `note()` and say what you could not reach |
| Command injection (blind) | `probe_time` | sleep separators vs measured baseline latency |
| SSTI | `probe_ssti` | `{{7*7}}`-family eval per engine syntax |
| File read / LFI | `probe_lfi` | traversal/absolute/encoded/null-byte + `file://`, `php://filter` decode |
| Open redirect | `probe_redirect` | canonical + //host, backslash, userinfo, suffix-confuse; meta/JS hops |
| CORS | `probe_cors` | foreign/null/subdomain/prefix origins x credentials flag |
| HTTP methods | `probe_method` | OPTIONS + PUT canary/cleanup + TRACE echo check |
| IDOR | `probe_idor` | id +/-1 and id=0 in path/query/JSON body |
| SSRF | `probe_ssrf` | self-fetch + short/decimal/hex/octal/ipv6 encodings + metadata |
| XXE | `probe_xxe` | external entity file/http resolution |
| CSRF | `probe_csrf` | token/SameSite audit + cross-origin replay under both preflight-free content types, bracketed by a `read_url` read before/after + GET state-change leads |
| Host-header | `probe_xfh` | XFH canary + X-Original-URL/X-Rewrite-URL ACL bypass |
| File upload | `probe_upload` | php/phtml/jsp/aspx/svg/htaccess/double-ext/spoof/traversal, served check |
| Race condition | `probe_race` | concurrent burst + serial baseline + overlap check |
| Deserialization | `probe_deserialize` | java/php/pickle/node/yaml/dotnet/ruby magic bytes vs parser errors |
| Cache poisoning | `probe_cache` | unkeyed XFH poison + .css-suffix deception path confusion |
| Prototype pollution | `probe_ppoll` | `__proto__` + `constructor.prototype` carriers, cross-object read |
| Request smuggling | `probe_smuggle` | CL.TE + TE.CL + obfuscated-TE raw sends; 'G'/'GPOST' poison own next request only |
| Info disclosure | `probe_disclosure` | sensitive-path sweep w/ artifact signatures |
| WebSocket | `probe_websocket` | cross-origin RFC 6455 handshake (101 + accept recomputed) **and** one masked text frame, read back off the wire |
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
`read_findings` lists every finding recorded so far (id, severity, category,
url, evidence) — the read side of `record_finding`, and the cheap way to see
what the run already has before probing a class again. `list_exploits` lists
the manifests under `resources/exploits/` with their `affects` fingerprint
and CVE, which is how you find out what `run_exploit` can be pointed at
without reading the directory. Both take no arguments.

## Resources

`resources/wordlists/<name>.txt` — wordlists for `wordlist_fuzz` (path/param/POST-body modes); add a
file to add a list. `resources/exploits/<id>/` — PoC manifests
(`command`, `affects`, `proof_marker`) for `run_exploit`; add a directory
to add an exploit. Both are data, not code — extending coverage needs no
code change. Lookup order is `resources/` in your working directory first,
then the bundled `argus/resources/` (a cwd file shadows a bundled one),
so the same mechanism works from a pip-installed `argus`.

Exploit manifests name commands to run, so the **cwd exploit tree is
opt-in**: it is only searched when `ARGUS_EXPLOITS_CWD=1` is set in the
real environment. Without it, a `resources/exploits/` inside the working
directory is ignored — running argus inside an untrusted checkout can
never turn a planted manifest into command execution. Wordlists carry
no commands and keep cwd shadowing unconditionally.

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
`sqli` -> CWE-89 -> OWASP A03 Injection; unknown categories simply omit
both), plus verbatim `evidence_excerpt` and cited `evidence_ids`.

It also carries `vuln_class`, `grade` and a `proof` block listing every
check with its outcome:

| grade | means | in the report |
|---|---|---|
| `proven` | the class artifact and its control are both on record | listed first; SARIF `kind: fail` |
| `candidate` | a real signal, a named check still missing | listed after, with the missing check printed; SARIF `kind: review`, `level: none` |
| `unproven` | nothing in the cited evidence meets the requirement | listed last with the requirement quoted |
| `refused` | this system does not prove the class | cannot be recorded at all |

`summary.json` carries `grades` as counts. Read the candidates as work to
finish, not as results: `argus proof <class>` prints what each one needs.

`argus verify <dir>` recomputes the grades from the chained transcript, so a
grade raised by hand in `findings.json` fails the check — including after an
`argus report` re-render has recomputed the artifact seal.

What the chain proves is narrower than it looks. Unkeyed it is
`sha256(previous + entry)`, computable by anyone with this code: it proves no
entry was edited, inserted or removed after the run, and nothing about whether
the run happened. For an engagement whose report will be read by someone who
did not watch it, pass `--seal-key` — each link becomes HMAC-SHA256 and only a
holder of the key can produce a chain that verifies. `argus verify` then needs
the same key and says so rather than reporting every line as tampered.

`python -m argus findings <session_dir>` reprints the table;
`python -m argus report <session_dir>` re-renders `report.md`;
`python -m argus sessions` lists every session dir with mode, finding and
request counts plus the producing argus version (`--json` for scripts);
`python -m argus compare <dirA> <dirB>` prints a side-by-side metrics
table (mode, findings, requests,
time-to-first-finding, endpoints touched, llm calls, workers, tokens
incl. cache read/write) for run-vs-team experiments; `--csv` emits one
row per session for spreadsheets/pandas. `--by-arm` is the N-trial form:
it groups the dirs by configuration (the parent directory with a trailing
`-<trial>` stripped, the layout `docs/EXPERIMENTS.md` lays out) and prints
the median of each metric per arm with N and the min-max spread. The
median is `median_low`, so on an even N it is a figure some trial produced
rather than the mean of the middle two, and `cost (usd)` stays blank
unless every trial in the arm carries a price.
`python -m argus diff <before> <after>` is the retest view: findings are
matched across the two sessions by bug class + host + path + params
(ports ignored, so a fresh lab instance still lines up) and printed as
`FIXED`, `STILL PRESENT` (with severity drift), or `NEW`; `--json` for
scripts. Both commands warn on stderr when the compared sessions were
run against different base hosts (a cross-host diff would silently read
as all-fixed + all-new); `compare` also warns when the sessions were
produced by different argus builds, since metric deltas are only
like-for-like on the same version.
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
invented evidence ids surface as `TAMPERED: findings [...]`. At run end an
`artifacts_digest` entry seals sha256 hashes of `meta.json`,
`findings.json`, `notes.md` and `report.*` plus `summary.json` (minus
the mutable head/duration fields) into the transcript - post-run edits
to ANY session artifact, even a byte, surface as `TAMPERED: [...] edited
since the run was sealed`. `argus report` re-renders re-seal the fresh
artifacts, skip failing findings and warn when the chain itself is
broken; `argus findings` marks failing rows `UNVERIFIED`. `verify --json`
emits the raw result (`ok` mirrors the exit code) for CI pipelines. Every
session also records which argus build produced it - `meta.json` /
`summary.json` carry `argus_version` (a resumed session keeps the
original and adds `resumed_by`), `argus sessions` shows it in the
listing and `argus verify` reports it as `produced_by`, so a reviewer
re-validating old artifacts knows which evidence rules applied.

Secret header **values** (`Authorization`, `Cookie`, `Set-Cookie`,
`X-*-Token` and any header carrying a `--header`-configured secret) are
recorded redacted - the audit shows the request was authenticated without
persisting live credentials into `transcript.jsonl` or the report. Header
names, the `Bearer` scheme, cookie names and `Set-Cookie` attributes stay
visible. Findings cite response bodies, so redaction can never break a
verbatim check. When full wire fidelity is needed, run with `--proxy`
through Burp/ZAP - the interceptor sees everything Argus sends.

Credential **values** anywhere else (a login password the agent posts in
a form body, a token it quotes) are covered by `--secret VALUE`
(repeatable, min 4 chars): every persisted artifact - transcript bodies,
event output, `notes.md`, `agent.log`, `meta.json` - has each declared
value replaced with a redaction marker at write time. The model still
sees the real bytes it needs to authenticate; only what hits disk is
scrubbed. A finding cannot cite a declared secret as its evidence
excerpt - by design, secrets are never proving bytes.

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

## A second model on the evidence (`argus judge`)

```bash
python -m argus judge <session>                  # the table picks the judge
python -m argus judge <session> --dry-run        # print the case file, no call
python -m argus judge <session> --judge-model gpt-4.1 --only F01,F03
```

One rule governs everything this command does:

> **a judge can dispute a finding or lower its severity. It can never promote
> one.**

The proof matrix is deterministic and auditable. A model's opinion is neither.
If an opinion could raise a `candidate` to `proven`, the strongest claim this
system makes would rest on its weakest check — so `grade` is never touched
here, and a disagreement lands in a separate `judge` field the report prints
next to the grade it disputes.

What a judge is *for*, then, is the gap the matrix cannot see. The matrix
grades whether the cited bytes meet a class's requirement. It cannot tell you
the finding is filed under the wrong class, that the title claims more than
the bytes support, or that the severity is indefensible. Those are judgements,
and a model from a different family is a real second opinion on them.

The judge is shown the finding, its class's requirement, and the cited records
— never the first model's reasoning, because the disagreement worth having is
the one that reasoning would not produce. `--dry-run` prints exactly what it
would be sent.

Four refusals worth knowing:

* **No independent judge is an answer.** If every model listed for the `judge`
  role outside the author's family needs a credential that is not set, the
  command says so and exits. Running the author's own family as its own
  reviewer and calling it cross-verification would be the kind of claim this
  system exists not to make — `--judge-model` is refused for the same reason.
* **Prose is not a verdict.** A reply with no JSON object carrying `agrees` is
  recorded as *no verdict*, not as assent.
* **Two contradicting objects are not a verdict either.** A model that
  illustrated the format and then answered, and one that answered and then
  hedged, emit the same two objects in the same order; picking one would be a
  guess, and a guess landing on "agrees" manufactures the assent the command
  exists to avoid.
* **A transport failure is not a dispute.** It is recorded as an error with no
  `reason`, so it cannot read as a substantive disagreement in the report.

The verdicts are recorded into the transcript as a `cross_verification` event,
so they are inside the hash chain, and the session is re-sealed afterwards —
the same trade `argus report` makes.

## Asking the evidence what is next (`argus next`)

```bash
python -m argus next engagements/2026-11-09-120000-target
python -m argus next <session> --json      # for a harness
```

The answer is computed from `transcript.jsonl` and `findings.json` and from
nothing else. It never saw the conversation, which is the point: a model whose
context has rolled over, or whose last four turns were the same payload with a
new separator, gets the same answer a fresh reader of the evidence would give.

Seven ordered rules, each naming the observation that fired it:

| action | fires when |
|---|---|
| `record_finding` | an exchange on disk already meets a proof requirement and no finding cites it |
| `close_proof_gap` | a recorded finding is `candidate`, and the matrix names the exact missing check |
| `probe` | a parameterised endpoint carries named inputs that no class-bearing probe touched |
| `park_and_switch` | one class has spent its probe budget on one endpoint with nothing recorded |
| `widen_surface` | findings exist but only one endpoint was ever reached |
| `report` | every endpoint is probed for the first-pass classes and every finding is graded |
| `open_session` / `recon` | there is no session, or no request/response pair yet |

The agent can ask the same question mid-run with the `next_action` tool. It is
advice, not a rail: departing from it is normal and often right, and the
contract is only that the departure is stated.

What it will not do is invent work. An endpoint with no named input is not
recommended for probing, because there is nowhere to put a payload; a static
asset is not surface; and rule 1 grades a probe's output **only under that
probe's own class**, because re-grading every exchange against all 29 would
turn any page that echoes its query into a recommendation to record `sqli` -
the exact failure the proof matrix exists to prevent.

## Choosing a model (`argus models`)

The provider is a fact about the model, not about the code. `argus/models.json`
says which provider each model belongs to, what it costs, and which jobs it is
listed for; `argus models` prints it.

```bash
python -m argus models          # the table, with which credentials are set
python -m argus models --json   # the same, for a script
```

Four columns matter. `provider` picks the adapter (`anthropic` speaks the
Messages API, `openai` speaks chat-completions - the loop itself is unchanged
either way). `in`/`out` are USD per million tokens **as published when the
line was written**, which is why a cost in a report names the table version:
a price that moved makes a stale report wrong, and you can check the line.
`cred` says whether an environment variable named for that model is actually
set right now - it is not a claim that the key works, only that one exists.

Name a model directly, or say what the task needs:

```bash
python -m argus run <target> --model deepseek-chat   # by name
python -m argus run <target> --role depth            # cheapest that can do it
python -m argus run <target> --role depth --policy strong
```

`--model` always wins over `--role`, because an operator naming a model has a
reason the table does not know. A model the table has never heard of is sent
to Anthropic rather than refused: an unknown name is far more likely a new
Claude release than a typo. The five roles are described in the table itself
(`planner`, `breadth`, `depth`, `judge`, `writer`) - `judge` is the one worth
reading, because a reviewer from the family that produced the finding is the
same prior answering twice, not a second opinion.

A non-Anthropic credential is refused over plaintext `http://` unless the
model's line opts in (`local` does, for a loopback server). That is not
paranoia about the lab; it is that an API key in cleartext on the wire is
spent.

### What the cost number is and is not

`summary.json` carries `llm_cost`, and the report prints it. It is the token
counts this run recorded, multiplied by the rates in `models.json`, with cache
reads at a tenth of input. It is **not** a bill: it ignores request overhead,
it uses the rate in the file rather than the rate you were charged, and a
model that is not in the table reports `usd: null` with the reason rather than
a guessed number - the same rule as every other figure here.

## Proof requirements

```
python -m argus proof            # all 29 classes, one line each
python -m argus proof rce        # one class in full
python -m argus proof sqli --json
```

Read it before probing a class, not after writing the finding —
`load_skill("<class>")` attaches the same requirement to the methodology
module, which is the moment it still changes what gets sent.

```
rce - proof requirement

  the output of `id; echo <nonce>` returned by the target, with the nonce
  tying the output to the probe

  checks that must pass:
    - a benign command was sent
    - identity output returned by the target
    - marker echoed in the output
  without this one, nothing above 'unproven' is available:
    - identity output returned by the target
  disqualifies the evidence entirely:
    - proof command stayed benign
```

## Serving argus to your own LLM (`argus mcp-serve`)

```
python -m argus mcp-serve http://127.0.0.1:8777 --allow-private \
    --require-proof --session-dir sessions
```

Speaks newline-delimited stdio JSON-RPC and serves 46 of the 56 tools.
Takes the same flags as `run`. Register it with any MCP host:

```json
{"mcpServers": {"argus": {
  "command": "python",
  "args": ["-m", "argus", "mcp-serve", "http://127.0.0.1:8777",
           "--allow-private", "--require-proof"]}}}
```

The scope guard, rate limiter, transcript, dedup and proof matrix stay on
this side. `initialize` returns the operating contract as `instructions`.
Withheld: the eight board tools (the host LLM is the orchestrator here, and
outside team mode there is no Board for them to reach) and
`mcp_list`/`mcp_call` (argus calling out while serving would be a loop the
operator cannot see). `finish` renders and seals the session, so
`argus verify` has an anchor for a served engagement too.

## MCP tool servers

`mcp_list` / `mcp_call` bridge external MCP servers (search, fetch, CVE
data) declared via `--mcp-config` or `ARGUS_MCP_CONFIG`. A `mcp.json` /
`.argus-mcp.json` / `.mcp.json` in the working directory is **ignored
unless `ARGUS_MCP_CWD=1`** — configs name subprocesses to run, so a file
inside an untrusted directory must not silently wire commands to the
agent:

```json
{"servers": {"search": {"command": ["npx", "-y", "some-search-mcp"]}}}
```

Servers spawn lazily, one subprocess each, shared across workers. Output is
flagged untrusted and logged as `mcp_call` transcript events. Because MCP
servers make their own network requests outside `GuardedClient`, any
http(s) URL found in `mcp_call` arguments is scope-checked first — a
fetch-type server cannot be used to reach out-of-scope targets.

## The lab

`argus/lab/vulnapp.py` is a stdlib-only vulnerable app planting one bug per probe
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

Severity and grade answer different questions, and both are printed.
Severity is how bad it would be; the grade is how sure we are. A
`critical` + `candidate` row is a lead worth a day of someone's time, not a
result — and `probe_*` verdicts say "candidate" for the same reason.
