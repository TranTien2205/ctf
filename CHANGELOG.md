# Changelog

Rebuild of the NCKH "agent for web pentest" project from the original
CTF-focused toolkit into an authorized, audit-ready web penetration-testing
system. All notable milestones on `agent-v2`.

## Rebuild milestones

### Core runtime (fail-closed by construction)
- ScopeGuard: host allowlist, private-IP and file-scheme refusal, per-hop
  redirect re-check, DNS-cache aware — refuses before any bytes are sent.
- GuardedClient: the only socket-owning client; every request is
  scope-checked, rate-limited, budgeted and transcript-recorded, including
  `send_raw` (desync probes carry operator headers but keep scoped Host).
- Evidence gate: `record_finding` requires a verbatim excerpt that is a
  substring of a cited recorded response, an in-scope URL, and dedups by
  bug class + endpoint + params.
- Tamper-evident audit: sha256 hash chain over `transcript.jsonl`, chain
  head anchored in `summary.json`; `argus verify` detects edits,
  insertions, deletions, tail truncation — and re-validates every finding
  against the immutable transcript so an edited `findings.json` fails too.
  Run end seals `meta.json`/`findings.json`/`notes.md`/`summary.json`
  sha256 digests into the chain (`artifacts_digest`), so post-run edits
  to ANY session artifact are caught; `argus report`/`argus findings`
  warn on broken chains, failing findings and seal mismatches.
- ScopeGuard exclusions match the normalized wire path: percent-encoding
  and dot-segments cannot bypass `--exclude` (httpx decodes/resolves
  before sending, so the raw-path check was fail-open).
- Operator secrets never persist: `Authorization`/`Cookie`/`Set-Cookie`/
  `X-*-Token` and any `--header`-configured value are redacted at record
  time (transcript + logs) and re-redacted at render time (old sessions);
  `--proxy` remains the wire-fidelity path. `--secret`/`ARGUS_SECRETS`
  declare credential *values* (login passwords posted in bodies, quoted
  tokens) that `Session` redacts inside every artifact write — bodies,
  event output, notes, meta.json, logs — while the model still sees the
  real bytes.

### The proof matrix (`argus/proof.py`)
- The verbatim gate proves the bytes were observed, not that the class was
  demonstrated: a benign page reading `uid=1 selected` satisfied it for a
  claimed critical RCE. Every finding is now also graded against a
  requirement written per class — 29 classes, four grades (`proven`,
  `candidate`, `unproven`, `refused`).
- Verifiers read the recorded request AND response of the cited exchanges,
  never a probe's self-report, so a probe cannot grade itself. `rce` needs
  the identity line plus a nonce and rejects an identity line that appears in
  its own request — a reflection cannot pass. `sqli` needs the engine named
  plus a row from a named table; an error string in the excerpt fails the row
  check by construction. `xss` cannot exceed `candidate` without a browser,
  and says so.
- Scanner output stopped being admissible: `run_external`/`mcp_call` record
  events with no `response`, so a claim citing only those fails the wire
  check for every class. The docs always said "a lead, not evidence";
  nothing enforced it.
- The grade never blocks the record — a candidate is worth re-testing — and
  the result names the checks that did not pass. Re-recording with the
  missing evidence **upgrades** the finding in place rather than being
  refused as a duplicate. `--require-proof` refuses anything below `proven`.
  A `refused` class (dos) cannot be recorded at all.
- `category` is an enum of the 29 classes and the dedup key is the canonical
  class, so `SQLi`, `sql-injection` and `sqlinjection` are one bug and not
  three — the cross-worker dedup the docs promised but normalized free text
  could not deliver.
- `argus proof [class]` prints a requirement; `load_skill("<class>")`
  attaches the same one to its methodology module, which is the moment it
  still changes what gets sent.
- `argus verify` recomputes every grade from the chained transcript, so a
  grade raised by hand in `findings.json` fails — including after an
  `argus report` re-render has recomputed the artifact seal, which is the
  only signal that survives that laundering.
- Graded against the old checked-in demo session: 1 proven, 2 candidate,
  2 unproven. One of the unproven was its `critical` "forged admin token
  accepted", which cited `GET /api/user/1` — a request carrying no token.

### argus as an MCP server (`argus mcp-serve`)
- `user -> LLM -> MCP -> tool`: 46 of the 56 tools served over
  newline-delimited stdio JSON-RPC, symmetric with the client in
  `argus/mcp.py`, so both halves of the protocol are testable against each
  other. Register it with any MCP host.
- The driver moves outside; the guards do not. Scope, rate limit,
  transcript, dedup and grading stay on this side, and `initialize` returns
  the operating contract as `instructions`.
- Withheld: all eight board tools (the host LLM is the orchestrator, and
  outside team mode there is no Board, so the four that were advertised could
  only raise) plus `mcp_list`/`mcp_call` (argus calling out while serving is a
  loop the operator cannot see).

### Probe coverage (27 matched-pair probes)
- Injection: sqli (quoted/numeric/OR-pair/xpath/UNION + opt-in bounded
  `extract_table` read with the LIMIT applied in the tool), nosqli, ssti,
  **cmdi** (`id; echo <nonce>` across 8 separator families, reads the output
  rather than the clock, and reports a reflection as a reflection),
  command-time, lfi, reflection/xss.
- Access: idor, user-enum (error+timing), lockout, mass-assignment.
- Transport: request-smuggling (CL.TE/TE.CL/obf raw sends), crlf,
  open-redirect (incl. javascript: scheme + httpx verbatim recovery),
  cors (5 channels incl. preflight + null origin), methods, host-header.
- Crypto/state: jwt_decode + jwt_forge (weak-secret crack → re-sign chain),
  deserialization (java/php/pickle/node/yaml/dotnet/ruby).
- Infra: ssrf (incl. file:// + ip-encodings), cache poison+deception,
  prototype-pollution (__proto__ + constructor.prototype), upload, race,
  websocket, xxe, info-disclosure, graphql-introspect, csrf.

### Multi-agent team mode
- Lead/recon/exploit/report role cards; tool subsets enforced in dispatch,
  never only in the prompt.
- Typed lead queue: recon `emit_lead`s surface while exploit workers
  `pull_leads` concurrently — streaming pipeline, not stage batching.
- Shared typed blackboard (leads/notes/requests/status/findings),
  worker-spawn requests, max_workers cap, per-role turn/request budgets.
- Crash isolation per worker, lead-death closes the pipeline, watchdog +
  bounded joins, daemon threads — the team cannot wedge.
- `mcp_call` scope-checks every http(s) URL inside its arguments — an
  MCP fetch server cannot become a path around the scope guard, and the
  block is recorded in the transcript.
- External-tool args are scanned for URLs, bare hosts, IPv6 literals
  (`nmap ::1` no longer slips past `split(':')`), single-label names
  (`localhost`, `db01`) and non-canonical IP spellings (`127.1`,
  `2130706433`, `0x7f000001`) — tools parse all of them even where the
  host resolver does not. Per-tool flag guards cover local-file exfil,
  target-list files (incl. IPv6 lines), redirect flags, and local code
  exec (ffuf `-input-cmd`, sqlmap `--eval`/`--alert`/`-z eva=`,
  nuclei `-code`/`-lfa`/custom interactsh, nuclei template dirs
  confined to cwd, ffuf `-request` files host-checked).

### LLM layer
- Auth chain: `--api-key`/`ANTHROPIC_API_KEY` → `ANTHROPIC_AUTH_TOKEN`/
  `CLAUDE_CODE_OAUTH_TOKEN` → Claude Code OAuth (auto-refresh) → OpenCode.
- Prompt caching with ephemeral breakpoints on the static prefix
  (~90% input discount); cache metrics in summary/compare.
- `--tools` allowlist for constrained OAuth tiers (validated, meta.json
  records the subset); `argus check` now diagnoses the tool-surface cap
  directly instead of letting it fail mid-run.
- Budget-aware loop: early warning at ~80% + record-immediately contract
  (measured A/B on a real run: 1 → 5 findings at equal budget).
- Context-bounded history: old tool_results compact to stubs naming their
  request_ids; `read_response` re-inspects any exchange — an 80-turn run
  cannot silently overrun the window.
- Real-LLM e2e verified over Claude Code OAuth: the evidence gate rejected
  hallucinated excerpts and malformed calls; no code path needed the
  model's word over the transcript's bytes.

### upload comes off the "cannot be proven here" list
- The note read "serving is not executing" — true, and the requirement
  sentence already dealt with execution by saying it is an rce finding graded
  as one. What was left unproven was what this evidence settles: a file served
  back with its bytes intact **and** a content-type that makes those bytes
  script.
- The content-type is the entire discriminator, and it was the one thing
  nothing checked. The same `.svg` is inert as `text/plain` and runs in the
  uploader's origin as `image/svg+xml`; a `Content-Disposition: attachment`
  neutralises it again, so a response carrying one does not pass.
- `probe_upload` was calling a `.svg` served as `text/plain` an upload
  candidate — conflating "an active file type was stored" with "it is served
  as something a browser runs". It now records `served_ctype`,
  `served_disposition` and `served_active`, and no longer counts the
  `control-txt` upload (which exists to show storage works at all) as a
  finding. Its canary prefix now matches `NONCE_RE` so the gate can tie the
  served bytes back to the upload that wrote them.
- Directions asserted: inert content-types (`text/plain`,
  `application/octet-stream`, `image/png`, none at all), an active type served
  as an attachment, a 404 on the stored path, a fetch of somebody else's file,
  and an ordinary HTML page with no upload in evidence.
- **The count, stated once.** `websocket` and `smuggle` remain capped at
  `candidate` for want of a verifier - two, down from six: `lockout`, `enum`,
  `crlf`, `upload`, `method` and `race` came off that list. `xss` (no browser
  ships here) and `ssrf` (no out-of-band collector) are capped for reasons
  that are not labour, and `dos` is refused by construction; those three will
  not move. The count used to be restated in three places written at three
  moments, two of which were stale by the time the third was written, so
  `test_the_capped_set_is_exactly_what_the_docs_claim` now asserts the set
  against the matrix - a doc gate cannot read prose, but a test can hold the
  claim it makes.

### The reason a class is capped is data now, not prose
- `ProofSpec.cap_reason` holds why a ceiling is there: `"unimplemented"` means
  a verifier nobody wrote and the transcript already records what it would
  need; any other value is a reason labour will not fix. It was prose in
  `ARCHITECTURE.md` and `CHANGELOG.md` and drifted from the matrix in both -
  at one point the count was stated in three places written at three moments,
  two of them stale, and `ARCHITECTURE.md` also listed `ppoll` as capped for a
  real reason when `ppoll` is not capped at all.
- `argus proof <class>` now prints the cap and its reason, because an operator
  needs to know `proven` is unreachable *before* spending an engagement
  reaching for it. A refused class prints its refusal the same way.
- The selftest holds the prose to the matrix: the stated "N classes are capped
  at `candidate`" must equal the count, every unimplemented cap must be named
  in some doc, every real-reason cap too, and the "`x` and `y` are capped for
  a real reason" sentence may name only classes that really are capped - that
  last check would have caught the `ppoll` claim. What it does not try is
  reading *which* names in the first paragraph are the capped ones: the same
  sentence also names the classes that came off the list, so that is prose,
  and a gate that guesses at prose is worse than one that says what it cannot
  check.
- Two tests hold the code side: a ceiling without a reason is undocumented, a
  reason without a ceiling is a leftover from a freed class, and the
  `unimplemented` set is exactly the `verify_generic` set minus `ssrf`.
- Standing: `websocket` and `smuggle` capped for want of a verifier; `ssrf`
  (no out-of-band collector) and `xss` (no browser) capped for real reasons;
  `dos` refused by construction. `lockout`, `enum`, `crlf`, `upload`, `method`
  and `race` have come off.

- Re-reading `verify_header_injection` found the same shape of hole in it: "a
  control response does not carry it" was satisfied by any exchange that
  happened not to carry the header, including one to a different host. The
  control must be the same endpoint - this is the defect an earlier audit
  found when `_endpoint_shape` dropped the host and made two SaaS tenants one
  endpoint.
- Re-reading `verify_method_effect` after writing it found one more hole: the
  read-back compared against `req_text`, which includes the URL, so a `PUT` of
  inert bytes to `/up/<nonce>.txt` plus a directory listing echoing the
  filename graded `proven`. The effect proven was the server printing a path
  back. The nonce must come from the request **body** - that is what "the
  bytes it wrote" means.

### Probes and the matrix are now checked against each other
- `tests/test_probe_matrix_agreement.py`: drive each probe against the lab and
  grade the exchanges it recorded under its own class. Every verifier written
  here exposed a defect in the probe that feeds it, always the same shape - a
  probe reporting a signal it could not prove, because nobody read the
  requirement while writing it. Those were found one at a time by hand; this
  finds the class of them, and keeps finding it.
- Two directions, and no reading of the probe's English: on an endpoint the
  lab really is vulnerable at, some honest quote must reach `proven` (or the
  ceiling); on a clean endpoint, nothing may. The second is the direction that
  fails when a verifier is too loose rather than when a probe is too thin.
- It found two live defects immediately. `probe_redirect` sent no in-origin
  control, so its evidence could never satisfy "control recorded for the
  expected outcome" and stopped at `candidate` against a real open redirect;
  `probe_crlf` had the same gap. Both now send the control first and report
  its request id, because the requirement cannot be answered without it.
- It also corrected its author twice: `/hello` and `/safedirect` went in as
  clean endpoints and neither is - the lab reflects any `Origin` with
  credentials from its shared response helper, and `/safedirect` is the
  deliberate "filter that allows //host" bypass.
- Six stale assertions came out with it, three in `selftest.py` and three in
  `tests/test_lab.py`: the `crlf`, `upload` and `race` checks matched verdict
  strings containing the word "candidate", which those probes stopped saying
  when their classes stopped being capped at it. The tests were right about
  the behaviour and wrong about how they read it, so they now assert the
  structured output - `injected_header` and `control_id`, `served_active` and
  `served_ctype`, `overlapped` and `serial_statuses`. `AGENTS.md` carries the
  rule: assert a probe's fields, never its English.

### method comes off the "cannot be proven here" list
- The note read "a status difference is not an effect". True of the verifier
  it had; `probe_method` was already recording both effects this class can
  have, and both are pairs.
- `verify_method_effect` takes either path and emits the same two check names,
  so the floor means the same thing both ways. **A write that landed:** `PUT`
  answered 2xx plus a later `GET` of the same path returning the bytes the PUT
  carried — the status alone proves nothing, because an endpoint can answer
  201 and discard the body. **TRACE enabled:** `TRACE` answered with a value
  in the body that was only ever in the request's headers, which is
  cross-site tracing.
- Found while writing it: `probe_method`'s `put_verified` looked for the
  canary *filename* in the GET response body, while the body it wrote was the
  fixed string "argus method probe" — so a server that stored the file
  correctly returned bytes the check could not recognise, and a PUT that
  really landed read as unverified. The canary now goes in the bytes written,
  and its prefix matches `NONCE_RE` so the verifier can tie it back.
- Also fixed: `canary` was only assigned inside the PUT and TRACE branches,
  so an endpoint advertising `Allow: GET, DELETE` raised `NameError`.
- Six directions asserted, including a 201 whose body was discarded, a
  read-back of a different path, a TRACE echoing nothing the probe sent, and
  a plain 200-vs-405 status difference.

### crlf comes off the "cannot be proven here" list
- The note read "this system compares bodies, so it stops at a candidate".
  That was true of the verifier it had and the wrong place to stop: the
  transcript records response headers as a dict, so the real artifact was
  checkable all along.
- `verify_header_injection` requires three things on ONE exchange: the request
  carried a CRLF sequence followed by `name: value`, the response carries that
  header with that value, and **a control to the same endpoint does not**. The
  third is what makes it a proof — a server that always sends `X-Cache: MISS`
  would otherwise satisfy the second for a payload that happened to name
  `X-Cache`.
- `probe_crlf` now sends the control first, because the requirement cannot be
  answered without one. It also reports `control_id` and tells the agent to
  cite both.
- Four directions are asserted: the real split proves, a body-only reflection
  does not, a header the server always sends does not, and a bare `%0d%0a`
  with nothing after it does not. Two stray pages now grade `unproven` for
  crlf rather than `candidate` — there is no header in evidence to have been
  injected.

### Cross-family verification (`argus judge`)
- Ported from the orchestrator plane, with one rule the original did not need
  and this tree does: **a judge can dispute a finding or lower its severity,
  never promote one.** `grade` belongs to the deterministic matrix; letting a
  model's opinion raise one would put the strongest claim this system makes
  behind the weakest check it has.
- What it is for is the gap the matrix cannot see: whether the finding is
  filed under the right class, whether the title claims more than the bytes
  support, whether the severity is defensible. The judge reads the finding,
  the class requirement and the cited records — never the first model's
  reasoning, because the disagreement worth having is the one that reasoning
  would not produce. `--dry-run` prints the case file and makes no call.
- The judge comes from a family the author does not belong to, via
  `models.for_role("judge", exclude_family=...)`. If none is credentialed the
  command says so and exits: running the author's own family as its own
  reviewer would not be cross-verification, and `--judge-model` is refused on
  the same grounds.
- Three non-answers are recorded as *no verdict* rather than assent: prose
  with no JSON object carrying `agrees`, two objects that contradict each
  other, and a transport failure (which carries no `reason`, so it cannot
  read as a substantive dispute). Verdicts land in the transcript as a
  `cross_verification` event, inside the hash chain, and the session is
  re-sealed.
- Fixed while building it: a reopened session had no `secret_values`, so any
  command recording an event into an existing session died with an
  `AttributeError` instead of writing its entry.

### The decision controller (`argus next`, `next_action`)
- Ported from the ledger plane of the four-plane tree, rebuilt on this tree's
  own artifacts rather than a second state file. Seven ordered rules computed
  from `transcript.jsonl` and `findings.json`: an unrecorded proof already on
  disk, a candidate finding's exact missing check, untouched parameterised
  surface, a first-pass class never tried, a spent probe budget, a
  single-endpoint engagement, and report as the only exit.
- Available to the operator as `argus next <session>` and to the agent as the
  `next_action` tool, so "what does the evidence say to do" is a question it
  can ask instead of a thing it must remember across a context rollover.
- It invents nothing: an endpoint with no named input is never recommended,
  static assets are not surface, and a probe's output is graded only under
  that probe's own class. `probe_time` is deliberately unmapped — a latency
  measurement is consistent with sqli, with rce and with a slow database, so
  counting it as "this class was tested" would let a timing run stand in for
  a proof it cannot produce.
- Found a live defect in the proof matrix on its first run against the test
  corpus (below).

### Model table & providers (`argus models`)
- `argus/models.json`: provider, endpoint, credential variables, published
  USD/Mtok and the roles each model is listed for — data, so adding a model
  is a line, not a patch.
- `OpenAICompatClient`: an OpenAI chat-completions adapter behind the *same*
  `chat(messages, tools, system)` the loop already called, so a non-Anthropic
  model runs the identical loop, evidence gate and proof matrix. Tool calls,
  tool results and multi-block system prompts translate both ways;
  malformed tool arguments survive as a reportable call rather than
  vanishing.
- `make_client(cfg)` resolves the provider from the table; a model the table
  does not know goes to Anthropic (an unknown name is likelier a new Claude
  release than a typo for a local server).
- `--role planner|breadth|depth|judge|writer` with `--policy cheap|strong`
  picks a model by what the task needs; `--model` always wins. `for_role`
  can exclude a family, because a judge from the family that produced the
  finding is the same prior answering twice.
- Cost in `summary.json` and the report: recorded tokens × the rates in
  `models.json`, cache reads at a tenth of input, carrying the table
  version. A model with no line reports `usd: null` and the reason — a
  price that cannot be traced to something checkable is an invented number.
- OpenAI counts cached tokens *inside* `prompt_tokens` and Anthropic counts
  them separately; the adapter subtracts them, so a cached token is billed
  once, not twice.
- A credential is refused over plaintext `http://` unless the model's line
  opts in (`local`, for a loopback server).
- `--role-models` (team mode): lead=planner, recon=breadth, exploit=depth,
  report=writer, each resolved through the table under `--policy`. Off by
  default — four agents silently on four models is harder to explain than it
  is worth, and an operator with one credential would watch three of them
  fail. A pick whose credential is unset falls back to `--model` and names
  the variable. `summary.json` then carries USD per agent with the model each
  one used, because one rate cannot describe a run that spanned providers.
- `local` lists its own credential variables (`ARGUS_LOCAL_API_KEY`,
  `OLLAMA_API_KEY`) rather than `OPENAI_API_KEY`. It costs nothing, so cost
  ordering put it ahead of every paid model — and an OpenAI key is not
  evidence that a server is listening on this machine.

### Reports & artifacts
- `argus diff <before> <after>`: retest comparison at finding level —
  FIXED / STILL PRESENT (with severity drift + id pairs in `--json`) /
  NEW, matched on class+host+path+params so fresh lab ports still line
  up; warns when either input session has unverifiable findings.
- `argus report/findings/diff` re-validate findings before trusting
  them: bad rows are excluded from renders and marked `UNVERIFIED` in
  listings; report refuses non-session and empty-transcript dirs rather
  than fabricating a verifiable "session".
- `report.md` + `report.html`: severities, CVSS, auto-mapped CWE,
  OWASP Top 10 (2021) buckets, verbatim proof, embedded transcript
  excerpts, coverage, constraints, agent metrics, notes appendix.
  Dynamic code fences mean target bytes
  cannot break out and inject fake report sections.
- `report.sarif`: SARIF 2.1.0 — findings ingestible by GitHub code
  scanning / Azure DevOps dashboards.
- `findings.json`, `notes.md`, `meta.json`, `summary.json`,
  `agent*.log`, per-session `report.*`.

### Extensibility (data, not code)
- `argus/resources/wordlists/*.txt` → `wordlist_fuzz`
  (path/param/POST-body modes).
- `argus/resources/exploits/<id>/manifest.json` → `run_exploit`
  (scope-checked, timeout-bounded, env-scrubbed, `proof_marker` verdict).
- `<cwd>/resources/wordlists/` shadows bundled lists on any install;
  `<cwd>/resources/exploits/` requires `ARGUS_EXPLOITS_CWD=1`.
- Two bundled exploits demonstrate the manifest path:
  `lab-auth-bypass`, `lab-jwt-forge`.

### Ambient-trust hardening (cwd/env are untrusted input)
- `.env` whitelists credential keys only — `ANTHROPIC_BASE_URL` and
  `ARGUS_MCP_CONFIG` from a stray .env can no longer redirect the API
  endpoint (key exfil) or name subprocesses.
- Target client runs `trust_env=False`: env proxies and `~/.netrc`
  cannot silently re-route scoped traffic or attach Basic credentials;
  `--proxy` is the only proxy path.
- cwd `resources/exploits/` and cwd `mcp.json`/`.argus-mcp.json` are
  opt-in (`ARGUS_EXPLOITS_CWD=1`, `ARGUS_MCP_CWD=1`) — a planted
  manifest/config inside an untrusted checkout cannot execute commands
  through the model; wordlists keep unconditional shadowing.
- `--header`/`--header-file` reject control characters — a pasted CRLF
  cannot smuggle header lines onto the raw-send wire.
- Reads are memory-bounded everywhere: response bodies stream at
  BODY_CAP, subprocess stdout/stderr go through tempfiles with
  stream-searched proof markers, MCP frames cap at 4MB, wordlists and
  target files read only what is needed, persisted request bodies cap.
- Corrupt-input forensic tolerance: `verify`, `report`, `findings`,
  `diff`, `compare`, `sessions` and `--resume` degrade safely on
  malformed JSON, non-list findings, directory-swapped artifacts and
  broken meta.json — flagged as integrity signals, never tracebacks.
- MCP config errors (unreadable file, missing `command`) warn on
  stderr at run start instead of silently dropping servers.
- DNS-rebinding defense: `send()`/`send_raw()` verify the connected
  peer's real address (`network_stream.server_addr` / `getpeername`)
  and refuse private IPs when `--allow-private` was not given —
  the scope check's resolution and the socket's are separate answers.
- Boundary validation before budget: non-str/bytes bodies, non-dict
  headers and control-char methods are rejected before `sent += 1`.
- `record_event` detail values bound at 60k serialized chars each;
  LLM/gateway shapes (non-object JSON, non-str text/input/name/id,
  non-int usage counters) degrade to retries/zeros, never crashes.
- Target-controlled URLs are fuzz-safe: `crawl`, `js_recon`, `diff`,
  renderers, `_redact_url` and `_finding_key` all skip/degrade on
  `http://[bad`-class input instead of tracebacking.
- Model-supplied JSON types are coerce-hardened end to end: every tool
  param that flows through `.lower()`/`.strip()`/`int()` is str/typed
  before use, numeric clamps share `registry._ival` (wrong type falls
  back to the default instead of killing the tool call), and
  `record_finding`/`finish`/team tools gate clean on int/list input.
- Operator-input validation is fail-fast: `--proxy` scheme (incl. a
  clear socks5-needs-socksio message), `--resume` session-dir check,
  `--session-dir` not-a-file check, malformed `--mcp-config` lands
  per-server errors instead of crashing startup.

### Verification & packaging
- `python selftest.py`: 137 offline checks, including a documentation
  consistency pass — every tool, subcommand, proof class and **stated count**
  in the docs is verified against the code, and a count the docs stop stating
  fails rather than passing on nothing. It caught a stale tool-schema count
  in `docs/USAGE.md` on its first run, left behind by an earlier version.
- `python -m pytest tests/ -q`: 476 tests (unit + live-lab + loop +
  team + MCP client + MCP server + proof matrix + provider adapters +
  the decision controller + the cross-family judge + CLI +
  external-tool subprocess path +
  hardening regressions).
- nosqli graded `proven` on a page that only echoed the operator back.
  `verify_data_extraction` asked the *request* whether the query named its
  target — for a document store the only place it could ask, since a Mongo
  query has no FROM clause — but that answers "a payload was sent", never "a
  store answered". So `{"$ne": null}` reflected into a search page's "no
  results" line passed every check: operator in the request, status 200, body
  not a DBMS error. Now the *response* must carry a document shape (`_id`,
  `ObjectId`, `$oid`, or a JSON array of objects) that the request does not,
  which is response-side evidence of a read rather than request-side evidence
  of an attempt. Found by the decision controller re-grading its own
  transcript, which is the use it was built for.
- The selftest printed its results before the documentation gate appended
  its own, so a doc failure was counted but never printed: the gate said
  `130/131` and named nothing, in the one subsystem whose entire claim is
  that it names what is wrong.
- The proof matrix is tested in both directions per class: an evidence set
  that must grade `proven`, and one that must not. The second is the one that
  matters, and `test_every_class_refuses_a_benign_page` runs all 29 against a
  page with no bug in it. Four defects were found that way — three checks
  that passed without the claimant doing anything class-specific, and a
  relative `Location: /home` read as the host `home`.
- Fault-tolerance pass: every forensic reader (`verify`, `findings`,
  `diff`, `sessions`, `_reopen`, renderers) degrades malformed session
  artifacts to flags/warnings instead of tracebacks — fuzzed across
  dir-swaps, non-dict JSON, null fields and truncated files; locked in
  by `test_readers_survive_mutated_session_dir`. `dispatch` itself is
  total (every tool × wrong-JSON-type args returns a serializable
  dict) under `test_dispatch_total_on_malformed_args`.
- `python -m argus demo` / `demo --team`: scripted end-to-end on the lab,
  no API key. Six findings each, five graded `proven` and one honest
  `candidate`, and both acceptance criteria are demonstrated offline:
  `id` output with the probe nonce for rce, five rows from `users` for sqli.
  Both arms thread request ids out of each probe result the way a real agent
  does; a scripted demo that cites differently from a real run is not
  demonstrating the pipeline it claims to.
- `lab/vulnapp.py` `/ping` executes for real so the rce class is reachable:
  argv through a seven-command allowlist, never a shell, `cat` confined to
  the lab's fake filesystem, bound to loopback. A destructive payload returns
  `command not found`.
- Wheel ships skills + role prompts + wordlists + exploit manifests;
  CI (Ubuntu+Windows × Py3.10/3.11/3.12) runs pytest + selftest + a
  wheel-contents check.
