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
  `X-*-Token` are redacted at record time by HEADER NAME (transcript +
  logs) and re-redacted at render time (old sessions);
  `--proxy` remains the wire-fidelity path. `--secret`/`ARGUS_SECRETS`
  declare credential *values* (login passwords posted in bodies, quoted
  tokens) that `Session` redacts inside every artifact write — bodies,
  event output, notes, meta.json, logs — while the model still sees the
  real bytes.
- That sentence used to end "...and any `--header`-configured value are
  redacted at record time", which claimed value-based redaction for every
  `--header`. The code does not do that and **should not**: adding each
  header value to the scrubbed set would put `application/json` from
  `--header 'Accept: application/json'` into it and redact that string
  across every artifact, destroying evidence. Name-based redaction for the
  credential-bearing headers, plus `--secret` for a credential used
  anywhere else, is the design - `docs/ARCHITECTURE.md` always stated it
  correctly. A claim stronger than the implementation is the defect this
  repository exists to refuse, and the documentation gate cannot catch this
  one: it checks names and counts, not whether a sentence is true.

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
- `user -> LLM -> MCP -> tool`: 50 of the 60 tools served over
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
- **The count, stated once.** No class is capped at `candidate` for want of a
  verifier any more - zero, down from six: `crlf`, `method`, `upload`,
  `race`, `websocket` and `smuggle` all came off, after `lockout` and `enum`
  before them. The selftest's word map took "no"/"none" so the docs can state
  zero *explicitly*; a deleted sentence must not read as agreement. `xss` (no browser
  ships here) and `ssrf` (no out-of-band collector) are capped for reasons
  that are not labour, and `dos` is refused by construction; those three will
  not move. The count used to be restated in three places written at three
  moments, two of which were stale by the time the third was written, so
  `test_the_capped_set_is_exactly_what_the_docs_claim` now asserts the set
  against the matrix - a doc gate cannot read prose, but a test can hold the
  claim it makes.

### An adversarial audit of this session's own code, and what it found
Nine lenses read everything written in this session and reported 80 candidate
findings. The ones below were reproduced directly before being fixed. The
dominant shape was the one two earlier audits had already found twice: **a
check that passes without the claimant doing anything class-specific.** Five
classes graded `proven` on evidence containing no vulnerability.

**Credentials leaving the machine (the most serious).**
- `make_client` fell back to `cfg.api_key` when the picked model's own
  variable was unset - and that is the ANTHROPIC key, which
  `OpenAICompatClient` sends as a Bearer token to whatever host the table
  names. So `--model gpt-4.1` with no `OPENAI_API_KEY` shipped the operator's
  Anthropic credential to `api.openai.com`, and `--model local` shipped it to
  a loopback server. A missing credential is now an error naming the variable
  to set, and the error does not contain the key.
- `allow_insecure_base` is a statement about the model's OWN endpoint (a
  loopback server). It was applied to a base URL the operator supplied
  through `ANTHROPIC_BASE_URL` too, turning the plaintext-credential refusal
  off for any host.
- `GuardedClient.send_ws` recorded the handshake's response headers
  unredacted, so the target's `Set-Cookie` persisted verbatim into
  `transcript.jsonl` - and from there into a judge prompt bound for another
  vendor. It also stored `request_text` unredacted, leaving operator
  credential headers in cleartext one field over from the redacted dict.
  `send` and `send_raw` both redact; this third socket path did not.
- `judge.render_case` ships recorded bytes to a DIFFERENT vendor than the one
  that ran the engagement, and trusted that the recorder had already
  redacted. A demonstration leaked five shapes at once: an `api_key=` in a
  body, a password, a JWT, a `Set-Cookie` and a URL's userinfo. It now
  re-redacts everything it assembles - `argus report` re-redacts old
  transcripts at render for exactly this reason.
- `for_role` ignored credentials, and `local` is priced at zero, so cost
  ordering put it ahead of every paid model: `--role breadth` resolved to a
  loopback server that is almost never running. It now skips models whose
  credential is unset, with `usable_only=False` to ask what the table says.

**Five classes graded `proven` on benign evidence.**
- `nosqli`: any JSON API answering normally satisfied "documents came back",
  because `/api/posts` returns `[{"_id": ...}]` whether or not the `$ne` in
  the query did anything. A PUBLIC listing graded `proven` the moment somebody
  probed it. nosqli now has its own verifier: the operator must have CHANGED
  what the store answered, against a control to the same endpoint without it -
  either a refusal turned into access (the common real one, and what the lab
  has) or documents a control does not return.
- `method`: `verify_method_effect` checked that a write was answered and its
  bytes came back, and never that the endpoint SHOULD have refused it. So
  `PUT /api/note/7` returning 200 plus a `GET` of the same resource graded
  `proven` - which is every correctly working REST API. It now needs TRACE, an
  `Allow` list that omits the method, or the same method refused elsewhere on
  the same host.
- `race`: ANY non-2xx after the burst counted as "the limit refused it", so
  three read-only GETs and a later 404 graded `proven`. A 404 says the thing
  is missing, a 3xx that it moved, a 5xx that the server broke, a 429 that you
  were too fast; none of them says a limit was crossed. The refusal must now
  be a spent-action status with a body that differs from what the burst got.
- `lockout`: five requests to one endpoint counted, with no requirement that
  they carry a credential or that they FAILED. Five views of `/about` graded
  `proven`, and so did five successful logins - a lockout policy governs
  failures.
- `upload`: the fetch was not required to be on the same host, to come after
  the upload, or to follow an upload the server ACCEPTED. A copy on a CDN, a
  page recorded earlier, or a 403'd upload all graded `proven`.
- `smuggle`: `BOGUS_METHOD_RE`'s `G[A-Z]{2,}` matched `GET` itself, so any
  response containing `"method": "GET"`, `(GET)` or `method GET not allowed`
  satisfied the desync check. It now needs `G` prefixed to a real verb, and
  the effect exchange must not carry that verb in its own request - a server
  naming back what the request sent is an echo.

**The judge could be made to agree with itself.**
- `parse_verdict` coerced `agrees` with `bool()`, so a judge answering
  `"agrees": "false"` was recorded as AGREEING - any non-empty string is
  truthy. Of all the ways to be wrong there that is the worst, because it
  manufactures the assent the module exists to avoid. Only a real boolean or
  the words for one count now; anything else is no verdict.
- A scalar `missing` was iterated into characters, so `"missing": "a control"`
  became `['a', ' ', 'c', 'o', ...]` in the report.
- `pick_judge` returned a Claude judge when the author's model was not a
  table key, because `family()` answers `"unknown"` and excluding `"unknown"`
  excludes nothing. A family that cannot be named cannot be excluded, so it
  refuses and says so.

**The ledger invented work and starved itself.**
- Rule 1 tried line after line of a response until one graded `proven`, which
  is shopping for a verdict. It now cites the candidate plus its NEIGHBOURS on
  the same endpoint - where a control lives - and takes the first honest quote.
- One `next_action` call was measured at **over five minutes**: the cap
  bounded how many exchanges rule 1 examined, but each was graded against the
  whole transcript and `_pairs` makes that quadratic. Cost is now flat in the
  length of the run (~6s worst case at 2000 or 4000 exchanges, asserted in
  `test_the_ledger_cost_is_bounded_by_the_window_not_the_run`).
- Rule 2 never consulted the class ceiling, so a `candidate` in a capped
  class was a permanent fixed point: `close_proof_gap` forever, and every rule
  below it never ran.
- `_params` treated any body containing `=` as a form, so the ledger
  recommended probing parameters called `<?xml version` and
  `SELECT 1 FROM t WHERE a`.

**And two defects in the test corpus itself.** `/redeem` holds one coupon in a
class variable on a session-scoped server, so whichever test drained it first
left every later one looking at an endpoint with nothing to race for - which
read as a verifier regression until the counter was printed. The lab grew an
explicit `/redeem/reset` so the dependency is visible in the tests that need
it.

CI then found a third, and it was the better one: **`probe_race` and
`verify_concurrent_crossing` computed "the burst overlapped" two different
ways.** The probe compared wall-clock duration against the sum of per-request
latencies; the gate reconstructs each window as `[ts - elapsed_ms, ts]` and
tests intersection. On Windows runners `ts` is coarser than `elapsed_ms`, so
the probe announced a race the gate then refused - a probe claiming what the
gate denies, which is the exact failure the agreement layer exists to catch,
caught on a platform this machine cannot run. The probe now reports the
gate's own reconstruction and keeps the wall-clock figure beside it as
`wall_clock_overlap`, a measurement rather than a verdict.

The second one CI found over three rounds, and the end of it is a decision
rather than a fix: **`race` has no live proving case any more.** Three
Windows jobs failed because the burst was serialised; after the first fix they
failed because the windows intersected while only ONE request got past the
guard; after the second, because the agreement case had become a test of the
host's scheduler. Whether eight threads overlap on a loaded runner is a fact
about the machine, not about the probe or the gate.

So the class keeps its CLEAN live entry, which is deterministic, and its
unconditional both-direction assertions are synthetic: three overlapping wins
plus a 409 naming the action spent proves; a 404, a 302, a 500, a 429 or a 409
carrying the burst's own body do not. That is the whole requirement, asserted
without a clock. The table says so in place, so the case is not re-added by
somebody reading only the list.

### smuggle: the last class capped for want of a verifier
- The note read "this system sends the desync pair and reads the difference,
  which is a candidate". The difference was never the evidence, and the real
  artefact had been recorded all along: `send_raw` keeps `request_text`, so a
  request declaring both `Content-Length` and `Transfer-Encoding` is visible
  rather than collapsed into a headers dict, and it keeps responses from an
  extra read, so a reply that arrived with no request of its own is visible
  too - which is the requirement sentence almost word for word.
- `verify_desync` takes two shapes, both of which `probe_smuggle` already
  sends: **TE.CL**, where the smuggled request line is complete so the
  poisoned answer arrives on its own (an entry whose request method is `-`),
  and **CL.TE**, where the stray byte prefixes the probe's own next request
  line. Either way the check that carries the weight is a bogus method named
  back - `GGET`, `GPOST` - because a 4xx naming no method is a server
  disliking an ambiguous request, which is what it should do.
- Five directions asserted, plus the live pair in the agreement layer against
  `/desync` and `/desync-none`: the two real shapes prove, a polite 400 does
  not, a bogus method with no ambiguity does not, a desync response recorded
  *before* the ambiguity does not, and one on another endpoint does not.
- **The verifier raised instead of refusing**, which `grade()` reports as
  "evidence is readable" failing and so hides the real answer. It ordered
  exchanges by parsing `r<n>` out of the id and called `min()` on the empty
  result when no id matched that shape. Ids belong to the recorder; a
  verifier reasons about position and content. `test_no_verifier_raises_on_an
  _id_it_cannot_parse` now runs all 29 classes against entries whose ids are
  a string, an int and `None`.

### websocket: the package has a WebSocket client now
- The cap read "needs a real WebSocket client. This system compares the
  handshake only" - a missing capability, not a missing proof.
  `GuardedClient.send_ws` is that client: one masked text frame out, one
  frame in, close. It is the third socket-owning path here, because after a
  101 the connection stops speaking HTTP and `http.client.HTTPResponse`
  cannot read a frame - and it goes through the same guards as the other two
  (scope check with the connect-time rebinding re-check, rate limiter,
  request budget, recorded exchanges). No fragmentation, no binary, no
  second message.
- `verify_websocket_channel` checks three things, each ruling out a different
  wrong conclusion: the 101 answers the key the request sent (recomputed from
  the record, because middleware that 101s without the RFC 6455 challenge is
  not a WebSocket endpoint); the Origin is one the target does not own (a
  same-origin handshake succeeding is the endpoint working as designed); and
  the channel answered a frame carrying a nonce that frame sent (a 101
  followed by silence is a handshake, not a hijackable channel).
- `probe_websocket` sends a foreign Origin and a nonce frame, and reports
  `accept_ok`, `answered`, `canary`, `reply` and both request ids. It no
  longer tells the operator to "test message-level controls manually".
- The lab grew `/ws`, which echoes one frame and checks no Origin, and
  `/ws-strict`, the same endpoint with the check in place. Both directions are
  exercised against a real server, not only a fixture: seven synthetic cases
  plus the live pair in `test_probe_matrix_agreement.py`.
- What it does **not** claim, and the requirement does not either: that the
  answer contained anything the caller should not reach. Data taken over the
  channel is a different class and is graded as one.

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
- The count check had a bug of its own, found the moment the count reached
  one: its regex said `classes?`, which is `classe` plus an optional `s` and
  never matches the singular. A gate that silently matches nothing reports
  "docs say nothing" rather than passing, which is why it surfaced at all -
  the earlier fix that made count checks fail on no match instead of passing
  on nothing is what caught it.
- Two tests hold the code side: a ceiling without a reason is undocumented, a
  reason without a ceiling is a leftover from a freed class, and the
  `unimplemented` set is exactly the `verify_generic` set minus `ssrf`.
- Standing: nothing capped for want of a verifier; `ssrf`
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
- Ordering/consistency hardening in the deepest paths: transcript lines
  serialize before `_last_chain`/`_transcript` mutate (a non-JSON leaf
  can no longer open a chain gap); `send_raw` pipelined `reads` bounded
  to 8 (each holds a 3 s socket timeout); blocked-redirect events record
  the verbatim `Location` before `urljoin` parses it; `run_exploit`
  children lose declared `--secret` values from their environment the
  same way `run_external` children always did.
- Semantic-safety warnings on comparison commands: `argus diff` and
  `argus compare` warn when session targets resolve to different base
  hosts (a cross-host diff silently reads as all-fixed + all-new);
  same-host retests on a different port stay quiet and keep matching.
- Detection-quality pass on the tool surface: `fingerprint` now flags
  present-but-broken security headers (invalid XFO/XCTO, HSTS
  `max-age=0`, `unsafe-url` referrer-policy, wildcard/unsafe CSP) via
  `header_notes`; `graphql_introspect` flags the CSRF-able GET
  transport and runs a field-suggestion probe when introspection is
  refused (blind schema enumeration); `probe_csrf` counts
  `SameSite=None` cookies as weak; `probe_method` sends its TRACE
  canary regardless of `Allow:` advertisement (XST is frequently
  enabled without being advertised); `probe_ssti` counts engines that
  evaluate AND echo the raw payload (error-page style) instead of
  requiring the payload to vanish. Lab gains `/bad-headers`,
  `/graphql-strict` and `/hello2`; `probe_method` gets its first
  coverage. Selftest exercises all four new paths (bad-header notes,
  schema+GET transport, suggestion leak, eval-and-reflect SSTI).
- `render_html` tolerates a transcript entry carrying `response: null`
  (forensic readers degrade malformed artifacts, never traceback).
- Recon extraction quality: `js_recon` recovers endpoints from generic
  HTTP-client call shapes (`this.http.get`, axios instances,
  superagent `.request`) with a path-like restriction so `map.get('k')`
  can't flood leads; `fingerprint` cookie→framework matching resolves
  exact names before prefixes (`sessionid` no longer reads as
  rails/django-style).
- Evidence gate covers header-class findings: `record_finding` excerpts
  resolve against recorded response headers as well as the body/event
  output (CRLF-injected headers, bad security-header values and server
  disclosure can now be quoted verbatim; headers are redacted at record
  time so nothing secret becomes citable). `Session._evidence_text_of`
  shares one implementation with the verifier so gate and check cannot
  drift, and history compaction preserves `run_id`/`call_id`/`rid`
  keys alongside `request_id` so compacted exploit/MCP results keep
  their citable evidence ids.
- Team sizing is honest: `--max-workers` caps workers only (the lead no
  longer consumes a slot, so `--max-workers 1` still staffs the team),
  a rejected initial spawn surfaces on stderr instead of vanishing, and
  `--max-workers 0` is refused outright (zero workers means no probe
  tools and no `record_finding` anywhere).
- Methodology modules gain a second tier: the 27 entry skills stay small
  (confirm/falsify/rate), and 8 `*-refs.md` depth references — ported
  from the original ctf-v4 skill corpus — carry payload-level detail for
  confirmed classes: per-DBMS SQLi extraction channels + file/OOB
  escalation + WAF evasion, XSS context payload sets + exfil shapes, SSRF
  parser-bypass table + cloud metadata + internal pivot, CL.TE/TE.CL
  desync shapes + upgrade smuggling, deserialization magic-byte format
  identification, SSTI engine flowchart + escapes, NoSQL operator and
  aggregation-pipeline surface, and XXE content-type confusion +
  parameter-entity exfil. Entry skills route to their refs file via a
  "Route to depth" section; `test_skill_two_tier_wiring` locks the
  INDEX/pointer wiring.
- Artifact provenance: `meta.json` and `summary.json` record the
  producing `argus_version` (resume keeps the original and marks
  `resumed_by`); `argus sessions` lists it, `argus verify` reports it
  (text + `--json` `produced_by`/`resumed_by`), `argus findings` prints
  it as a context header, `report.md`/`report.html` carry it in the
  header, `argus diff --json` emits before/after context, and
  `argus compare` both warns on cross-build metric sets and prints
  `target_host`/`argus_version` as table rows + trailing CSV columns.

### An exemption list that no longer described anything
- `_NOT_TOOLS` exempts identifiers that LOOK like tools because they share a
  prefix with a tool family - `run_id` against `run_external`, `mcp_tools`
  against `mcp_list`. It had grown to thirty entries and a third of them were
  for words no doc contained any more, so the list had stopped describing the
  problem and become somewhere to add things. Ten are gone, and a check now
  fails when an exemption is named in no doc - the pressure is to prune at the
  moment an entry goes dead rather than to accumulate.
- The check cannot tell `probe_sqli` from `run_id` by syntax, so the list is
  the mechanism and not a workaround; that is written down next to it now, to
  save the next reader the detour I just took.

### The evaluation doc said nine, and the matrix said three
- `docs/EXPERIMENTS.md` stated that **nine** classes cannot reach `proven`.
  Three can't: `xss` (no browser), `ssrf` (no out-of-band collector) and `dos`
  (refused by construction). The other six came off that list as their
  verifiers were written, and nothing noticed, because the doc gate counted
  tools, classes, flags and test totals - not this. It is the denominator of
  every recall figure in the evaluation, so a stale nine would have understated
  the agent's recall by six classes.
- The gate counts it now, and checks that every unreachable class is named.
- It also stated the offline reproduction numbers - 6 findings on both demo
  paths, 5 `proven` and one honest `candidate` - as the shape every measured
  run is compared against, with nothing checking them. A test reads the
  numbers out of the document and runs both paths against the bundled lab, so
  the two cannot drift apart silently. Both match today.

### The agreement layer had the defect it exists to find
- `tests/test_probe_matrix_agreement.py` drives each probe against the lab
  and grades the evidence it recorded, in both directions. Its proving table
  covered **fourteen** classes - every class whose verifier had been written
  here - and the lab plants **nine more that nothing drove**. The table
  looked complete, which is why nobody counted it against the lab.
- Extending it to those nine, and then to `csrf`, found four real defects.
- **`verify_restricted_access` could not prove the variant its own alias is
  named after.** It required the refusal to be on the same path as the
  bypass. That holds for IP spoofing and is false for `X-Original-URL`,
  where the request line asks an allowed path and the header names the
  forbidden one - those paths cannot be equal. The shape the lab plants, and
  the one the class is called `x-original-url` for, was unprovable. It now
  accepts the rewrite variant when the header names exactly the path a cited
  exchange shows refused AND a control on the bypass path without the header
  answers differently - without that control a server that ignores the
  header proves the class.
- **`probe_xfh` never reached the restricted endpoint.** It put `restricted`
  into the URL's path component, so a caller passing a URL - which an agent
  naturally does - produced `http://host/http://host/admin` and got a 404.
  The probe's entire second half ran against a page that was never
  restricted, and the acl-bypass signal was silently lost. It normalises a
  path or a URL now, and records the no-header control the requirement needs.
- **`probe_enum` sent each username exactly once** while `verify_oracle`
  requires each answer to be observed more than once - and that verifier's
  docstring asserted the probe "sends a known and an unknown account, more
  than once". It did not, so `enum` could not be proven against any target.
  The probe repeats the bogus answer and its hits now, and says so when the
  difference does not reproduce.
- **`verify_state_change` accepted the reverse of what it asked for.** It
  gathered "reads carrying the excerpt" and "reads not carrying it" without
  comparing when either happened, so quoting the state BEFORE the write and
  citing a later read that no longer had it satisfied "the state changed
  between two reads". Any site whose two reads differ - a timestamp, a
  counter, a rotating banner - proved csrf. Measured: a real cross-origin
  write to the lab's `/api/config` graded `proven` on the quote
  `{"theme": "dark", "lang": "en"}`, the pre-write body. Both reads are now
  ordered against the write by recorded `ts`, with position as the fallback.
  This is the only one of the four in the loose direction, and the one that
  mattered.
- `probe_csrf` collected two of that class's four checks. It sends a foreign
  `Origin`/`Referer` now, takes a `read_url` to bracket the write with, and
  replays under both preflight-free content types - it tried only
  `text/plain`, which an endpoint parsing form bodies reads as empty, so the
  write was accepted and changed nothing.
- `_best_grade` offered only whole lines as quotes, and `ppoll` and `cache`
  are proven by quoting the marker alone: the verifier asks that the excerpt
  appear verbatim in the poisoning *request*, where the surrounding markup
  is not. Both read as probe failures while probe and matrix agreed. It
  offers marker-sized tokens too.
- Then two more, found by auditing the above an hour after writing it - the
  same lens, asked of my own fresh code:
  - The rewrite variant's control was matched on the request **path** and
    only had to **differ**. On any site with a 404 page that is free: send
    `X-Original-URL: /nope` to `/search?q=a`, cite `/search?q=b` as the
    control - it differs because the queries do - and cite the 404 as the
    refusal. The control must be the same request without the header, and
    must lack the quoted content.
  - `verify_state_change`'s two reads were not required to be of the same
    resource, so read `/home`, send the write, read `/about`, and quote text
    `/about` has always carried. `verify_unkeyed_input` already required the
    same resource because "a value appearing elsewhere on the site is not a
    cache entry"; the same reasoning applies here and was missing.
- `probe_cache` returned the same "no signal" for two different answers:
  the header is keyed (the defence working) and the cache was already warm
  (the probe could not decide, because nothing it sent ever reached the
  cache). The second is the common case on a live target - and is what any
  earlier reader of the page does to it. It says `undecided` now, naming the
  cache header it saw, and requires that header rather than inferring a
  cache from three identical bodies: a static page that does not reflect the
  header answers identically too, and calling that a warm cache would be a
  claim about infrastructure nothing observed. `tests/test_probes_unit.py`
  asserts both directions with a stub, because the lab serves no cache
  header and cannot reach the branch.
- And one in the lab, of the kind its own `/redeem/reset` comment already
  describes: `/cached` keys on path only and lives in a class variable, so
  whichever test reads it first decides what every later test is served.
  `probe_cache` sent its marker into an already-warm cache and recorded
  nothing carrying it - which reads as a probe regression and is a shared
  fixture. The lab has a `/cached/reset` now, and the case clears it first.
- Then the clean direction, which the module calls the one that matters,
  had the same asymmetry: 11 entries against the proving table's 24. Driving
  the nine new classes against a measured-clean endpoint found a fifth
  defect, and in the loose direction: **`verify_mass_assignment` accepted
  any response body as the read-back.** The check "a later read shows it
  set" asked only that the excerpt appear in some read and not in that
  read's request - true of any ordinary answer - so a write that merely
  *mentioned* `role` in its request and got a 200, paired with any later
  read, proved the class. Measured: `/api/order` drops every injected field
  and its probe says so, and massassign graded `proven` on the quote
  `{"order": 1, "owner": "user-1", "total": 11}`. The read-back must now
  carry the privileged field **and the value the write sent**, and that
  value must be absent from the read's own request.
- Closing that showed the plant had no read path at all: `_registered` was
  written by `POST /api/register` and never served, so the only evidence the
  field took effect was the write echoing its own input - exactly what the
  requirement refuses. The lab serves `GET /api/register/<id>` now, on its
  own path so the planted IDOR endpoint's 404s are unchanged, and
  `probe_massassign` takes `read_url` to do the read-back its own note has
  always told the reader to do by hand.
- One more in the same area, and a reminder that a gate's history is part of
  its design: `req_text` joins method, url, headers and body with spaces, so
  a form body whose FIRST pair is the privileged one (`role=admin&...`) is
  preceded by whitespace rather than `&` - and `PRIVILEGED_FIELD_RE`'s
  boundary was `[?&]`, so form-encoded APIs were unprovable for this class.
  Widening that boundary to whitespace makes `role=` match every ARIA
  attribute on every HTML page, which re-opened a real bypass once and has a
  test asserting it never happens again. So the form branch reads the request
  BODY alone, and only when the body looks like a form rather than markup.
- Every clean endpoint in the new entries was measured, not assumed. This
  module has twice asserted a lab endpoint was clean and been wrong, so the
  rule is to drive it first and keep only what grades below its ceiling.
  `method` and `xfh` get no clean entry: the lab answers TRACE on every path
  and honours `X-Original-URL` before it routes, so both are properties of
  the server rather than of an endpoint, and their refusals are synthetic.
- The coverage sentence is itself a count, and the first draft of it said 23
  while the table held 24 - the kind of unchecked number the documentation
  gate exists to refuse, except that gate counts tools, classes, flags and
  test totals and does not reach a count stated about a test module. A test
  does: it reads "N of the M probed classes" out of every document that
  states it and asserts both numbers against the tables.
- Then the two classes that had no row at all, missed for the same counting
  error one level up: `graphql` and `jwt` are not driven by a `probe_*`
  tool, so neither appeared in any coverage figure derived from the probe
  table. Both were already reachable, and driving them found two more
  things:
  - **`graphql` was absent from `decide.PROBE_CLASS`.** `graphql_introspect`
    sends the introspection query and the GET fallback under its own name,
    so those exchanges ARE evidence the class was tried - and they were
    attributed to nothing. A run could call it five times and `argus next`
    would still say the class had never been probed: the per-class budget
    never counted it, rule 6 never offered its evidence for grading, and
    `_tool_for_class("graphql")` fell through to `http_request`. That is the
    drift the decision controller exists to prevent.
  - **the agreement module could not have graded `jwt` even with a row.**
    `_exchanges` filters the transcript to entries carrying a response, and
    `jwt`'s first requirement - "this system minted the credential" - is
    made of the `jwt_forge` EVENT and nothing else. Measured: the same
    evidence grades `unproven` on the exchanges and `proven` on the full
    set. Grading sees the events now; quotes still come from responses.
- `jwt`'s recommendation was `http_request`, the LAST step of a chain, with
  no hint that the first two exist. A `CLASS_TOOL_CHAIN` names the chain
  (`jwt_decode` → `jwt_forge` → `http_request`), `_tool_for_class` answers
  with its first step, and the action carries the rest in `tool_chain`. It
  is deliberately separate from `PROBE_CLASS`: those two tools send nothing,
  so mapping them as evidence would mark the class tried on an offline call
  - the same reason `fingerprint` is not in there.
- The coverage denominator is the MATRIX now, not the set of classes that
  happen to have a `probe_*` tool. Counting against the tooling is precisely
  how `graphql` and `jwt` sat outside the module unnoticed.
- The proving direction now covers 27 of the 29 proof classes.

### The one document nothing checked was the claims table
- `docs/VERIFICATION.md` is the claim -> mechanism -> test table, the
  document a reviewer reads to check a claim rather than take it. It was the
  only `docs/*.md` missing from `selftest.py`'s `_DOC_FILES`, so **no check
  reached it** - not the tool names, not the flags, not the subcommands, not
  the stated counts. Bringing it in found two staleness bugs in it
  immediately: it put the dispatch test's coverage at 54 where the registry
  has 56 - and the sentence you are reading could not quote that stale
  figure with its unit attached, because the gate counts exactly that
  phrase - and it named `load_config` where a
  tool name was expected (it is the config loader, now an explicit
  exemption).
- The doc set was a hand-maintained tuple, which is the same error as
  counting a test table against the features that already have rows: a list
  that grows per document added by hand cannot reveal a document nobody
  added. The gated set is derived from globs now - `docs/*.md`, the
  top-level documents, `lab/*.md`, the four `argus/team/roles/*.md` worker
  prompts and the `argus/resources/*/README.md` data guides - so a new
  document either joins it or fails the gate.
- The role prompts are the part of that worth saying out loud: a worker is
  handed one the same way a probe class hands over a methodology module, so
  a new role prompt escaping the gate is guidance put in front of a model
  that nothing checks. `docs/` was derived first and the rest of the tuple
  stayed hand-listed, which is the same half-fix this session kept finding.
  Proved by planting a file under `lab/` and watching the check name it,
  then removing it and watching the gate come back green - a check's wiring
  and a check's logic are different claims.
- And the gate never checked the third column. 89 test names are cited
  across the live documents, and a renamed or deleted test silently unbacked
  whatever claim named it - in the one document whose entire value is that
  third column. Every cited name must now be a defined test or an existing
  test module, with a second check that the column has not quietly emptied.
  `CHANGELOG.md` stays out of scope on purpose: it is a historical record,
  so an entry saying a test was deleted names it correctly by its old name.
- And a repository invariant the gate did not hold: nothing large or opaque
  may be tracked. The biggest tracked file is about 150 KB and the package is
  standard-library-only by design, so a megabyte of anything is a mistake -
  and the mistake is close at hand. This working tree holds a 19 MB
  `ghidra.zip` and two 4 MB binaries, untracked and **not** ignored, so one
  `git add -A` writes some 27 MB of binaries into the history, where removing
  them means rewriting it. The check refuses archives and anything over a
  mebibyte; it does not decide what may be committed, only which shapes
  cannot be taken back. The examined count is in the label, so a checkout
  with no git reads as "0 examined" rather than as agreement.
- And the other half of that hazard, resolved on evidence rather than on a
  guess about what the author wants committed. `challenges/`, `cache/`,
  `solved/` and `tools/` have **zero commits on any branch** of this
  repository, so nothing in them has ever been intended as content - while
  `git add -A` would have committed all of it: the 19 MB archive, two 4 MB
  binaries, a tarball of this repo, and challenge `flag.txt` files. They are
  ignored now, which took the untracked set from about four hundred files to
  thirty-seven and left nothing matching "flag" in it. `knowledge/` is
  deliberately NOT ignored: it is committed on branch `ctf-v3`, so the author
  does keep it. Each line is one line to delete if a directory becomes
  content.
### The same hole on the MCP client side, with a worse symptom
- Having fixed the server's read loop, I asked the mirror question one
  module over: `argus/mcp.py`'s `_reader_loop` also wrapped `json.loads` in
  `except ValueError`, and a deeply nested frame from a server raises
  **RecursionError**. It already bounded `readline` at 4 MiB - the author
  had thought about a newline-free stream - so the gap was only the catch.
- The symptom is worse than the server's crash, and that is the part worth
  keeping. This runs in a thread, so **the process lived on**: the
  legitimate reply that followed the hostile frame was lost, and every later
  call waited out its full timeout and reported `timed out`, pointing an
  operator at the server or the network instead of at a dead reader inside
  this client. A dead component that still answers "timeout" is harder to
  diagnose than one that crashes.
- So the fix has two halves. Every parse failure is skipped rather than
  fatal; and `_rpc` now checks whether the reader is alive before blaming
  the server, because a dead reader and a slow server are the same silence
  and need different actions. Reverting the catch now produces
  *"the reader thread for 'hostile' is no longer running, so no reply could
  ever arrive ... This is not a timeout on the server's side"* instead of
  `timed out after 4s`.
- Driven end to end against `tests/hostile_mcp_server.py`, which answers
  `initialize` and then emits the hostile frame followed by a valid reply -
  the exact sequence. With the fix the reply arrives in 1.5s; without it the
  call fails at the timeout.

### The last sweep finding: the mapping was derivable after all
- I closed the sweep saying this one needed "a module-to-classes mapping
  that does not exist, and inventing one is how a taxonomy acquires a wrong
  row". The second half stands; the first was wrong. The mapping was already
  in the repository, written as the tools each module names.
- `load_skill` attached a proof requirement only when the module's STEM
  resolved to a class. Five gradeable classes have no `<class>.md`: `enum`
  and `lockout`, `jwt` and `massassign` (all in `auth-enum` and
  `auth-session`), and `method` (in `triage`). A worker that loaded
  `auth-session` for a JWT problem got the methodology and nothing about
  what proving `jwt` takes - and the requirement is only useful BEFORE
  probing, because it is the half that changes which request gets sent.
- Derived through the same tool-to-class table the ledger uses for evidence
  attribution, so the two cannot disagree, and `selftest` check 8 already
  reads that relation in the other direction. Measured after:
  `auth-session` carries `jwt`, `lockout` and `massassign`; `auth-enum`
  carries `enum`; `triage` carries `graphql` and `method`; a single-class
  module like `sqli` carries nothing extra.
- `http_request` and `probe_time` are excluded, and that exclusion is the
  whole difference between a derivation and a mess: `http_request` is the
  last step of the jwt chain and `probe_time` names no class at all because
  a latency measurement is consistent with sqli, with rce, and with a slow
  database. Both appear in modules that teach neither.
- Check 8b is the mirror of check 8 - every gradeable class is taught by
  some module, 28 of 28, with `dos` exempt because it is refused and has no
  methodology to teach.
- Two things the plants caught, both in my own new work. The selftest check
  calls `_also_taught` directly, so **removing the wiring from
  `load_skill` left it passing** - it proves the derivation exists, not that
  anything uses it; the pytest test is what catches that, and the pair is
  the coverage. And my assertion that the generic tools imply no class used
  `sqli` as its subject, which never mentions `http_request`, so it passed
  whether the exclusion existed or not. Third vacuous assertion of my own
  this session, found the same way as the other two: by planting the defect
  and watching nothing happen.

### A bounded shutdown that was bounded everywhere except its last line
- `MCPClient.call()` takes `self._lock` and holds it across `_rpc`'s
  blocking `q.get(timeout=...)`, a per-server timeout clamped at 600s.
  `close()` took the same lock unconditionally. The manager is shared by
  every worker thread, so `Coordinator.run()` - which bounds its join to 30s
  with the comment *"workers are daemon threads so a straggler can't
  hang"* - then called `close()` and blocked on the lock the straggler was
  holding. Every deliberate bound in that shutdown, defeated by its own last
  statement.
- Terminating the subprocess is precisely what unblocks the waiter: the
  server's stdout closes, the reader thread ends, and `_rpc` returns the
  dead-reader error instead of waiting out its timeout. So `close()` now
  tries briefly for the lock and proceeds without it - the lock protects
  request/response pairing, which has no meaning once the process is going
  away - and reads `self._proc` into a local first, because without the
  lock another thread may be clearing it.
- The test asserts the bound by actually holding the lock while calling
  `close()`, which is the only way to assert a bound rather than describe
  one. Measured with the plant: the unconditional version waited the **full
  30 seconds** the holder held it; the fix returns immediately.
- That closes every finding from the sweep except one, which stays open and
  measured: `load_skill` attaches a proof requirement only when a module's
  STEM resolves to a class, so `enum`, `jwt`, `lockout`, `massassign` and
  `method` - taught by multi-class modules - get none. 24 of 27 stems
  resolve. Closing it needs a module-to-classes mapping that does not
  exist, and inventing one is how a taxonomy acquires a wrong row.
- Sweep tally: 38 candidates, 19 survived three adversarial refuters,
  18 fixed across six commits, 1 left open with its measurement written
  down. Three were false positives in the proof gate - the gate accepting
  what it exists to refuse - and one was a false negative in the same
  function I had corrected earlier in the other direction.

### The wall clock was primary, and it is the one thing that can go back
- `_ordering` had `ts` primary with the recorder's sequence breaking ties
  only. An NTP or chrony step, a VM resumed from suspend, a container host
  resync mid-engagement makes `ts(read) < ts(write)` - and the post-write
  read then falls into neither `before` nor `after`, because `before` also
  requires the excerpt to be ABSENT and this read is the one carrying it.
  Measured: step the clock back two seconds and a csrf the lab really has
  drops from `proven` to `candidate`.
- A false negative, where **the first version of this same reasoning
  produced a false positive**. This is the second correction to one
  function, and it reverses the first: `ts` was made primary "so an
  explicitly stamped order still decides", which left the deciding to the
  only component that can move backward.
- The sequence cannot do either. `record_exchange` increments it under its
  own lock and writes it into the id before any author sees it, and the
  transcript is hash-chained - monotonic by construction and as
  authoritative as the stamp ever was. It is primary now; `ts` separates
  entries that somehow share one, and an entry still needs a usable stamp
  to participate at all, which is the fail-closed behaviour a hand-written
  finding depends on.
- The swap broke one existing test, and the break was the useful part.
  `test_csrf_needs_a_tokenless_cross_origin_write` creates `cross`, `late`
  and `tokened` AFTER the post-write read and then used explicit stamps to
  claim they came earlier - so it built entries in one order and asserted
  another, and the ids assigned in creation order quietly disagreed with
  both. Its own comment said why it needed the stamps. The ids now encode
  each sub-case's order directly, which is faithful and is the only thing
  the gate reads.
- Verified against the live lab as well as in fixtures: all 52 proving and
  clean cases still pass, so the ordering change did not quietly make a
  class unprovable. The new test also pins the property that could have
  been lost - a read RECORDED before the write cannot be the read that
  shows its effect, however it is stamped or cited.
- Two sweep findings remain unaddressed and are named here rather than
  closed: `mcp.close()` contends for a lock held across an in-flight RPC,
  defeating its own bounded shutdown; and `load_skill` attaches a proof
  requirement only when a module's STEM resolves to a class, so `enum`,
  `jwt`, `lockout`, `massassign` and `method` - taught by multi-class
  modules - get none. Measured: 24 of 27 module stems resolve, and those
  five gradeable classes have no module of their own. Fixing the second
  needs a module-to-classes mapping that does not exist yet, and inventing
  one is how a taxonomy acquires a wrong row.

### A report that said 1970, and three partitions closed while empty
- **The report printed a date of `1970-01-01` and a duration of about
  1.76e9 seconds.** `_reopen` initialises `started` to 0.0 and overwrites it
  only when meta.json exists, parses and carries a truthy `started` - and
  that `except: pass` is deliberate so a damaged session stays reportable.
  summary.json is written BY the renderer, so on the FIRST report of such a
  session both sources were absent and the header computed from zero. Fifty-
  six years, in a report whose whole job is to be checkable.
- Two figures, not one: I fixed the duration, wrote a comment claiming the
  renderer prints "unknown" for a negative value, checked, and it does not -
  it prints the number with an `s` after it. The `Date:` line one row above
  had the identical defect via `localtime(0.0)`. Both now say "unknown", and
  summary.json carries `null` rather than a number so a reader can tell "no
  measurable time" from "nothing recorded when it began". A healthy session
  is asserted to still show real figures, or the fix would simply have made
  every report say unknown.
- **`.env` silently dropped four of seven declared credentials.**
  `_DOTENV_ALLOWED` was hand-written with the three Anthropic names while
  `models.json` declares seven `api_key_env` values, so `OPENAI_API_KEY`,
  `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY` and `ARGUS_LOCAL_API_KEY` in a `.env`
  were ignored - an operator putting their key there got "no API key" and
  nothing saying why. The credential half is now DERIVED from the catalogue,
  which is the honest definition of the bound this allowlist exists to
  enforce: a provider's key becomes loadable when the catalogue declares it,
  a name the catalogue does not declare still cannot be set, and the
  Anthropic three stay listed explicitly so credentials never depend on that
  file parsing.
- **A test that depended on state it did not own.** `test_cache_probe` was
  the only reader of `/cached` that did not reset it first, and
  `probe_cache` reports `undecided` when it finds an entry it did not put
  there - so any new or reordered test that touches `/cached` first turns
  its assertion into a failure about someone else's request. Third instance
  of this shape in two days; the reset endpoint already existed.
- **And three partitions closed while they were still empty**, which is the
  cheapest moment: every registered tool is granted to some role card (56 of
  56 today - `next_action` was the one that was not, found by hand, and the
  plant reproduces exactly that), every CWE reachable by a gradeable class
  has an OWASP bucket, and the doc flag exemption is decided per line.
- **One dispute left unresolved on purpose.** Two sweep lenses independently
  flagged a 10ms sleep separating two `round(time.time(), 3)` stamps
  compared with a strict `>`. One verifier refuted it on nine Windows
  job-runs whose failures were enumerated in full; another reproduced it at
  22% by quantising the clock. Settling that costs a CI run; widening the
  gap to 50ms - three Windows ticks - costs 40ms. A simulation agreeing with
  me is the evidence that failed twice in this log, so the cheap defensive
  change wins over being right.

### Five more from the sweep, and two wrong fixes not made
- **A proven finding that vanished from the summary.** `_CWE` is pinned to
  the matrix by a test; the second hop to `_OWASP` was pinned in neither
  direction and was already two short. `CWE-1321` had no bucket, so a
  `ppoll` finding that graded PROVEN carried a CWE and then dropped out of
  the OWASP taxonomy the audit report is organised by - present in one,
  absent from the other. Bucketed, with `CWE-400` (dos, refused by
  construction) named as an explicit exemption, and the pair held by a test.
- That bucket choice is where I nearly invented something. I was about to
  write `CWE-1321 -> A08 Integrity Failures` as "the official OWASP
  mapping", checked it, and **OWASP's A08:2021 CWE list does not name
  CWE-1321 at all** - it names CWE-915, the parent weakness, which this
  table files under A04. So the child goes where the parent lives here, the
  disagreement is written in the comment, and the parent's row is left
  alone because relabelling it would change what already-written reports
  say.
- **`probe_time` called a transport failure a delay.** `slow = elapsed_ms >=
  threshold` read a duration and ignored the `status` in the same dict. On a
  read timeout the client records status 0 and keeps `elapsed_ms` as the
  whole wait - 15s against a threshold of baseline + 2800ms at the default -
  so a WAF that blackholes requests containing `SLEEP(`, `pg_sleep(` or
  `WAITFOR` rather than rejecting them reported a time-based candidate on
  every payload family at once. The defence manufacturing the evidence for
  the bug it defends against. Now requires an answer; a 500 still counts,
  because a database that errors after sleeping did sleep.
- **A precondition of mine, two commits old, was vacuous from the wrong
  directory.** `Path("argus").rglob(...)` in the board-reach test is
  relative to the process cwd, so running pytest from `tests/` yielded zero
  files and the assertion passed on the empty set - measured: 0 files from
  `tests/`, 39 anchored at the test file. That assertion is the stated
  precondition for the whole derivation above it, and it was exactly the
  vacuous-check shape the check was written to prevent.
- **The flag exemption said per-line and did per-corpus.** `foreign` was one
  set accumulated across every line of every gated document and subtracted
  globally, so a flag seen once on a curl or nmap line was excused
  everywhere - 11 names in this tree. Measured first: with the global union
  and with the per-line rule, `invented` is empty either way, so this closes
  a hole with no current occupant, which is the cheapest moment to close
  one.
- **A doc check that validated two names out of 29.** "docs name only real
  proof classes" extracted from one literal form, `argus proof <name>`,
  which across the whole gated doc set names `rce` and `sqli` and nothing
  else - and had no floor, so rewording those two usage examples would have
  left it reporting PASS while validating zero. Widened to `load_skill(...)`
  and to backticked names on lines about classes or skills (10 now), and
  floored, because a check that can validate nothing is not a check.
- **And the reverse direction, which I checked and did not "fix".** The
  obvious next move was to require every matrix class to be named in the
  docs. Measured: 24 of 29 appear in living documents, which looks like five
  undocumented classes - and then every one of the five turned out to be
  reachable. `cache-poisoning`, `info-disclosure`, `host-header` and
  `deserialization` are the names the docs use and **all four resolve
  through `spec_for` to their class**, and `massassign` is named in the
  README's diagram without backticks, which is why my pattern missed it.
  There was no gap. Had I shipped the check I was about to write, I would
  have pasted five class names into the documentation to satisfy a defect
  that did not exist.

### Two false positives in the proof gate, found by adversarial sweep
- Ran a six-lens sweep over the repository with every candidate finding put
  to three independent agents prompted to REFUTE it, surviving only on
  2-of-3. 38 candidates, 19 survived. The two that matter are **false
  positives in the proof gate** - the gate accepting what it exists to
  refuse, which is the worst defect class this repository has.
- **`massassign` graded `proven` on a read recorded BEFORE the write.** The
  check is named "a later read shows it set" and nothing established
  "later": `_pairs` yields both orderings of every cited pair and `_witness`
  keeps the best-scoring one. Reproduced exactly: a legitimately-admin
  account read from `GET /api/me` at ts 1000.0, paired with a
  `POST /api/register` at ts 1001.0 that sends `role=admin`, returns 200 and
  silently DROPS the field - the very case this verifier's docstring says
  was measured on `/api/order` - graded proven. What it accepted was the
  defence working.
- **`cache` and `ppoll` graded `proven` on a victim read recorded BEFORE the
  poisoning request.** `verify_unkeyed_input` is the `floor` check for both
  classes. It required the value in the poisoner's request, in the victim's
  response, absent from the victim's request, and one endpoint shape - never
  that the poisoning came first. So any value already on the page before the
  probe ran satisfied "the value reached a requester that did not send it".
  Reproduced: served a full second before anything injected it.
- Both are the same shape, and it is the one this log keeps recording:
  `verify_state_change` was fixed for exactly this, with a ten-line comment
  about quoting the pre-write state, and **the fix never reached its
  siblings**. Three verifiers pair exchanges; one had been corrected.
- Fixed with the ordering the recorder owns - `_ordering`, `ts` primary with
  the recorder's id sequence breaking ties a coarse clock cannot. No
  same-resource constraint added to `massassign`, deliberately: the field is
  set by `POST /api/register` and read from `GET /api/me`, so requiring one
  endpoint would refuse the real case.
- Verified in both directions and against the lab. Read-before-write now
  grades `candidate` naming the real reason; read-after-write still proves;
  citation order does not decide, because that order is the author's. All
  six proving and clean cases for `cache`, `ppoll` and `massassign` still
  pass against the live lab, which is what says the probes were not broken
  by tightening the gate.
- Both pinned, and both proved to fail without their fix: reverting either
  check reports `assert 'proven' != 'proven'` - the false positive itself.
- **A third false positive, from the same sweep: `lockout` could not see a
  progressive delay.** `verify_no_throttle` decided "none of them was
  refused" from status 429 and a body regex only, while `elapsed_ms` is
  recorded on every exchange and no verifier but
  `verify_concurrent_crossing` had ever read it. So the commonest real
  defence - back off a little more each time, no 429, no lockout wording -
  graded `lockout` PROVEN, and proven here means *this target has no
  lockout*: the gate asserting the absence of a defence that was sitting in
  the record it declined to read. Reproduced: ten 401s on `/login` whose
  recorded latency ramps 150 -> 600ms.
- The probe's half missed it for the reason this log keeps recording.
  `probe_lockout` tests the same property with a DERIVED ratio,
  `last3_avg > first3_avg * 3 + 150`, which on that ramp computes 550 > 750
  and says no. Two quantities describe one property and the derived one lost
  the signal; the verifier now reads the recorded one, as medians of the
  first and last third so one slow request cannot decide it, with an
  absolute floor so loopback noise cannot either. A genuinely flat series
  still proves - otherwise the class would just have been made unprovable.
- **And one check that passed on nothing.** `_spent_refusal` ends with
  `all(body != resp_body(w) for w in won)`, and `all()` over an empty
  sequence is True - so with no winner in the burst it returned True on the
  status allowlist alone, and the check whose stated job is "a different
  answer than the one the burst got" passed with nothing to differ from.
  The grade stayed `unproven` because another check fails independently, so
  this was not a false positive; it still fed
  `score = (len(burst) >= 2) + (len(won) >= 2) + bool(refused)`, where it
  hands an all-refused group a point it can win group selection with against
  a group that actually contains the race.
- Writing those two tests turned up the fixture doing the same thing one
  layer along. `ex()` in `tests/test_proof.py` never set `elapsed_ms` at
  all - the identical unfaithfulness its own docstring records being fixed
  for `ts`. It now takes one, deliberately NOT defaulted: `_window` reads a
  missing duration as a zero-width window that overlaps nothing, which is
  the fail-closed answer every existing race and ppoll fixture relies on, so
  handing them all a duration would quietly give close stamps intersecting
  windows and change what those tests assert. The key is absent rather than
  present and wrong, and the docstring says so.
- One finding from the sweep I could not reproduce and am not fixing: it
  claimed `lockout` proves on a bare 401 ramp, and my first attempt graded
  `unproven` on both checks. It reproduced once I put credentials in the
  request body - the "counted series" check requires a login shape - so the
  finding was right and my first construction was wrong. Worth recording
  because the obvious read was "the agent overclaimed".

### The simulation said 20/20 and the platform disagreed
- The coarse-clock race test from the entry below **failed on real Windows
  3.10, 3.11 and 3.12** - all three jobs, that one test, nothing else. It
  is removed, and the note in its place in `tests/test_lab.py` says why.
- So the 16ms simulation is not a faithful model of the platform, and
  measuring it 20 times did not make it one. That is the third time in this
  stretch that I established something locally and the platform disagreed,
  and the first two had the decency to be single samples - this one was a
  rate.
- What the arithmetic says should happen: `ts` lands on a ~15.6ms grid,
  `elapsed_ms` is precise, so a reconstructed window start is out by at
  most one tick; two independent errors is at most ~32ms; the gaps are 50ms
  each. It should hold. On the platform it does not, and I cannot close
  that gap from here. Ruled out on paper, not on the platform: the
  millisecond rounding in `ts` (adds <=0.5ms), the burst's own spread (it
  only moves `burst_end` later, which helps), and `_fire` returning before
  the burst completes (it cannot - the pool is drained with `list()`).
- The gaps in `probe_race` STAY. They removed a real failure mode in
  simulation, they cost 100ms, and they cannot make a non-race prove - the
  control must still be refused and must still overlap nothing. But their
  evidence is **simulation only**, and that is now written where it will be
  read rather than implied by a passing test.
- `race` stays out of the proving table. The honest state is unchanged from
  the revert: a mechanism that is diagnosed on paper, reproduced in a model
  that the platform has now contradicted, and not demonstrated where it
  matters. Diagnosing the rest needs the platform, and the vehicle for that
  is a throwaway branch that prints the recorded windows - not the mainline,
  and not another confident entry here.
- The pattern across all three is the same and worth stating once: a model
  I built to stand in for a platform agreed with me every time, and the
  platform did not. The model was mine; the agreement was not evidence.

### The race diagnosis: a coarse clock and two adjacent controls
- Diagnosed the failure the revert above could not name, and the pattern
  gave it away. `time.time()` on Windows resolves to 15.6ms up to Python
  3.12; 3.13 switched it to `GetSystemTimePreciseAsFileTime()` for better
  than 1us - CPython gh-63207, with a `versionchanged:: 3.13` note on
  `time.time` itself. That is exactly the CI split: Windows 3.10/3.11/3.12
  failed while Windows 3.13/3.14 and every ubuntu job passed. I had the
  release from memory and went and checked it, because a mechanism asserted
  from memory is the thing this repository refuses everywhere else.
- The gate reconstructs each window as `[ts - elapsed_ms, ts]`: `ts` is the
  recorder's wall clock, `elapsed_ms` comes from `monotonic()`. A coarse end
  with a precise duration puts the reconstructed START out by up to one
  tick. The serial control has to start at or after the burst's end, and the
  probe sent it the instant the burst returned - so that boundary had no
  slack, the control slipped behind it, and
  `verify_concurrent_crossing` found no control at all.
- Reproduced locally and deterministically by quantising the recorder's
  clock: at 16ms, `unproven` / `['no evidence']` - the CI message word for
  word. At 1ms and precise, `proven`.
- **The first fix looked sufficient and was not, and only measuring found
  that.** A 50ms gap before the baseline made one run prove at 16, 32, 48
  and 64ms granularity, and I nearly recorded "4x headroom" off those single
  samples. Ten runs at 16ms: 8/10. The next sample failed.
- The second separation is the real one. The gate also requires the control
  to overlap NOTHING, and the two controls are adjacent - each ~150ms wide,
  the second starting as the first returns. Round both stamps down by
  different amounts and the second's start slips behind the first's end:
  they appear to overlap each other, and that disqualifies BOTH. Separating
  them too gives 20/20 proven at 16ms and 20/20 at 32ms.
- Made local, like the clock defect before it: the new test quantises the
  recorder's clock to 16ms and requires the class to prove anyway. Failure
  rates with each half removed - 4 in 10 with only the pre-gap, 1 in 10 with
  neither - are recorded in its docstring as 10-sample estimates with wide
  error bars, because 1-vs-4 is not a real ordering and claiming it would be
  the same mistake one layer up.
- `race` stays OUT of the proving table in this commit. The mechanism is
  now diagnosed rather than guessed, but the note says not to re-add on
  local measurement alone, and this is local measurement. The new test ships
  first; if CI passes it on Windows 3.10-3.12, that is the platform evidence
  the table entry needs.

### race reverted, fourth round - and my evidence was the wrong half
- The flip failed CI on Windows 3.10, 3.11 and 3.12. Windows 3.13, 3.14 and
  every ubuntu job passed. Reverted, because the entry's own instruction
  said to delete it and say so rather than add a conditional skip.
- The part I got right is not the part that mattered. I read the earlier
  Windows failure as proof that the burst DOES achieve concurrency there -
  its first assertion passed, six requests returned 200 against one coupon -
  and that reading holds up:
  `test_the_race_window_can_be_made_deterministic` passed on the very
  Windows jobs that failed this case. The lab side is fixed.
- But concurrency was never the whole requirement, and I treated "the
  mechanism works" as "the class proves". The grade came back `unproven`
  with `missing: ['no evidence']` - which is `_best_grade`'s *starting*
  value, so not one quote from any recorded exchange graded above unproven.
  That is a different failure from the three before it, and I cannot yet
  name its cause. Checked and ruled out: the overlap reconstruction, which
  takes windows of `[ts - elapsed_ms, ts]` with a strict intersection -
  those are ~150ms wide and start within ~16ms of each other, so they
  intersect even when Windows' coarse `ts` makes them identical.
- So the honest state is a missing diagnosis, not a missing mechanism, and
  the entry says that instead of pretending the warning it replaced was
  satisfied. The earlier note predicted failure on somebody else's machine
  and I answered it with local measurement plus one reading of one CI run.
  Twice now. The note now says: do not re-add this on local measurement
  alone.
- What stays, all independently green: the barrier and the wide window in
  `/redeem`, their two tests in `tests/test_lab.py`, and the synthetic
  both-direction assertions in `tests/test_proof.py`. Coverage is back to 27
  of the 29 proof classes, and the changelog again needed no edit for that
  figure.

### The test written to catch a flake was itself flaky, at 13%
- The CI matrix is Python 3.10-3.14 and the local gate only ever ran
  3.14.6, so I ran the suite under the 3.12 and 3.13 interpreters that are
  also installed here. 3.12 passed. **3.13 failed** -
  `test_csrf_proves_when_the_recorder_s_clock_is_coarse`, the test added two
  commits earlier to make a Windows-only clock defect local.
- It was not a version defect. In isolation it passed 3/3 under 3.13, and
  the whole of `test_lab.py` passed under 3.13; only the full suite failed
  it. Measured directly instead of guessed: **3 failures in 24 isolated
  runs, 12.5%**, against a span of 0.136s across the probe's exchanges that
  predicts ~14% - because I coarsened the clock by QUANTISING it to one
  second, and a quantisation does not collide stamps. It guarantees they
  fall within a second; a run that straddles a boundary gets two values.
- So the defect class this test exists to catch was committed inside the
  test: a measurement that depends on where the wall clock happens to be.
  It went green on 11/11 CI jobs, which across ~10 samples at an 87% pass
  rate is about a 1-in-4 outcome. The green was luck, and I reported it as
  evidence.
- Fixed by making the clock a CONSTANT rather than a quantisation. There is
  no boundary to straddle and every stamp is identical by construction.
  Measured after: **0 failures in 30 runs**, ten each under 3.12, 3.13 and
  3.14.
- Both assertions re-proved live afterwards: removing the ordering tie-break
  fails it for its real reason, and removing the clock patch fires its own
  guard - *"the coarsened clock did not actually collide the stamps, so this
  test is not measuring the thing it exists for"*, naming the four distinct
  stamps.
- What actually found this is worth naming, because it was not the lens I
  reached for. Running the suite under three interpreters did not surface a
  version difference - it tripled the sample count, and a 12.5% flake that
  a single run had missed more than ten times showed up on the third pass.
  More samples, not more platforms.

### race is driven in the proving direction again
- The note standing where this entry now sits ended: *"if you re-add a live
  proving case here, expect it to fail on somebody else's machine."* It was
  right about the design it described, so this records what changed rather
  than quietly deleting it.
- Proving this class needed two things from the host. Both are now taken
  away from it. That every request is inside the window before any commits
  is guaranteed by a barrier in `/redeem`; that each recorded window is wide
  enough for two of them to be shown overlapping is guaranteed by the
  endpoint's own delay, which the barrier release does not shorten. The
  first attempt removed that delay, proved the race, and destroyed the
  `elapsed_ms` the overlap is reconstructed from - which is why the delay is
  now the thing a test asserts rather than an implementation detail.
- The decisive evidence was sitting in the Windows run that **failed**. Its
  first assertion passed: six requests returned 200 against one coupon. Six
  successes means all six were inside the window, so the burst does achieve
  concurrency on Windows. Only its *measurability* ever failed there, and
  measurability is the half that is now server-side. I had been treating the
  failure as evidence that Windows cannot overlap requests; it was evidence
  of the opposite.
- Measured before re-adding: 8/8 proven locally, six successes each,
  narrowest recorded window 157-173ms against a 150ms server delay, and the
  parametrised case green on six consecutive runs.
- Proved the entry is not passing vacuously: planting a lock around the
  check-then-act - i.e. fixing the lab's vulnerability - makes it fail with
  *"reached: unproven ... missing: ['no evidence']"*, while the CLEAN entry
  for the same class still passes, which is what a fixed endpoint should
  look like.
- The table entry carries the instruction for the next person: if this does
  start failing, the honest read is that a runner cannot get two requests in
  flight at once - delete the entry, put `race` back in `NOT_DRIVEN`, and
  say so. Do not add a conditional skip; that is how the case came to be
  testing the scheduler the first time.
- One class remains undriven in the proving direction: `dos`, refused by
  construction because its proof is the damage. That one is not coming back.
- Worth noting what this change did NOT need: **the changelog was not
  touched for the coverage figure.** Raising it used to require editing two
  historical entries into saying something they did not say at the time.
  That assertion was scoped to living documents a few commits ago, and this
  is the first change to collect on it.

### The local gate cannot see a platform defect, so one was made local
- Two of this stretch's CI failures were invisible here: 633 tests passed
  locally every run while Windows and ubuntu-3.14 jobs went red. The repo's
  own rule is to run the gate before accepting a change, which implies the
  gate is sufficient, and for timing and clock-resolution defects it is not.
  So the clock one is now a local test: the recorder's clock is coarsened to
  a full second, every stamp in the run collides, and the csrf proof has to
  survive it. It fails with the tie-break removed - *"every exchange in this
  run shares one timestamp, and csrf no longer proves"*. It is the test that
  would have caught me.
- It also asserts that the coarsening actually collided the stamps, because
  a clock patch that silently stopped applying would leave the test passing
  on nothing.
- **And writing it reproduced the defect class it was written for.** The new
  test passed, and it broke a sibling in another file: the
  proving-direction csrf case started failing - but only when run AFTER
  mine, never alone. Not a leaked clock patch. `/api/config` keeps
  `_usercfg` as a CLASS variable on a session-scoped server, so my write
  left `csrfmark` in it, and the next probe's own write then changed nothing
  NEW - so "the state changed between two reads" failed in a test that had
  nothing to do with the one that polluted it.
- Found only by running the plant. The test passed, the suite passed, and
  the contamination showed up because removing the tie-break made me run
  the two together. A new test is a new writer of shared state, and that is
  not visible in its own result.
- Fixed the way this lab already handles it: `/api/config/reset`, the same
  shape and the same reason as `/redeem/reset` and `/cached/reset`, and the
  test takes the state and hands it back in a `finally`. Re-proved
  afterwards that under the plant my test fails and the sibling does not,
  which is the isolation actually being claimed.
- CI is green on the tip: 11/11 on `6044010`, with the race window test
  passing on every Windows job now that the window stays wide.

### The barrier proved the race and destroyed the evidence for it
- CI also failed the test I had just added for the barrier -
  `test_the_race_window_can_be_made_deterministic`, Windows 3.12 - and the
  verdict names the defect exactly: *"inconclusive: the recorded windows do
  not intersect, so nothing was on the wire at once (burst 0.01s ...)"*.
  Its first assertion PASSED: all six requests returned 200 against one
  coupon. The race happened. The evidence that it was concurrent did not
  survive.
- I had replaced `time.sleep(0.15)` with the barrier, reading the sleep as
  the unreliable part. The sleep was doing a second job. A barrier releases
  its waiters together, so once released each request returns almost
  immediately and its **recorded** window collapses - and `probe_race`
  decides overlap by comparing the burst's wall time against a serial
  estimate, while the gate reconstructs it from `ts` + `elapsed_ms`. Both
  lose the signal. The barrier decides WHO is inside the window; the delay
  is what makes the window wide enough to be seen.
- So the sleep is back, barrier or not, and the comment at that line says
  why so the next reader does not make the same trade.
- The instructive part is my first attempt at guarding it. I asserted the
  burst/serial ratio - and the plant walked straight through it. Measured:
  without the delay the ratio is still **2.1x** on this host, because ~45ms
  of client-side overhead per request props it up; my threshold was `> 2`.
  The same accident is why the broken version passed locally in the first
  place.
- The assertion now reads the quantity the GATE reads, `response.elapsed_ms`,
  with a floor of 100ms. Measured both ways: the narrowest recorded window
  is ~161ms with the delay and ~11ms without it - a 15x collapse that is
  server-side, so the floor holds on a slow sandbox and a fast runner
  alike. The plant now fails here, naming the narrow windows, instead of
  failing in CI.
- Two lessons worth keeping. A fix measured only where the measurement is
  generous is not measured. And when a derived quantity and a recorded one
  both describe the property, assert the recorded one - the derivation is
  where the host's noise hides.

### CI was red for two pushes, and both failures were mine
- I reported CI as green. It was not. Querying it before flipping the race
  table showed `1e0b5ee` and `4869825` both **failed**, each with two jobs
  down, and the same two tests in both runs. Neither reproduced locally -
  633 passed here on every run - which is why nothing surfaced until I
  looked at the actual runs instead of carrying forward an earlier state.
- **`test_a_malformed_frame_does_not_kill_the_server`, ubuntu 3.14, twice,
  deterministic.** The hostile frame is `[`x100000 + `]`x100000, which is
  BALANCED, so it has two legitimate answers: a recursive parser hits the
  recursion limit and the frame is "invalid JSON", while a parser with
  headroom parses it into a deeply nested *list*, which is then "not an
  object". Both are the hardening working - the server survived and
  reported an error. Asserting only the first wording made the test a
  measurement of CPython's JSON internals, and 3.14 in CI answers
  differently from 3.14.6 here. It now asserts the property, and that the
  server reported *some* error at all. Verified by driving the server with
  a frame that parses to a non-object and confirming the message is exactly
  the one CI produced, rather than assuming the set covers it.
- **`probe_csrf` in the proving direction, Windows only, 3.10 then 3.12.**
  This one is a defect I introduced. I made `_ordering` fail-closed so that
  equal timestamps cannot be ordered - correct reasoning, wrong premise.
  The premise was "at the recorder's resolution those two events cannot be
  told apart", and the clock's resolution is not the recorder's: `ts` is
  `round(time.time(), 3)` and `time.time()` on Windows has a granularity
  near 16ms, so events tens of milliseconds apart tie there, land in
  neither `before` nor `after` under the strict comparisons, and a csrf the
  lab really has grades `candidate`.
- The recorder knew the order the whole time. `record_exchange` assigns
  `r1`, `r2`, `r3` from a counter under its own lock, before any author
  sees them, and the transcript is chained. So `ts` stays primary and the
  recorder's sequence breaks ties. This is **not** the "position" that
  function refuses: that was the index in `[entries.get(r) for r in
  evidence_ids]`, which is whatever order the claimant listed.
- Reproduced CI's failure deterministically rather than reasoning about it.
  Quantising the session clock to 1s ties all four stamps: with the
  tie-break, `proven`; with it removed, `candidate` and
  `missing: ['the state changed between two reads']` - CI's message word
  for word. A 16ms-granularity clock was not enough to tie them on this
  host, because requests here take ~47ms; a CI runner on loopback is
  faster, which is why the failure is Windows-only and intermittent.
- The security property is what the updated test now pins, because it is
  the one that could have been lost: the verdict must not move when the
  citation order moves, and the recorder's order must win over the author's.
  So the tied entries are graded cited forwards and backwards (same
  verdict), and then relabelled so the read carrying the new value was
  recorded BEFORE the write - which must NOT prove, in either citation
  order.

### A check that could only be satisfied by falsifying the record
- Having made the race window deterministic, I went to raise the proving
  coverage and could not. The check that guards the figure asserted every
  `"N of the M proof classes"` string in four files against the CURRENT
  value - and two of those strings are **historical changelog entries**,
  true about the day they were written. Raising the number meant editing
  them into saying something they did not say at the time.
- Isolated the mechanism rather than asserting it. Running the old loop
  with a hypothetical coverage of 28 produces four failures, two of them
  `CHANGELOG.md says 27`. A check satisfiable only by rewriting the record
  has frozen the measurement instead of verifying it.
- The anti-rot guard was worse. `assert seen >= 2` exists so a regex that
  stops matching cannot make the test pass forever on nothing - and it was
  **load-bearing on exactly those two frozen lines**. Measured: `AGENTS.md`
  matched zero times and this module matched zero times, while the module's
  own docstring *claimed* to state the figure. So the floor was met by the
  changelog alone: the living documentation could have dropped the claim
  entirely and the guard would not have noticed.
- Both halves fixed. The module docstring now states the figure in full,
  which makes its own long-standing claim true and gives the floor a second
  living source. The changelog is out of the assertion, with the reason
  written where the list used to be: a historical entry is a statement
  about its own time, and asserting it as a current claim is a category
  error that costs the ability to change the thing being measured.
- The floor now counts distinct FILES, not matches, so one document saying
  it twice cannot stand in for two documents still saying it. Proved both
  ways: changing the living figure reports *"docs/VERIFICATION.md says
  26"*, and dropping it from the docstring reports *"only
  ['docs/VERIFICATION.md'] states the coverage - the living documents are
  where this claim has to survive"*.
- The figure is now changeable without touching history, which is the
  precondition for driving `race` once CI has been seen green on Windows.
  That remains the open evidence, not this.

### The race window was a wager on the host's scheduler
- `/redeem` is the lab's TOCTOU endpoint, and its window was
  `time.sleep(0.15)` plus the hope that a burst lands inside it. That made
  the class provable or not according to the scheduler, not according to
  the probe or the gate - three rounds of Windows CI failures, and the
  recorded diagnosis of the second one is exact: *the windows intersected
  while only ONE request got past the guard*. The overlap happened; the
  decrement still beat the other checks. Two conditional skips later the
  case was testing the machine, so `race` was dropped from the proving
  direction with that reason written down.
- The reason was right and the requirement was wrong. `/redeem/reset`
  now accepts `parties=N`, which arms a barrier **inside** the window -
  after the `coupons > 0` check, before the commit. Every request that
  reaches the barrier has already passed the guard, so when it releases
  they all commit. The overlap stops being a wager.
- What is left to the host is only whether N requests get in flight inside
  the barrier timeout, which is far weaker than interleaving
  microsecond-wide critical sections. And an under-filled barrier releases
  its waiters *together* on timeout, so two in flight still proves - the
  degraded case degrades into the thing being measured rather than into a
  flake.
- The timeout is 8s, deliberately below the client's 15s read timeout.
  Measured at 20s first: every request died at status 0 and the failure
  read as a network fault rather than as a burst that never assembled.
- Opt-in. No `parties`, no barrier, and the sleep path the demo and any
  manual run take is untouched - asserted, because a barrier that became
  the default would hold a single redeem for the whole timeout.
- Measured 6/6 proven across repeated trials with the barrier armed, and
  the plant that matters reproduces the Windows failure locally: remove the
  `barrier.wait()` and the test reports `assert 1 == 6` - one winner out of
  six, which is the CI diagnosis word for word. Arming it by default trips
  the opt-in test on elapsed time.
- `race` is still out of the proving table. The cause is addressed and
  measured here, but the evidence that mattered was Windows CI behaviour
  and this host cannot produce it; flipping the table on a local 6/6 would
  be the fourth round of the same mistake. The barrier is the precondition,
  recorded as such.

### The same shape a third time: BOARD_TOOLS
- `mcpserver.py` states the principle plainly - *"A manifest entry a host
  can never call successfully is a lie in the catalogue"* - and withholds
  `BOARD_TOOLS` plus the two `mcp_*` tools. Three tests assert that nothing
  withheld reaches the manifest. All three check the same direction, and it
  is the direction you only change on purpose.
- The direction that rots by neglect is a new team tool that needs
  `ctx.board` and never gets declared. Measured, the cost is spread over
  four readers rather than one: `mcpserver` advertises it to a host that
  can never call it, `loop` offers it to a single-agent run that has no
  board, `argus check` lists it in the tool surface, and `--tools` accepts
  it as a valid name. Then `_board(ctx)` raises RuntimeError.
- Measured today: eight implementations reach a board, every one of them is
  declared, **no gap**. So
  for the third time in this stretch there was nothing to fix, only a
  partition to hold - and that is itself the finding. This repository
  reliably checks the direction that cannot rot and leaves the other one to
  care.
- The set is derived from the implementation rather than hand-listed, and
  the check asserts its own precondition: that `argus/tools/team.py` is
  still the only tool module reaching a board (`loop.py` touches
  `ctx.board` once, for a mode label). A derivation that silently
  under-counts is exactly the failure this check exists to prevent.
- Four assertions, each proved to fail on its own. Undeclaring
  `spawn_worker`: *"['spawn_worker'] need a board but are not in
  BOARD_TOOLS, so the MCP manifest advertises them, a single-agent run is
  offered them, and calling one raises RuntimeError"*. Declaring a tool
  that does not exist: the subset assertion names it. Renaming `_board` so
  the derivation matches nothing: *"the derivation found no board-needing
  tools at all, so it has stopped measuring anything"*. Letting a second
  module reach a board: the precondition names all three files.
- Writing this entry, the gate refused my own prose twice: for naming a
  subcommand that does not exist, and for a bare count it correctly read as
  a claim about the tool total. Third time this stretch. A gate that only
  ever catches other people's drift is not being run.

### The shared prompt was a single-agent playbook given to four roles
- `build_system` was unconditional, and `SYSTEM`'s numbered method is
  imperative throughout - "fingerprint() the target, crawl() the surface",
  "record_finding() IMMEDIATELY", "finish() with", "call next_action()".
  Every team role got it verbatim while `dispatch` enforces the role's
  card, so the prompt instructed what the gate denied:

  | role | instructed to call, gate denies |
  | --- | --- |
  | recon | `record_finding`, `next_action` |
  | exploit | `crawl`, `fingerprint`, `js_recon`, `next_action` |
  | report | `crawl`, `fingerprint`, `js_recon`, `record_finding`, `next_action` |
  | lead | `finish`, `record_finding`, `next_action` |

- Proven by calling it, not by reading: `dispatch` with each role's real
  grant answers `{"error": "tool next_action is not available to role
  'recon-1'"}`, and the same for exploit and for the lead.
- Two measurements decided which half was wrong. Every role CARD's own
  prompt is exactly consistent with its own grant - zero mismatches across
  all four - so the shared block is the broken one, and widening the grants
  to match it would dissolve the role separation that is the point of team
  mode. Recon maps, exploit proves, so only exploit records: that is a
  design, not an oversight.
- `next_action` was the worst of them because **no card held it at all**,
  the lead's included, while `decide.py`'s docstring names two readers of
  the ledger - the operator, and "the agent itself, via the `next_action`
  tool". For every team agent the second was false. The instruction also
  fires at the three moments the agent most needs an answer: unsure what is
  worth doing, a class has stopped producing signal, the engagement looks
  finished. A worker spent a turn there and got a refusal naming its own
  role, with no fallback named.
- So the lead now holds the ledger - deciding what happens next from
  recorded evidence is what a coordinator does - and every other role is
  told the truth instead: which tools it has, which of the method's tools
  it does not, that those steps belong to another worker, and how to hand
  them over. Both the disclaimer and the hand-over tools are **derived from
  the grant**, because a hand-written list is what drifted in the first
  place.
- That derivation immediately caught my own fix doing the same thing. The
  hand-over sentence named `emit_lead()`, which the `report` role does not
  hold - the half-fix, in the paragraph written to fix the half-fix. The
  hand-over tools are now filtered against the grant too.
- Three checks, each proved to fail on its own. Dropping the grant block:
  *"recon is instructed to call record_finding and cannot, with no
  statement in the prompt that it cannot"*. Rendering the disclaimer in
  single-agent mode, where every tool is granted and nothing is
  withheld: `'YOUR TOOLS.' not in ...` fails. Taking the ledger back off
  the lead: the grant assertion names the frozenset it is missing from.

### The probe-attribution denominator came from the mapping it checked
- `PROBE_CLASS` maps a probe tool to the class it tests, and the ledger
  reads it for three separate things: the per-class budget, rule 6's offer
  of evidence for grading, and `_tool_for_class`. It was checked in one
  direction only - every entry names a real tool. That direction cannot rot
  on its own, because you only add an entry on purpose.
- The direction that rots is a probe landing in the registry attributed to
  nothing, and the ledger then reporting its class as never tried however
  many times the run called it. Not hypothetical: `graphql_introspect` was
  exactly this, and `decide.py` already records the three things it cost.
  The entry was added. **Nothing was added that would catch the next one** -
  the old check's denominator came from the mapping being checked, not from
  the registry, which is the same shape as the count-checking gate's own
  blind spot earlier in this log.
- Measured: 27 registered `probe_*` tools, 26 attributed. The one gap is
  `probe_time`, and it is *correctly* excluded - a latency measurement is
  consistent with sqli, with rce, and with a slow database, so attributing
  it would let a timing run stand in for a proof it cannot produce. So
  there was no defect to fix, only a reason held by a comment.
- The comment is now `UNATTRIBUTED_PROBES`, data with a stated reason, and
  the pair is a partition a test holds: every registered `probe_*` tool is
  either attributed to a class or named as excluded with the reason. Both
  options are one line; being in neither is the bug.
- Proved each of its three assertions can fail on its own. Dropping
  `probe_time`'s exclusion: *"['probe_time'] send requests but are
  attributed to no class"*. Attributing a tool in both places: the
  disjointness assertion names the overlap. Shortening the reason to
  "too noisy": *"probe_time is excluded without a stated reason"*.
- Audited the rest of `decide.py` and found nothing. `counts` is keyed
  `(endpoint, class)` and `recorded` `(class, endpoint)` - opposite orders
  in one function, which is a readability hazard - but all five use sites
  swap correctly, so I left them alone rather than churn a module whose
  every branch cites a past failure.

### Three refusals arriving as one, and the wrong one
- `LeadQueue.push` returned `False` for three unrelated reasons - the
  pipeline is closed, the lead is a duplicate, the 10000-unique-lead bound
  is spent - and `emit_lead` reported all three to the model as
  **"duplicate of an existing lead"**. The queue's own docstring said only
  "Returns False when it duplicates an existing one", which is where the
  caller got the wrong label.
- The reason a worker is shown decides what it does next, so this is not
  cosmetic. Told "duplicate", a recon worker correctly goes looking for
  DIFFERENT surface. Against a closed pipeline that burns its remaining
  turns producing leads nobody will ever pull; against a spent bound it
  reports the surface as covered when nothing about that lead was wrong.
  And an operator reading the transcript saw "duplicate" in all three
  cases and concluded recon had been thorough. Same defect class as the
  MCP reader two entries up: different causes, one indistinguishable
  signal, different actions needed.
- `push` is now `offer(lead) -> str`, returning `""` or which refusal
  applied. **Renamed on purpose**: a reason-returning `push` would have
  left `if not leads.push(lead)` reading a non-empty reason as success, so
  a missed caller had to fail loudly rather than silently invert. It
  immediately did - `selftest.py` had its own `q.push` call that my grep
  over `argus/` and `tests/` never saw. A bool return would have passed
  that site and quietly stopped checking anything.
- The model-facing half mattered as much as the return value.
  `registry.py`'s tool description still told the model "Duplicates are
  dropped automatically", i.e. the same half-truth in the one place it is
  read *before* the tool is ever called. It now names all three refusals
  and what each one means for the next move.
- Pinned at both levels and proved it can fail: collapsing the three back
  to `"duplicate"` reports `assert 'duplicate' == 'closed'` and
  `assert 'duplicate' == 'capacity'` from the queue tests, and the two new
  tool-level tests assert the prose the model actually reads - that it does
  NOT say "duplicate", and that a spent bound says the surface is not
  covered.
- Audited the rest of `leads.py` while in there and found nothing else:
  the heap's `(priority, counter, lead)` tuple never compares two `Lead`s
  because the counter is unique, `pull` polls at 1s so `close()` is always
  noticed, and the unguarded `pending`/`closed`/`drained` property reads
  are single atomic operations feeding a display. Model-supplied `params`
  and `priority` reach `Lead` only through `emit_lead`, which coerces both
  - so the frozen dataclass cannot be handed an unhashable `params` list
  that would raise inside `offer`.

### An invariant two readers depend on, held only at a distance
- Audited `argus/team/board.py` and `argus/ratelimit.py`, both of which I
  had named as unexamined. **Both are clean, and that is the finding** -
  `board.py`'s lock discipline holds, `del lst[:-N]` really does keep a
  tail, and `RateLimiter.wait` holds the lock *across* its `time.sleep` on
  purpose: that is what makes the limiter global instead of per-thread.
- What the audit did turn up is not a bug but a shape. `board.py` reads
  `session.findings` behind `isinstance(f, dict)`; two sibling readers do
  not - the dedup loop in `record_finding` and the team coordinator's final
  per-agent metrics pass both call `.get()` on a row without checking it.
  That asymmetry is the half-fix shape this log has recorded nine times, so
  I went looking for the live crash.
- There is none, and the reason is worth writing down: `findings.json` is
  operator-editable, so a stray scalar is a real input, but `_resume`
  filters non-dict rows on load and every live session goes through it. The
  invariant protecting those two readers lives in a *third* function, and
  nothing failed if it went away.
- The tempting fix - filter in `_reopen` too - is wrong, and measuring it
  is what showed why. `argus judge` rewrites `findings.json` from the list
  `_reopen` loads, so filtering there would silently **delete** an
  operator's malformed row instead of preserving it for `argus verify` to
  flag. The two halves are deliberately opposite. So the right change is
  not code at all: it is a check, because an invariant held by distance is
  one nobody is told they broke.
- Pinned in both directions, and proved it can fail. Removing `_resume`'s
  filter: the test reports `assert 5 == 1`, and the dedup loop it protects
  raises `AttributeError: 'str' object has no attribute 'get'` - measured,
  not assumed, because the docstring claims that consequence. Adding a
  filter to `_reopen`: `assert 1 == 5`. Four other readers of the same list
  (`sanitized_findings`, `findings_bad`, `findings_overgraded`, and the
  `findings` subcommand, which prints `<malformed entry> UNVERIFIED`)
  already honour the contract, each deliberately.

### One malformed frame killed the MCP server and skipped the seal
- `argus mcp-serve` is the `user → LLM → MCP → tool` path the project is
  graded on, and its read loop wrapped `json.loads` in `except ValueError`.
  Deeply nested JSON raises **RecursionError** - measured: `"[" * 100000`
  does - which is not a ValueError. It escaped the handler, left the
  `for line in stdin` loop, and killed the process.
- The second half is worse than the crash. `_finalize()` runs **after** that
  loop, so the escape skipped the seal entirely: one malformed frame ended
  the engagement with the session unsealed and unrendered - the exact
  failure the disconnect path immediately below it was written to prevent.
  A guard placed after a loop protects nothing on the paths that leave the
  loop sideways.
- Every parse failure is now a `PARSE_ERROR` reply, and a frame is bounded
  at 4 MiB: `for line in stdin` reads until a newline, so a host sending
  megabytes without one buffered all of it - the same reasoning this package
  already applies to a planted wordlist, applied to the one input another
  process writes.
- Checked by reverting the catch and watching the server die with
  RecursionError, and the test asserts an ordinary `tools/list` still
  answers - hardening that eats the server is not hardening.

### A defence on the vendor-egress path that could not fire
- `argus judge` sends a case file to a **second model vendor**, and `_scrub`
  is the last thing between that text and the wire. It called `_redact_url`
  on the whole blob - and `_redact_url` only works when the entire string is
  a URL. Measured: `"target is http://admin:SuperSecret123@10.0.0.5/app
  now"` came back **unchanged**. A line that looks like a defence and never
  fires is worse than none, because it is counted as one.
- A prose-level pattern replaces the password of any
  `scheme://user:pass@host` anywhere in the text now. Only the password:
  the host and the username still read, because a judge asked whether a
  disclosure happened needs the shape of what leaked, not its value - and
  this is the one place where scrubbing beats preserving evidence, since
  the text crosses to another vendor.
- Two shapes are deliberately untouched, and asserted: a credential-free
  URL, and a bare `@` in prose. A scrubber that mangles either is a
  scrubber that corrupts the case the judge is asked to rule on.
- Also measured and left alone, with the reasoning recorded rather than
  guessed: `Cookie:` values are not in `_SCRUB`'s shapes, and a bearer
  token under 16 characters is below its floor. The first is covered on the
  first line - `cookie` is in the client's sensitive-header set, so a
  transcript never carries the value - and the second floor exists to stop
  the pattern eating ordinary prose. Both are second-line gaps whose first
  line holds; saying so is more useful than widening a regex until it bites.
- Checked by removing the fix and watching the test fail
  (`assert 'SuperSecret123' not in ...`).

### The target's password was still in three writers
- Redacting the target's userinfo in `meta.json` and `notes.md`'s header
  covered the URL FIELDS. The credential also travels as **free text**: the
  loop logs `session <id> -> <target>`, and a note or an event detail can
  quote the URL. Measured with the earlier fix in place: `notes.md`,
  `transcript.jsonl` and `agent.log` each still held it - and `agent.log` is
  sealed into the chain and shipped with the bundle. Ninth half-fix in this
  stretch, two commits after the first half of the same leak.
- One change covers every writer: the target's **password** joins the
  declared-secret set, so everything that already scrubs declared values
  handles it - notes, events, logs, report. Fixing `_log` alone would have
  been the tenth half-fix.
- Two deliberate limits, both load-bearing. The **password only**: scrubbing
  the username by substring would mangle prose, since a user called `admin`
  would redact the word everywhere. And free text keeps **other** URLs'
  userinfo, because a target leaking `http://svc:pw@db/` in its own HTML is
  a disclosure finding and the note describing it is the evidence - a
  blanket scrub would eat the finding it was meant to protect, the same
  shape as redacting `Transfer-Encoding` out of a desync. The existing
  4-character floor still applies, so a 3-char password stays out rather
  than redacting innocent bytes everywhere.
- Checked by disabling the fix and watching the test name the files
  (`['notes.md', 'transcript.jsonl'] == []`) - before trusting it, this
  time.

### A sweep test that claimed four fixes and covered one
- The four redaction leaks were each found alone, so the obvious follow-up
  was one end-to-end guard: plant a distinct secret in every
  operator-controlled channel, drive the real client against the lab, sweep
  every file in the session dir. Its docstring said it would have caught all
  four together.
- Then the rule this stretch had adopted - revert the fix and watch the test
  - and it **passed with the fix reverted**. Measured one by one: it catches
  the target's userinfo (reverting that fails with
  `{"meta.json": ["userinfo"]}`) and catches **none** of the other three,
  because httpx drops a header named `"Authorization "` before the request
  is built, so the recorded header dict is empty and the planted shape never
  reaches the recorder. The test ran on a path where the condition it checks
  cannot occur.
- A test whose docstring overstates its reach is worse than no test: it
  stops the next reader writing the one that is needed. The docstring now
  states what is covered, what is not, and why, and points at the
  unit-level tests that hand the redactors those shapes directly - each of
  which was checked for failure when it was written.
- This was the eighth time in this stretch that my own instrument or claim
  was the defect, and the first time I caught it **before** committing,
  using the habit the earlier seven paid for.

### The target's basic-auth credentials persisted in two artifacts
- `session.py`'s own docstring said basic-auth in a URL "persists nowhere;
  the scope guard only ever needed the host". It was true of the request
  path, which `_redact_url` covers, and false of **the one URL an operator
  certainly types with credentials**: the target, which argus takes as a
  positional argument. `argus run http://admin:SuperSecret123@10.0.0.5/app`
  wrote the password verbatim into `meta.json` - sealed into the hash chain
  and shipped in the bundle - and into the `notes.md` header.
- A footnote worth keeping: the first draft of this entry passed the target
  as a long option rather than positionally, and the documentation gate
  refused it, because no parser accepts that spelling. The gate this stretch
  kept extending caught its own author inventing a flag, in the paragraph
  describing a credential leak - and then refused the correction too, since
  naming the wrong spelling in prose is indistinguishable from using it.
  The same tension as quoting a stale count: a gate that validates names in
  prose cannot be shown the name it rejects, so the entry describes the
  mistake instead of spelling it.
- Both are redacted now, at all three writers (fresh session, resume
  meta-rewrite, resume notes-create), and the host survives because a
  reviewer must still see what was tested.
- Writing it redacted without touching the comparison would have made
  **every resume fail**: `_resume` tested `old_target != target`, so the
  stored marker would never equal the live credentialled URL. Both forms are
  accepted now, which also keeps a session written by an older build
  resumable.
- Fixing `meta.json` first left the same credential in `notes.md` - the
  eighth half-fix in this stretch. So the test sweeps **every file in the
  session dir** rather than the writers that were changed, and asserts the
  resume still works and that a genuinely different target is still refused.

### Raw-wire redaction was defeated by the header name
- The lens that found two credential leaks in an earlier session is "what
  leaves the machine", and `httpclient.py`'s redaction had not been asked
  that here. `_redact_request_text` keyed on `": "`, and the header names on
  that path are **model-supplied input**. Two shapes walked an operator
  credential into `transcript.jsonl` and the shareable report:
  `Authorization:Bearer tok` - the space after the colon is optional in
  HTTP, so `": " in line` was False and the line persisted verbatim - and
  `Authorization:Bearer tok: `, a name carrying the colon and the value, so
  `partition(": ")` took the token as part of the NAME and the name did not
  match the sensitive list.
- Reachability, stated rather than implied: neither is reachable through
  `send_raw`'s own composition, which always writes `f"{k}: {v}"`. Both are
  reachable through the header pairs a model hands it - which is precisely
  what that path exists to send. And a credential the operator did not
  declare with `--secret` has **no second line of defence**, because
  `Session._redact_obj` only knows declared values; the name check has to
  hold on its own. It splits on the first colon now and folds a
  colon-bearing name.
- A declared secret inside a non-sensitive header value was the other
  hypothesis and it is **not** a leak: `Session._redact_obj` replaces
  declared values by substring across the whole request structure, which was
  checked before changing anything.
- The test asserts the other direction too, because it matters more than
  usual here: `Transfer-Encoding` and `Content-Length` must survive
  untouched. Those lines ARE the desync evidence, and a redaction that ate
  them would destroy the finding it exists to protect.

### The scope boundary disagreed with itself about multicast
- `scope.py` is the module the "authorised testing only" claim rests on, and
  nothing in this stretch had looked at it. Measured against a **public**
  target with `allow_private` off: `localhost` and `10.0.0.1` were refused,
  and `224.0.0.1` and `239.255.255.250` - the SSDP group, a local-network
  address - were allowed. `is_multicast` was simply not in `_ip_private`.
- Stated at its real size: the host still has to be in scope, so this was
  **never an allowlist bypass**. It was a disagreement about what counts as
  private inside a boundary whose job is to refuse before any bytes are
  sent. One predicate closes it.
- Two measurements of mine were wrong on the way here, and both are in the
  test file now so the next reader does not repeat them. The first put the
  private host in as the TARGET and read `10.0.0.1` being allowed as the
  gap - but `allow_private = allow_private or target_private` is deliberate,
  because labs run on loopback; the risk path is a public target plus a
  private host discovered later. The second was the hypothesis that
  IPv4-mapped IPv6 was the hole: `::ffff:127.0.0.1` looks like the classic
  way past a loopback check, and `ipaddress` already reports it as loopback
  and `::ffff:169.254.169.254` as link-local. Believing it would have meant
  "fixing" something that was not broken, so it is asserted instead - which
  also catches a stdlib change if one ever lands.
- The second half of the new test is the half that keeps the fix honest: a
  real public address must still pass, or the repair is just a stricter gate.

### An audit of this session's own changes, and two holes in them
- The rule this repository already records is to audit a gate adversarially
  before trusting the green suite, because a passing test asserts what its
  author thought of. Nine verifiers and six probes changed here; the audit
  had been done in spots and not over the whole diff. Over the whole diff it
  found two.
- **An ordering a claimant controls.** `_ordering`, added for the csrf
  before/after check, fell back to an exchange's POSITION when the session
  carried no `ts`. But the cited list is built as
  `[entries.get(r) for r in evidence_ids]` - its order is whatever the
  finding's author wrote. A claimant listing the ids in a chosen order would
  decide which read came "before" the write, and the tie-break on equal
  timestamps was position too. It is fail-closed now: no recorded time, no
  before/after, no proof - and two exchanges sharing a stamp are equally
  unusable, because at the recorder's resolution they cannot be told apart.
- **A transient error as the control.** `_acl_header_changed_the_answer`
  asked for the same URL, no ACL header, and the quoted content absent. A
  flaky 500 on that URL satisfies all three for a reason that has nothing to
  do with the header: the page failed. The control must be a real answer
  (2xx/3xx) now.
- Three things about the instruments, kept because the next session will
  otherwise repeat them. My own test
  `test_csrf_ordering_falls_back_to_position_without_timestamps` existed to
  **protect** the positional fallback; it asserts the opposite now and says
  where I was wrong. `ex()` - the fixture helper behind 178 tests - built
  exchanges with **no `ts`** while a real session always has one, making it
  unfaithful to the recorder for every time-ordered requirement; it stamps
  in creation order now, and the csrf test's writes carry explicit stamps
  because, left to creation order, a write built after the read it supposedly
  caused is recorded after it and correctly refused. And a
  `replace(..., 1)` of mine matched a function-local `import json` instead of
  the module header and broke the file - the one place in this stretch where
  I omitted the `assert s.count(old) == 1` guard I had used everywhere else.

### deserialize comes off the "cannot be proven here" list
- I had written that this class needs "a second code-execution path, which
  `CLAUDE.md` blocks", and cited the rule at the reader twice. Reading the
  rule again: *"Code execution is proven with `id; echo <nonce>` and stops
  there"* constrains **what counts as proof**, not whether the lab may have
  a second door into the executor it already has. The refusal was
  over-cautious, and citing policy is not the same as checking it.
- `/import` routes a gadget's command into the **same** bounded executor
  `/ping` uses - seven commands, no shell, no path component, `cat` confined
  to the fake tree - so it adds no capability this lab did not already have.
  A gadget carrying no runnable command still gets the
  `InvalidClassException` parser error, so "a surface is not execution"
  stays a measurable distinction rather than a sentence, and both the clean
  and proving cases are live in the agreement table.
- The probe also had to carry a nonce: it sent `os.system ['id']`, and the
  class is proven the way rce is - identity line AND a token tied to this
  probe. My first attempt used `_marker("deser")` while `NONCE_RE` is
  `\bargus[a-z0-9]{4,24}\b`, so the token was unrecognisable as the probe's
  own and the class sat at a candidate with its nonce in plain sight on both
  sides of the exchange. Found by measuring the grade, not by reading the
  diff.
- The proving direction now covers **27 of the 29 proof classes**. `dos` is
  refused by construction and `race` is evidenced by wall-clock concurrency,
  which this repository has already decided not to assert against a clock.

### A run that died looked exactly like a run that found nothing
- Running the baselines produced the finding, and it is the thesis's own
  claim turned on itself. The first trial stopped on
  `Anthropic API error 400` before a single successful call, and the session
  it left behind was **sealed, verifying** (`argus verify` prints OK) and
  carried `findings: []`, `grades: {}`, `requests: 0`, `llm_calls: 0` and
  `cost: 0.0`. The terminal error reached `agent.log` and the loop's return
  value - **never `summary.json`**. For any reader who did not open the log,
  a run that never started was indistinguishable from a clean run that found
  nothing. The artifact did not overstate; it understated by omission, which
  the promise does not cover and should.
- `compare`, `sessions` and the report all read `summary.json`, so such a
  run folded into an arm as a legitimate trial with zero proven. Measured:
  paired with one real trial that found four, `median_low([0, 4])` reported
  **0** - the failed run halved the arm. The summary records the error now,
  `compare --by-arm` excludes those trials from every median, and it NAMES
  them on stderr with the error text and marks the arm `(n=1, 1 failed)`.
  Dropping a trial silently would be the same defect one level up.
- The error survives a re-render: it is not in the renderer's recomputed-key
  set, so `argus report` on a failed session carries it forward.
- Then the half-fix shape, one more time, in my own fix. The finding itself
  said "`compare`, `sessions` and the report all read `summary.json`" and
  only `compare --by-arm` was taught. Measured on a dead-run fixture:
  `argus sessions` printed `findings=0 requests=0 dur=4s v1.0.0 sealed` with
  no hint, `sessions --json` carried no `error` key at all so a script could
  not tell, the A/B table showed `findings 0` with no error row, and the
  report - the document a reviewer actually opens - was indistinguishable
  from a clean one.
- All four say it now. `sessions` appends `FAILED: <error>`, the A/B table
  leads with a `FAILED` row (truncated to the column, because an API error
  is a sentence and an untruncated one made the table unreadable), the CSV
  gained an `error` column, and the report carries a banner **above every
  figure** - each number below it describes a run that may not have
  happened, so the reader has to be told before reading the table rather
  than after.

### Two promises about dependencies that nothing kept
- `AGENTS.md` says "No new runtime dependencies without strong cause" and
  `CLAUDE.md` says an engagement should not fail on a pip install. Both were
  prose, enforced only by a reviewer noticing. One `import requests` in a
  probe keeps the suite green on a developer machine that happens to have it,
  ships a wheel that cannot run, and surfaces mid-engagement - the worst
  possible moment for an import error.
- Every import in the 39 shipped modules is now checked against the standard
  library plus the dependencies **declared in `pyproject.toml`**. The
  allowlist is derived rather than hard-coded to `httpx`, because declaring a
  dependency is a deliberate act that should pass and importing one nobody
  declared is what must fail.
- The claim was true when checked - no third-party import beyond `httpx` -
  so this is a guard rather than a repair, and it was proved by planting
  `import requests` in `argus/scope.py`, watching the check name the module,
  and restoring the file.

### The default model retires this month
- `DEFAULT_MODEL` was `claude-sonnet-4-5`. It is **deprecated and retires
  2026-11-30** - seventeen days from the day this was found - so every run
  without `--model` or `ARGUS_MODEL` pointed at a model that stops answering
  this month, and `.env.example` offered it as the example to copy. The
  value was right when written and nothing checked it against anything.
- `models.json` carried no Claude 5 entry at all, so a run on the current
  generation reported **no cost** - the honest fallback working, and still a
  thesis chapter with an empty cost column. It now prices
  `claude-opus-5-5` (4.00/20.00), `claude-sonnet-5-5` (2.00/10.00) and
  `claude-haiku-5-5` (0.10/0.50), each from the published figures, with
  `priced_as_of` on the table so staleness is visible rather than implied.
  Haiku 5.5's note records what this schema cannot hold: 0.10/0.50 applies
  to prompts up to 100K tokens and 0.50/2.50 above, so one price pair
  under-reports a long-prompt run fivefold.
- The two previous-generation rows were checked rather than assumed.
  `claude-haiku-4-5` at 1.00/5.00 **matches** the published figure and is
  untouched. `claude-opus-4-5` is still served, and its 15.00/75.00 is left
  exactly as recorded with a note saying why: no current published figure
  covers that model, and every current Opus is cheaper, so changing the
  number would be a guess dressed as a correction.
- A retirement date cannot be checked offline, so the deprecation is DATA in
  the table - the same move `cap_reason` makes in the proof matrix - and the
  gate refuses a default that is unpriced or marked deprecated. A second
  check refuses a model named in a document that the table does not price,
  since a run on one reports no cost at all. Both were tried against the
  shapes they must catch before being trusted.

### `strong` reached past the current generation, and my own change showed it
- Pricing the Claude 5 family made a latent assumption visible.
  `for_role(..., "strong")` ranks by **price as a proxy for capability** - its
  own docstring says "takes the most expensive" - and that proxy held only
  while each generation cost more than the last. With the current generation
  priced below the previous flagship it inverted: `strong` picked
  `claude-opus-4-5` at 15/75 over `claude-opus-5-5` at 4/20, an older model
  at 3.75x the cost, for `planner` - the role whose own description in
  `models.json` says a wrong call there costs the engagement rather than
  money.
- Fixed without inventing a capability ranking, because nothing here is
  entitled to claim one model is smarter than another. `superseded_by` records
  the **published successor relation** as data, and role selection drops a
  model whose successor this machine can call. It degrades rather than
  stranding a role: if the heir cannot be called, the older model is still the
  answer, the same reasoning as `usable_only`.
- Role selection also never consulted the deprecation added in the previous
  commit, so a fallback could have reached `claude-sonnet-4-5` - the model
  that stops answering on 2026-11-30. It is excluded from every policy now
  and still reachable by explicit id, because an operator may have it pinned.
  That is the half-fix shape again: the data went in and only one reader
  learned to use it.
- The first attempt at this silently did nothing. `superseded_by` went into
  the JSON and the `Model` dataclass dropped it, so the measurement after the
  edit was identical to the measurement before - caught only because it was
  measured rather than assumed.
- `test_strong_policy_reaches_for_the_strong_models` asserted the literal id
  `claude-opus-4-5`, so it was asserting the old behaviour and made a
  legitimate table change look like a regression. It checks the property now -
  an Opus, not superseded, not deprecated - which is the same lesson as
  asserting a probe's structured output instead of its verdict prose.

### A green suite that failed on correct output
- Widening the CI matrix to 3.13/3.14 doubled the Windows jobs, and the next
  run failed - the first CI failure in this stretch, and not a regression.
  `test_reopen_report_findings_verify` asserted
  `"Duration" in text and "1970" not in text`, guarding against an epoch
  timestamp rendering as `1970-01-01`. The lab binds an ephemeral port; the
  run drew **51970**; the finding URL read `127.0.0.1:51970/item?id=1`; and
  `51970` contains `1970`. The report was correct and the assertion was not.
- The epoch bug shows up in exactly one place - the rendered `Date:` line -
  so the test looks there now. An assertion that reads like a precise claim
  and is really a substring search over a whole document fails on correct
  output, which is worse than not asserting: it spends a reviewer's
  attention on a report that was right. Verified in both directions - a
  `1970-01-01` Date line is still caught, and the ephemeral port no longer
  trips it.
- It was the only bare numeric substring assertion of this shape in the
  suite.

### `.env.example` named seven of the ten variables the code reads
- It is the file an operator copies to `.env`, so completeness is its whole
  purpose. `ARGUS_SEAL_KEY`, `ARGUS_MCP_CWD` and `ARGUS_EXPLOITS_CWD` were
  absent, and the seal key is the one that matters: an operator setting up a
  keyed engagement learned nothing about it from the configuration file.
  All three are real-env-only by design - `_DOTENV_ALLOWED` is a five-name
  list - and for the seal key that design is load-bearing: a `.env` inside
  an untrusted directory must not be able to choose the HMAC key for the
  transcript chain, or planted config could produce a chain that verifies.
  Each now carries that reason.
- The existing check ran the other way round, that a variable named in a
  document exists. The reverse one holds the file to the code now, which is
  the fifth time in this session that one direction of a correspondence
  turned out to be the whole check.
- My first measurement of this was wrong and said the file listed one
  variable: the grep anchored on `^[A-Z]` and so skipped every commented
  line, which is where six of the seven live. The instrument was the defect,
  not the file.

### Two tools the model could call that no document mentioned
- The gate asked that a tool named in a document is real. It never asked
  that a real tool is named - and two were not: **`read_findings` and
  `list_exploits` were registered, callable, and named in no document at
  all.** Not the reference in `docs/USAGE.md`, not the README, not a
  methodology module. A reader of the documentation could not learn they
  exist, and the model's own description was the only place they were
  written down.
- Both are now in `docs/USAGE.md` beside the other utility tools, with what
  they are for: `read_findings` is the read side of `record_finding` and the
  cheap way to see what a run already has before probing a class again, and
  `list_exploits` is how you learn what `run_exploit` can be pointed at
  without reading `resources/exploits/` by hand.
- The reverse check now holds it. One direction of a correspondence is half
  a check, and this gate has now been wrong that way four times in a row -
  about test tables, probe coverage, the document set, and methodology
  modules naming their own tool. The asymmetry, not the instance, was the
  defect each time.

### The package claimed a Python range CI did not prove
- `requires-python = ">=3.10"` is open-ended: pip installs on every version
  from the floor up, so each one is a support claim. The matrix tested
  3.10-3.12 while the development interpreter here is 3.14 - so **3.13 was
  claimed by the package metadata and tested by nobody**, and 3.14 only ever
  locally. A claim exceeding its evidence is the one thing this gate exists
  to refuse, and it was sitting in the packaging metadata where the gate
  never looked.
- The matrix runs 3.10 through 3.14 on both OSes now, and `selftest.py`
  holds the claim to it with two conditions: the `requires-python` floor
  must be one of the tested versions, and the matrix must have no gap - so
  adding a new top version without the one below it fails the gate. Both
  halves were checked against the shapes they are meant to catch (a skipped
  3.13, an untested floor, a missing matrix, a floor that is not a `>=`
  bound) before being trusted.

### The modules the model reads were out of step with the probes
- `load_skill` puts a methodology module in front of the model when the
  signal points at a class, so stale guidance there costs findings directly.
  Four probes changed contract in this session - `probe_csrf` and
  `probe_massassign` gained the `read_url` read-back, `probe_enum` repeats
  its differential, `probe_xfh` records the control - and six modules still
  taught the old shape. An agent following `csrf.md` would have stopped at a
  candidate on a class that is now provable, because nothing told it to pass
  `read_url` or that the probe sends the foreign Origin for it. All six say
  what the requirement turns on now, including `probe_cache`'s new
  `undecided` answer, which must not be read as "the header is keyed".
- Then the general case, measured rather than assumed: **ten of the
  twenty-four class modules named no tool of their class at all.** An agent
  reading `ssrf.md` on an SSRF signal was taught the methodology and never
  told `probe_ssrf` exists; the same for `idor`, `nosqli`, `race-condition`,
  `websocket`, `file-upload`, `prototype-pollution`, `info-disclosure`,
  `deserialization` and `logic-flaw`. Nothing noticed because the only check
  here was that a named tool is real - never that the right one is named.
  Each now carries one line: the tool, and the thing about the requirement
  it turns on.
- The gate holds it, with the denominator taken from the class -> tool table
  rather than from what a module happens to mention. `INDEX.md` already
  states that a module name resolves to a matrix class directly or through
  an alias, so the mapping was computable all along; the three
  methodology-only modules it names carry no class and are skipped.

- `deserialize` is excluded from the live agreement table for a stated
  reason, and `race` sets the precedent for what that obliges: assert both
  directions where no lab is involved. It already had both - the existing
  declaration test proves a gadget whose output returns and refuses the rce
  proof that sent none - but not the three shapes that matter for the
  exclusion itself: the lab's own `/import` answer (a gadget that raises
  `java.io.InvalidClassException` and never executes, which is a surface and
  not execution), a gadget plus an identity line with the nonce absent, and
  a destructive gadget hitting the veto that was asserted for `rce` and
  never for the class sharing its verifier. The stated exclusion is a
  measurement now.
  `race` and `deserialize` are excluded with a stated reason in the module
  docstring - `/import` returns a parser error and never executes, so
  "identity output plus the probe nonce" is unobtainable against this lab,
  which is a limit of the lab and not of the class.

### The evaluation asked for medians and nothing computed one
- `docs/EXPERIMENTS.md` says "report median" and "Report medians per
  configuration" - and no code computed a median. Every evaluation of this
  system would have taken the figures out of N session dirs by hand into a
  spreadsheet, which is exactly where a number gets mistyped and no reader
  can check it.
- `argus compare --by-arm` groups the session dirs by configuration - the
  parent directory with a trailing `-<trial>` stripped, which is the layout
  the document's own loops write (`exp/single-$i`) - and prints the median
  of each metric per arm with N and the min-max spread. `--csv` for a
  spreadsheet.
- Two decisions in that output are load-bearing. The median is
  `median_low`, so on an even N it is a figure some trial produced rather
  than the mean of the middle two: a system whose claim is that it invents
  nothing should not report a measurement no run made. And the spread is
  printed beside every median, because a median alone cannot distinguish
  five trials at 5 from five trials at 1, 1, 5, 9, 9.
- `cost (usd)` prints `-` unless every trial in the arm carries a price. A
  median over the priced subset would still appear under that heading and
  read as the arm's cost.
- Printing the two arms side by side immediately found a real defect:
  **a team run with no priced model reported a total cost of `0.0`**.
  `_cost_breakdown` summed per-agent costs, each `None` contributed
  nothing, and the total came out zero - which reads as free. The
  single-agent path has always reported `None` for this, and its own
  docstring said "rather than contributing a zero that reads as free". It
  reports `None` now, with the basis saying there is no total.
- And a crash either side of it: a session dir with no `summary.json` has
  no `argus_version`, so the version warning ran `sorted({"1.0.0", None})`
  and `compare` died with a `TypeError` instead of reporting what it had.
  Both compare paths now ignore non-string versions, and `--by-arm` warns
  that such a dir counts toward N while contributing no metric.

### The ledger hid a finding and crashed on a well-formed file
- Rule 1's suppression was per CLASS, so an `rce` recorded on `/a` hid an
  unrecorded `rce` proof on `/b` for the rest of the run - and the probe
  budget was spent per class too, so the second endpoint was parked as well.
  Two endpoints are two findings; both are keyed on (class, endpoint) now.
- `_load_findings` failed soft on bad JSON and not on a well-formed document
  of the wrong shape: `findings.json` containing `42` raised
  `TypeError: 'int' object is not iterable`. The contract says a malformed
  file is a fact about the run, and that covers `42`, `"hello"`, `null`, an
  object with no `findings` key, and a list of ints - all six are asserted.

### `argus judge` left the report contradicting the record
- Writing a verdict into `findings.json` and then re-sealing left `report.md`,
  `report.html`, `report.sarif` and `summary.json` describing findings that no
  longer matched: a reader opening the report saw a `proven` finding with no
  sign a judge had disputed it, under a seal that covered both. The command
  re-renders before sealing now, and records which model cross-verified and
  when. A render failure warns and keeps the verdicts rather than losing them.
- `parse_verdict` took the LAST of several agreeing objects. A model that
  answers and then appends `Summary: {"agrees": false}` put its reason,
  severity and missing list in the first one, so all three were discarded.
  Agreeing objects merge - later wins on the fields it carries, earlier detail
  survives where it does not - and a contradiction is still no verdict.

### Costs, verdict parsing, and three smaller things the audit had flagged
- **Cache writes were free.** `Model.cost` charged cache READS at a tenth of
  input and never charged cache WRITES at all, so a run that primed a large
  prefix was understated - the cheaper half priced, the more expensive half
  free. On the published 5-minute-TTL rates a write is ~1.25x input, so a
  100k-write / 900k-read run was reported at 0.27 USD and actually costs
  0.645. Both call sites pass the fourth count now, and `summary.json`'s
  `basis` line says what it charges.
- **`parse_verdict` was quadratic.** It restarted the brace scan from every
  `{` and ran to the end of the reply, so an 8 KB answer with nested objects
  took seconds - per finding. One depth-tracking pass does the same work in
  3 ms at 16 KB, and it no longer counts braces that sit inside a JSON string.
- **Every cited record was labelled `(event)`** in the judge's case file -
  the word this module's own prompt uses for evidence that is NOT class
  evidence - so a judge reading a real request/response pair was told it was
  not one. An exchange reads `(http exchange)`; an event keeps its kind.
- **An unrated finding swallowed a severity reduction.** `apply_verdict`
  compared against `_RANK` and gave up when the finding's own severity was
  absent or misspelled, silently dropping the one direction this module is
  supposed to allow. It applies it and records `severity_was_unrated`.
- **The lab's frame echo had no deadline.** `settimeout` bounds one `recv`,
  not a frame, so a client feeding one byte at a time held a handler thread
  indefinitely - test-only code, but it runs in the selftest's own process.

### Before and after belonged to the claimant, in four verifiers

A second adversarial sweep was pointed at the shapes the first one proved
real rather than at guesses, and its best lens was the one that measured
something: nine verifiers pair two exchanges with `_pairs`, and only two
ordered the pair. Four of the unordered ones needed to.

`_ordering` has a docstring that refuses exactly this defect - "a claimant
listing the ids in a chosen order would then decide which read was
'before' the write, which is the opposite of a check" - and three
verifiers were doing it anyway, through `claim.exchanges.index(...)`. The
cited list is built as `[transcript.get(r) for r in evidence_ids]`, so its
order is whatever the finding's author wrote. Each was reproduced before
being touched:

- **`method`**: a GET recorded BEFORE the PUT, carrying the nonce because
  the server had left it in that resource earlier, graded **proven** with
  the detail "argusput7k3m9x2q was written by r2 and read back by r1".
  `_witness` made it worse rather than catching it: the honest post-write
  read refutes the claim and scores 1 of 2 required checks, the pre-write
  read confirms it and scores 2, so the scoring *preferred* the exchange
  that predates the write and discarded the one that disproves the finding.
- **`upload`**: the identical two entries graded **proven** cited
  [upload, fetch] and **unproven** cited [fetch, upload], with the fetch
  recorded first by both id sequence and `ts` in each case. The detail text
  for the failing branch reads "<id> was recorded before the upload" - it
  was asserting a fact about the recorder while reading a fact about the
  claimant.
- **`jwt`**: a `jwt_forge` event stamped a full second AFTER the response
  it is credited with graded **proven**, floor check reading "jwt_forge r9
  set ['role'], echoed 'admin'". Cheap to hit by accident, which is what
  makes it bad: the echoed value is a short ordinary string - a role, a
  tenant, a department - that any authenticated page carries. Read a page
  with a legitimate session, mint a token afterwards, cite both.
- **`smuggle`**: both directions were live. The same two entries graded
  proven cited [ambiguity, effect] and unproven cited [effect, ambiguity],
  so a real desync written up effect-first was refused, and any
  earlier-recorded response on the endpoint whose body names a G-prefixed
  verb became "the effect" by being listed after it.

The desync one is the quietest form of the half-fix shape in this log. It
ordered by citation position *and said why*: "the ids are the recorder's
business, and an id this verifier cannot parse made it raise rather than
refuse". The worry was real and `_ordering` had already answered it - an
unparseable id gets sequence 0 instead of an exception. The reason expired;
the workaround did not.

`_follows(when, later, earlier)` is now one named predicate, fail-closed,
used at all four sites. It spans events and exchanges because
`record_event` and `record_exchange` increment one `self._seq` under one
lock and both return `r<n>`, so the sequence is authoritative over the
whole transcript rather than its HTTP half. Eight verifiers order their
evidence now, up from three.

Two tests hold the shape rather than the four instances: one fails if any
verifier reads `exchanges.index(...)` or enumerates positions again, and
one requires every verifier to either order its evidence or be listed in
`_ORDER_FREE` with the reason it does not need to - so a new verifier
written tomorrow fails until someone decides which it is. **Four of the
seven unordered verifiers were right to ignore order** and are listed
there: a true-payload and a false-payload response differ whichever was
sent first, an injected header and its echo are the same exchange. Fixing
those would have been a change to code with no defect in it.

Five existing tests failed on the new requirement, and the fixtures were
what was wrong, not the gate: they hand-rolled entry dicts with no `ts`,
bypassing the `ex()` helper that was given one earlier in this work for
precisely this reason. `record_exchange` and `record_event` write a stamp
on every entry, so an unstamped entry cannot come from this system. The
gate was not relaxed to accommodate a fixture. One of those tests had a
leg named "a fetch recorded BEFORE the upload" that passed only because
the citation order happened to agree with the recorder - it never covered
the defect it was named for.

### A lockout check with three holes, all of them mine

The progressive-delay check added earlier in this session shipped with
three defects, found by pointing the same sweep at it. All three measured:

- **Gated at six attempts while the class accepts five.** The minimum
  series `lockout` accepts was exactly the series whose latency was never
  read: five attempts ramping 150 -> 650ms graded **proven** - "this
  target has no lockout" - while the identical shape at ten graded
  candidate. Two literals for one threshold, 5 and 6, written in the same
  change. They are one constant now.
- **Fail-open on a missing `elapsed_ms`.** It required every cited
  exchange to carry one and skipped the whole check otherwise, so
  appending a single latency-free entry to the ten-attempt ramp - the
  exact evidence the fix was measured on - put it back to **proven**. The
  claimant could turn the check off by citing one more exchange, in a
  check whose stated reason for existing is that refusing is the
  fail-closed direction here.
- **Measured in citation order.** Citing the same ten attempts
  newest-first made the ramp read as a decline and graded **proven**. This
  one the sweep did not report; it turned up by applying the sweep's own
  ordering lens to the code I had just written.

The probe half was still wrong too, and the comment in `verify_no_throttle`
*documented* that instead of fixing it - "the probe's own half missed it
too, and for the reason this log keeps recording". `probe_lockout` tested
the same property with its own derived quantity, means of three and
`last > first * 3 + 150`, which on a 150 -> 600ms ramp computes 553 > 650
and reported the target UNTHROTTLED. So probe and verifier disagreed on
one property, and the probe disagreed in the direction that writes a false
finding. It also averaged `results[:3]` against `results[-3:]`, which
overlap below six attempts, so at its own `len >= 4` gate it compared a
window with itself. Both halves now call one `proof.latency_ramp`, the way
`probe_cmdi` already borrows `_overlaps`.

What is still open, and now stated in the report text rather than hidden:
if no attempt carries a recorded latency the ramp cannot be measured, and
the class can still prove blind. The detail used to read "all N answered
without a throttle" in that case; it now says how many were timed and that
a progressive delay could not be ruled out.

### "The target never replied" was not a concept this gate had

`grep '"error"' argus/proof.py` matched one docstring and nothing tested
`status == 0`, so an exchange the target never answered was evidence like
any other. `GuardedClient` records a transport failure as `status: 0`, an
empty body and a `response.error` naming the exception, and every field
needed to tell that apart from an answer was already in the transcript.

Measured: four POST /login attempts, two answering 200 "Login failed" and
two that timed out, graded `enum` **proven** - "2 distinct answers over 4
requests", "both answers repeat". The second answer was the absence of one,
and it repeated because the target was down twice.

`_answered(entry)` is now `100 <= status < 600`, the same test the
`status_of_result` callers in `probes.py` use, so both halves agree on what
an answer is. The status decides it and not `error`, because a response
that arrived and then failed mid-body carries both and did answer.

Beside it, three more gate false positives from the same sweep, each
reproduced before being touched and each with a sibling in the same file
that already had the guard:

- **`nosqli` proven off a flaky 500.** `refused_control = next(c for c in
  controls if status_of(c) >= 400)` read the server BREAKING as the server
  refusing. A 503 on the control plus a 200 answering
  `{"session":"","user":null}` - no access at all - graded proven, and so
  did a 500 control beside the public listing a search endpoint answers
  anyway. The rule was written down twice in this file already:
  `_acl_header_changed_the_answer` guards it in prose, and
  `verify_restricted_access` uses an allowlist.

  Closing the `access` branch alone was not enough. The `extraction`
  branch rests on the control NOT carrying documents, which "Internal
  Server Error" satisfies for free, so the 500 case still proved until a
  broken control stopped counting as a control at all.

  The first version of `_refused` was a narrow allowlist, and planting the
  old `>= 400` back showed two things at once: nothing failed, because the
  caller's filter already excluded 5xx and the allowlist's only remaining
  contribution was 429 - and leaving 404 out would have introduced a false
  NEGATIVE, since `POST /api/login` answering 404 "no such user" while the
  same request with `{"$ne": null}` answers 200 with a session is a real
  bypass. A guard no test can tell from its absence is not a guard, and
  one that refuses real evidence is worse than none. It is 4xx except 429
  now, and both boundaries are asserted.

- **`method` proven by a path echo.** `PUT /files/<canary>.txt` then `GET
  /files/<canary>.txt` answered by a soft-404 whose body names the URL it
  could not find graded proven - "written by r2 and read back by r3".
  Nothing was stored. The comment in the verifier records removing the URL
  from the WRITE side for this exact reason, and that closed nothing,
  because `probe_method` puts the canary in the filename AND the body.

  The obvious guard - require the nonce absent from the read's own request
  - is wrong, and measuring said so: the read's URL always carries the
  canary, so the honest case dropped to `unproven` and the class became
  unprovable for the shape its own probe produces. What separates them is
  the BODY. The stored object comes back; a soft-404 returns the path. The
  written bytes must appear in the read and must not be something the
  read's own request supplied, the second half because a reflecting
  endpoint answering `GET /x?q=<written bytes>` would otherwise echo its
  way to proven.

A behavioural check now asks the module-wide question rather than the
three local ones: every gradeable class, handed nothing but exchanges the
target never answered, must refuse.

### Four probes measured the defence as the bug

`status_of_result` was added to `probes.py` when `probe_time` was
corrected, with a docstring generalising the rule - "any probe that reads a
duration without reading this is treating a transport failure as a
measurement". Four probes went on doing it, one of them 130 lines away. A
rule in a docstring is not a check.

Every comparison in them is fail-OPEN on a dropped request:
`_similarity("", page)` is 0.0, which is maximally different, status 0
differs from any real status, and the read timeout kept in `elapsed_ms`
clears any delay threshold. So the defence manufactured the evidence for
the bug it defends against, and in each case the probe told the operator
to record a finding the proof gate refuses - the direction that wastes an
engagement:

- `probe_cmdi`'s blind timing fallback: "blind candidate: delay on
  semicolon, pipe, and, background" - four separator families at once -
  against a target that blackholed every request carrying a shell
  separator. The 15s read timeout IS the delay it measured.
- `probe_sqli`: a dropped payload scored as a boolean-blind differential,
  with `statuses 0/200` printed in the signal string the model reads as
  proof. `probe_nosqli` had the same shape in two places.
- `probe_enum`: a dropped request was a differing answer AND reproduced,
  because `_similarity("", base)` is 0.0 and `_similarity("", "")` is 1.0 -
  so a username dropped twice became a confirmed enumeration oracle.
- `probe_upload`: `served` was a bare body substring test and
  `entry["status"]` keeps the UPLOAD's status, so the fetch's status
  appeared nowhere in the probe's output. Against an app that accepts every
  upload, answers `{"url": "/uploads/<canary>.php"}` and stores nothing:
  "unrestricted upload: stored and served as active content" for all ten
  active payload families at once.

`probe_lockout` had a fifth, found by the check below rather than by the
sweep: against a target that answered nothing it said "no lockout or rate
limit after 10 failed attempts - online password guessing is unthrottled",
with "they got no answer" as a parenthetical underneath. Ten attempts that
got no answer are not ten failed attempts, and a caveat under a wrong
headline is still a wrong headline.

**The first two versions of the test for all this caught none of it.** With
every send unanswered, `probe_cmdi`'s threshold is computed from dead
baselines and never clears, and `_similarity("", "")` is 1.0 so nothing
differs - the defect needs one side of a comparison answered and the other
dropped, which is what a WAF blackholing the payload actually does. The
second version matched the blocked payload against the percent-encoded
URL, so it matched nothing. Both passed. That is the fifth time in this
work that a model built to stand in for reality agreed with the fix and
proved nothing about it, so each of the six defects was planted back and
the verdict the finding reported was watched to reappear, word for word,
before the test was kept.

The negative-prefix rule those tests use also cannot see a claim in a
second clause - "no lockout ... is unthrottled" starts with "no " and
passes - so the probe that was actually wrong has its own assertion. Two
earlier versions scanned for the words a claim uses instead, and flagged
`probe_time`'s correct "no delay observed" on the word "observed" and
`probe_enum`'s correct "no enumeration signal" on the word "enumeration":
a keyword list tests the wording, not the claim.

### The gate called the defence working the finding

`verify_token_forgery`'s floor check is "this system minted the
credential", and it could not tell which request carried the minted token,
because nothing in the system recorded that. Measured, with the ordering
fix above already in place:

    jwt_forge r1       claims_set {"role": "admin"}
    r2  GET /api/me    cookie: s=mine                 200  {"role":"admin"}
    r3  GET /api/me    authorization: Bearer forged   401  invalid signature

    grade: proven, missing: []
      [x] this system minted the credential
      [x] a forged credential was accepted
      [x] the same endpoint refuses another credential

The forged token was **refused**. The 200 is the operator's own session
reading its own role. The gate reported it as a forgery accepted - the
exact inversion the test named
`test_the_defence_working_is_not_a_finding` exists to prevent, and that
test did not catch it, because its jwt leg cites no mint at all. With no
`jwt_forge` event the only failing check is the spec's floor, which is
already the whole subject of a different test, and the two checks that
would have to tell an auth system working from a forgery both passed. The
defence-detection logic could have been deleted and the assertion would
still have held.

Three things let the inversion through, all measured: `echoed` asks only
whether a forged claim VALUE appears in the accepted response, and a forged
`role=admin` echoes trivially out of a real admin's own page; `differ` was
`bool(cred_r)`, so "a different credential" was never established; and
`_pairs` picks (accepted, rejected) by status, never by which request
carried the token.

**The correlating datum was half-built and unread.** `jwt_forge`
fingerprints the token it mints, and its comment says what for - "the
fingerprint is enough to link the mint to the request that carried it" -
but nothing fingerprinted the credential a request SENT, so there was
nothing to link it to, and `token_sha256_16` appeared nowhere in
`proof.py`. One half of a mechanism, with a comment describing the whole.

`GuardedClient` now records `request.credential_sha256_16`, a sha256-16 per
credential header with the scheme word stripped so it hashes the same bytes
`jwt_forge` does, and the verifier requires the accepted request's digest to
be one the mint produced. It is a one-way digest of the same shape
`analysis.py` already wrote for the same reason; the header value stays
redacted, and the live-lab test asserts both halves - the digest is right,
and the credential is still absent from the transcript an operator shares.

Fail-closed when no fingerprint is recorded, because a real exchange always
has one and an evidence set that cannot be correlated is exactly the set
this class used to prove on.

The jwt fixtures were unfaithful in the same way, and `ex()` now calls the
recorder's own `credential_fingerprints` rather than a copy, so a fixture
cannot drift from the thing it stands in for. Two of them had the accepted
request carrying the operator's own cookie while the mint sat unreferenced -
which is to say they were the defence working, graded proven, written down
as the expected result.

### Probes decided on 12,000 characters; the transcript keeps 200,000

`GuardedClient.send` stores `body[:BODY_CAP]` (200,000) in the transcript
and hands `body[:RETURN_CAP]` (12,000) back to the caller - and sets
`body_truncated_at` only for the 200k cut, so a probe could not tell its
view was a prefix. Every probe that asks "is my marker in the body" was
asking of the first 12,000 characters: `probe_reflection`, `probe_sqli`'s
similarities, `probe_lfi`'s markers, `probe_cmdi`'s identity match,
`probe_massassign`, `probe_upload`, `probe_disclosure`'s soft-404
equality.

Measured on a new lab endpoint built for it: a 15,688-character page
echoing the canary with raw `<>"'` at offset 15,665 made
`probe_reflection` answer "not reflected", while the proof gate - which
has always read the recorded body - found the same reflection and passed
"payload reflected unencoded into HTML". Probe and gate disagreeing on the
same bytes with the probe blind, and a false negative is the quiet kind:
the operator is told there is nothing there and moves on.

`_send` now returns the recorded body, which fixes every probe downstream
of it in one place rather than at thirty call sites. Nothing passes a whole
body into a probe's RESULT - the excerpts there are explicitly bounded - so
what reaches the model is unchanged. `probe_race` had been reaching the
recorded entry this way all along and was the only one.

The test drives the real lab rather than a fake client, and asserts the
geometry it depends on - that the reflection really is past
`RETURN_CAP` and really is inside `BODY_CAP` - because otherwise it would
pass without testing anything.

### A clean endpoint already reached the best grade its class can reach

`test_the_matrix_refuses_a_probe_run_on_a_clean_endpoint` asserted
`grade != "proven"`, and `xss` and `ssrf` are both capped at `candidate` -
`ProofSpec.verdict` runs `_clamp(raw, self.ceiling)`, so `proven` is not in
the range of `proof.grade` for them on any input. For those two rows the
assertion was true for every possible input.

The table's own comment states the right rule - "keep only what grades
below its ceiling" - and the assertion implemented a weaker one. Tightened
to match the comment, 21 of 22 rows pass and the ssrf row fails: driven
against `/search?q=x`, a clean search box reached `candidate` with
`missing == ['settled by this system (held at candidate)']`, meaning every
required check PASSED and only the cap held it down.

That is not a defect in the verifier. `ssrf` is graded by
`verify_generic`, whose one check is "the excerpt discriminates against a
control", and a search box that echoes its term differs from its own
control by construction - which is exactly why the class is capped. The
row was pointed at the one kind of endpoint the clean direction cannot
mean anything for. `/internal/status` serves a fixed JSON body, so payload
and control come back identical and the check genuinely fails: measured
`unproven`.

Checked by sabotage, which is how the refuter found it: forcing every
`_check` to pass unconditionally now fails 21 of the 22 clean rows. Before
this it left three passing, the two capped ones among them. The one that
still passes is recorded in the table's comment rather than left for a
reader to assume - `/ws-strict`'s refusal offers no quotable line, so
`_best_grade` returns `unproven` without ever calling `proof.grade`, and
that row asserts the probe produced nothing citable, which is a weaker
claim than "the verifier refused it".

### CI verified a committed artifact that the local gate never looked at

The credential-digest requirement above went in fail-closed in both
directions, passed 663 local tests and 158 doc checks, and CI answered
within a minute:

    TAMPERED: F06 claims grade 'proven' but its cited evidence supports
    'unproven' - unmet: this system minted the credential

`python -m argus verify docs/sample-session` ran **only** in CI's wheel
job - not in `selftest.py`, not in pytest - so the local gate could not
see it. That is the gap, and it
matters more than the change that fell into it: `argus verify` re-grades
every finding against the transcript, which makes it the one check that
notices when the proof matrix moves under a shipped proof. It is a pytest
test now, so all ten pytest jobs and the local gate run it too.

The artifact was right. F06 is a real forgery - a `jwt_forge` event with
its fingerprints, a Bearer token accepted 200 echoing the forged claims,
another credential refused 401 - and only the digest of the accepted
request was missing, because the field did not exist when the session was
recorded. Failing closed there reports TAMPERED on a legitimate proof,
which is a false alarm about the evidence rather than a finding about the
target.

So the check has three states and not two:

    digest present and matching  -> this request carried the minted token
    digest present, no match     -> it carried something else: REFUSE
    digest absent entirely       -> graded by the old rule, and said so

The third is not a loophole in this build. `GuardedClient` writes a digest
for every credential header, so an accepted request that carried a
credential has one; one that carried none fails "a forged credential was
accepted" on its own. That is asserted, because it is what keeps the
compatibility path narrow. And without a digest there is genuinely nothing
to correlate - both requests persist as `Bearer <redacted>`, which is the
reason `differ` is only `bool(cred_r)` two checks down - so the detail text
names which rule ran rather than letting the gate quietly be two gates.

Both directions were checked by planting them: making the absent state
refuse reproduces CI's message locally, and letting the no-match state
through fails the defence-working test.

### Three tests whose assertions did not touch their subject

All three passed, all three would have passed with the code they are named
for deleted, and a sweep lens built for exactly this shape found them.

**The lab's path containment, twice.** `test_cat_containment_is_not_prefix_based`
ended with

    sibling = realpath(FAKEFS) + "-other"
    assert not realpath(join(FAKEFS, "x")).startswith(sibling)

which is true for every possible value of `FAKEFS` - the left side
continues with `/x` exactly where the right side continues with `-other` -
and never called `_lab_exec`, the containment it is named for. The subject
was not even the lab's root: `lab/vulnapp.py` is a shim that snapshots
`globals().update(vars(_real))` once at import, while `make_server`
rebinds `FAKEFS` with `global FAKEFS` inside `argus.lab.vulnapp`. So
`vulnapp.FAKEFS` stays `""` all session and `realpath("")` is the process
cwd: the assertion compared `<cwd>/x` against `<cwd>-other`. The function
is shared and only the global is stale, which is why `_lab_exec` itself
worked. It also did not request the lab fixture, so it depended on another
test having started the server first.

It now creates a real sibling directory beside the live root, asserts
`_lab_exec` refuses to read out of it, asserts a file inside the root
still reads (or "refuses everything" would pass), and asserts the naive
prefix test would have let the sibling through - which is what the
separator in the real comparison is for. Dropping that separator now fails
it with the sibling's contents in the output.

**`test_cat_containment_is_case_folded`** rebuilt the comparison from
`ntpath.normpath`, `str.lower` and `ntpath.sep` and asserted its own
model; nothing from `vulnapp` or `argus` appeared in the loop. Its only
link to the code was `assert "os.path.normcase" in src`, which proves an
identifier occurs in the function text, not that it is applied to both
sides. The model also differed from the code twice: `str.lower()` where
the code uses `os.path.normcase` (which on NT also folds `/` to `\`), and
`ntpath.sep` where the code uses `os.sep`.

The containment is now a named `_within_root(path, root)` so a test can
have it as its subject, and the Windows test drives that function under
patched NT semantics. Dropping `normcase` or dropping the separator each
fail it.

The wiring - that `cat` consults that function - is deliberately NOT
asserted there. A source grep cannot tell a call from a mention, measured:
planting `if _within_root(path, FAKEFS) is False and False:` keeps the
substring, disables the guard, and passes a grep for it. The behavioural
test in `test_lab.py` holds the wiring instead. Logic in one place, wiring
in the other, neither pretending to be the other.

**`test_windows_semantics`'s "skipped as a path" leg** computed
`[t for t in toks if os.sep in t]` inside a block that patches `os.sep` to
`"\"`, one line after `[t for t in toks if "\" in t]` - the same
predicate twice. The second assertion could not fail unless the first had,
and it never touched the external-arg scope check whose behaviour it
claimed to verify. It now drives `_args_scope_check` with a recording
scope and asserts the Windows path was not read as a hostname while a
bare hostname beside it still was.

And what that does NOT pin, measured rather than claimed: deleting the
`os.sep in tok` skip leaves both assertions passing, because
`_hostish_token` rejects every token containing a separator - `C:\lists\
hosts.txt` splits to host part `"C"`. That skip is defence in depth and
the second guard does the work. Removing the hostname check instead does
fail the test, which is how the two were told apart.

### Six bounds the target set the cost of

Each one claimed a limit in a comment and bounded something narrower. A
sweep lens asked, of every bound in the package, *what actually defeats
this* - and the answers were all the same shape: a quantity the target
chooses.

**A timeout that killed one process.** `subprocess.run(..., timeout=)`
sends SIGKILL to the direct child and waits for it; anything that child
spawned is reparented to init and keeps the stdout fd it inherited - a
temp file already unlinked, so it grows with no visible file - along with
its network access. For this package that is not tidiness: the orphan goes
on talking to the target with no ScopeGuard, no RateLimiter and no request
budget, nothing it does reaches the transcript, and the engagement's own
record says the run was stopped after N seconds. Measured both ways - with
`subprocess.run` a grandchild's marker file appears after the run reports
a timeout; with the process group killed it never does. POSIX gets
`start_new_session` plus `killpg`, Windows `taskkill /T`, and both fall
back to killing the one child, which is the old behaviour.

**A drain that read whatever the target sent.** `send_raw` kept only
`BODY_CAP`, and the cap gated the APPEND, never the read - so the loop ran
until the server chose to end the body. Memory was bounded; time was
`declared_length / bandwidth`. The comment above the `reads` clamp claimed
"each extra read holds a 3s socket timeout, so an unbounded value would
pin the tool for reads*3 seconds", and that was false for exactly this
reason. The sibling httpx path gets it right. It cannot simply stop early
either - the comment above the loop says why, and it is a protocol fact:
a connection whose stream position is unknown cannot be read again. So the
cut reports itself through `error`, which also stops the further reads.

**A read timeout that bounded the silence between bytes.** `_fetch_capped`
consumed the body with `iter_bytes(65536)`, and an httpx read timeout
bounds one read, which every arriving byte resets. A target sending one
byte just inside the window was never timed out: the ceiling was
`BODY_CAP` reads x the read timeout, and the call returned status 200 with
`error: None`, so nothing downstream could tell a trickle from a fast
response while every probe here decides on that body.

The first version of that fix was wrong in the way it was fixing. It added
a deadline and kept `iter_bytes(65536)`, and httpx accumulates until it HAS
65536 bytes - so the deadline was consulted between chunks and a target
sending a byte every 10ms stayed inside the first yield for eleven
minutes. The test for it hung until it was killed. `iter_bytes()` with no
size yields per arriving piece. Same shape as `BufferedReader.read(n)` in
`_ws_read_frame`, two bounds apart in the same file.

**A frame deadline that bounded the header.** `_ws_read_frame`'s docstring
promises "a deadline over the whole frame", implemented by checking the
clock between `fh.read()` calls - and `fh` is a `BufferedReader`, whose
`read(n)` loops on the raw socket internally until it has all n bytes. A
server that declares a length, up to `_WS_MAX_FRAME`, and then feeds one
byte at a time stayed inside a single call for length x interval. `read1`
makes at most one call to the raw stream. Planted back, the test is killed
at 25 seconds; fixed, it returns in one.

**A page bound that counted successes.** `crawl`'s `len(pages) < max_pages`
counts pages APPENDED, which happens only after `send` returns - so a
refused send fell through to `continue` without advancing it. And `send`
called `self.rate.wait()` BEFORE testing the request budget, so every call
after the budget was spent slept a full rate interval and raised without
sending a byte. The queue length is the target's choice: `_SurfaceParser.
links` has no cap and one `BODY_CAP` body holds thousands of hrefs.
Attempts are bounded now as well as pages, and the budget is checked before
the wait - refusing costs nothing.

**A guard written for one metric.** `compare --by-arm` reports `-` rather
than a median over part of an arm, with the reason beside it: "a median
over the priced subset of an arm would read as the arm's cost while
describing only part of it". It covered `usd`. `time_to_first_finding_s`
is null for every run that found nothing, and `duration_s` was made
nullable in this same body of work, AFTER that guard was written - so an
arm of five trials where one found nothing printed a median over the four
that did, under the arm's full N. For `ttf` the subset is systematically
the SUCCESSFUL trials, which is the worst bias available: the arm that
fails more often reports the better time-to-first-finding.

Every one of the six was planted back and watched to fail, which also
caught a seventh thing: setting `response_data["error"]` records a slow
body in the transcript and leaves `out["error"]` - the dict every probe
reads - saying `None`.

### A platform simulated around real code changes more than one thing

`test_windows_semantics` ran `_args_scope_check` inside
`mock.patch.object(os, "name", "nt")`. `pathlib.Path()` chooses its
flavour from `os.name` AT CALL TIME on Python 3.10 and 3.11, so
`Path(tok).exists()` inside the code under test instantiated a
`WindowsPath` on Linux and raised `NotImplementedError`. Green on 3.12,
3.13 and 3.14 - the three interpreters on this machine - and red on the
two CI jobs for the versions it does not have.

The two claims are now separate: the splitting claim keeps the patch,
because it is about `_split_args`, which reads `os.name` and touches no
paths; the scope-check claim runs unpatched with this platform's own
separator, because "a token containing `os.sep` is not a hostname" is not
Windows-specific.

And the trap is reproducible here now rather than only in CI: an autouse
fixture makes `analysis.Path` raise the way 3.10 would whenever `os.name`
is patched away from this platform's. It reproduces the CI failure exactly
on the old shape and passes on the new one. Narrow on purpose - it covers
the module these tests drive - and a mechanism rather than a source grep,
so it fails on the behaviour and not on the spelling.

### The doc gate refused a name and the exemption list was the wrong fix

    [FAIL] docs name only registered tools (56) - CHANGELOG.md: [...]

The refused token was a `run_*`-shaped identifier, matching the family
`run_external` defines, and the obvious answer was to add it to
`_NOT_TOOLS` beside `run_id`, which is exempt for exactly that reason. The
comment written beside the new entry said it was "this gate's own script,
`test/run_*.sh`, which the operating rules tell a reader to run before
accepting any change".

There is no such script in this tree. Neither is there a
`test/cases/proof_*.json`. Both belong to the superseded tree the archive
banner points away from; this one states its gate in `AGENTS.md` as
`python selftest.py` and `python -m pytest tests/ -q`, which is what every
run in this log has been. The only three things naming that script were
the three pieces of prose written beside the exemption.

So the gate was right and the exemption silenced it. A check whose stated
purpose is "documentation names only things that exist" had found a
document naming something that does not exist, and the repair applied was
to stop it looking. The exemption is gone and the prose names the gate this
tree has - and the gate then refused the first draft of THIS entry, which
still spelled the identifier out.

Worth recording for the shape rather than the typo: an exemption list is
the one repair that always works, which is what makes it the wrong
instinct. Every other entry in `_NOT_TOOLS` is a real thing sharing a
prefix with a tool - a module, a transcript field, a probe parameter. One
more for a file that does not exist would have made the list the place the
gate's own failures go to be forgotten.

### One value answering two questions, and four rounds of Windows CI

`race` was the one proof class missing from the proving direction of
`tests/test_probe_matrix_agreement.py`, and the note holding its place said
what was missing was not a mechanism but a diagnosis: on Windows 3.10, 3.11
and 3.12 it graded `unproven` with `missing: ['no evidence']` while Windows
3.13, 3.14 and every ubuntu job proved it. It had been added and reverted
twice on local evidence. Here is the diagnosis.

`proof._window` reconstructs a request's window as `[ts - elapsed_ms, ts]`
and returns `(0.0, 0.0)` when the duration is unusable - documented, and
right, as "a zero-width window: it overlaps nothing, which is the
fail-closed answer". `verify_concurrent_crossing` then asked that same
tuple a second question, *is this entry after the burst*, as
`_window(e)[0] >= burst_end` and as a sort key. Zero is the conservative
answer to *did it overlap*. It is the **epoch** as an answer to *when was
it*: before everything, so an entry whose duration did not record could
never be after anything.

`elapsed_ms` is a difference of two `time.monotonic()` reads, and
`time.monotonic()` on Windows is `GetTickCount64` up to Python 3.12 -
CPython gh-88494 moved it to `QueryPerformanceCounter` in 3.13, 15.6ms to
100ns. A difference of two reads of a 15.6ms clock is a multiple of 15.6ms
and **zero for anything shorter than one tick**. `probe_race`'s serial
controls are refusals, which the lab answers in 2-5ms. So on those three
runners both controls recorded `elapsed_ms: 0.0`, were placed at the epoch,
and the class had no control at all.

Measured on a real local recording, quantising only the recorded
quantities to that tick and changing nothing else:

| model of the platform | grade |
| --- | --- |
| as recorded | `proven` |
| `ts` quantised only | `proven` |
| `elapsed_ms` quantised | `unproven`, missing the serial control |
| both quantised | `unproven`, missing the serial control |

The second row is what the simulation that cleared the previous fix
modelled - it coarsened the recorder's clock, behind `ts`, and left
`elapsed_ms` precise. That is why it measured 20/20 twice and was wrong
twice, and it is a sharper statement than "the simulation was unfaithful":
it was unfaithful in one nameable respect.

- `proof._window_start` is a separate accessor for the ordering question:
  the reconstructed start when there is one, the recorded `ts` otherwise.
  `_window` is untouched, so overlap stays fail-closed on a zero-width
  window. Widening `_window` to `(ts, ts)` would also have fixed the
  ordering and would have let one instant inside another request's window
  count as "two attempts on the wire at once"; that is the second plant,
  and `test_a_window_with_no_duration_still_overlaps_nothing` fails on it.
- Four cases in `tests/test_proof.py`, both directions: a duration that did
  not record still has a position; a window with no duration still overlaps
  nothing; a fast refusal recorded *before* the burst is still not the
  serial control; an attempt the target never answered is still not the
  serial control. Removing the fix fails the first with
  `'unproven' == 'proven'`.
- `race` is back in the proving table - 28 of the 29 classes now driven in
  the proving direction, `dos` alone excluded, by construction.
Confirmed on the platform rather than locally, which the standing
instruction required. A throwaway `agent-race-diag` branch printed what
each runner records. Windows 3.10.11: `monotonic()` is `GetTickCount64()`
with a delivered tick of 15.0000ms; the burst recorded `elapsed_ms: 156.0`
six times and both serial controls recorded `elapsed_ms: 0.0` with window
`(0.0, 0.0)`. The same recording graded `proven` with the fix and
`unproven` / `['no evidence']` without it, in one run - the platform
planted the defect back itself. 5/5 proven in each of the three Windows
jobs that used to fail; all 11 jobs green with the row in the table.
Windows 3.13.17 for contrast: `QueryPerformanceCounter()`, 0.0001ms.

It also corrected one figure: `time()` on those runners delivers a 1.75ms
tick, not the 15.6ms `get_clock_info().resolution` claims for it. `ts` was
never the coarse clock there, so the simulation that coarsened `ts` was
coarsening the only clock on the box that was already fine.

- What this does NOT fix: a loaded runner that serialises the burst. The 8s
  barrier in `/redeem` makes that unlikely and the first assertion would
  report it (six 200s against one coupon cannot happen without
  concurrency), but it is a different failure from the one diagnosed here
  and it is not addressed.

### A gitignore rule that hid the tool layer, and a check that passed by not working

`.gitignore` carried `tools/` for a local 19 MB `tools/ghidra-dist/`. A
pattern with no leading slash matches a directory of that name at ANY
depth, so it also matched **`argus/tools/`** - the whole tool layer:
`registry.py`, `probes.py`, `analysis.py`, `web.py`, `team.py`,
`mcp_tools.py`, `_subproc.py`, `__init__.py`. All eight are tracked, so
`.gitignore` never untracked them and nothing was broken.

The damage was prospective and silent. Measured both ways on a real new
file at `argus/tools/_claim_check.py`: with the rule as shipped,
`git status` in porcelain form over `argus/tools/` prints **nothing**,
and `git add -A`
stages everything else and skips it; with the rule anchored it appears as
`??` and adds normally. Meanwhile AGENTS.md tells a contributor that every
tool must be registered in `tools/registry.py`, and
`skills/extending-argus/SKILL.md` walks them through adding one. A
committed registry importing a module that was never committed fails on a
fresh clone and in the wheel, and says nothing at the moment the mistake
is made. `/*.tar.gz` in the same block was already anchored; these four
were not.

- `/challenges/`, `/cache/`, `/solved/`, `/tools/` anchored. The
  conventional patterns at the top of the file are deliberately left
  unanchored, because the gate now covers that whole class.
- Two checks in `selftest.py`: no tracked file is ignored, and a new file
  in any package directory is not ignored. Two questions, because after
  the fix the first passes forever while a later bare `cache/` or
  `build/` would still swallow a new `argus/cache/`; the second probes a
  filename that never exists on disk, which is what git's no-index mode
  is for.
- **The first draft of those checks was vacuous and passed with the defect
  planted back.** `git check-ignore` reads NEWLINE-separated paths from
  standard input unless `-z` is given, and it was handed NUL-joined bytes
  without it - so
  git saw one enormous path, matched nothing, exited 1, and both checks
  read that as "nothing is ignored". They would have passed in either
  state. They now send one path that MUST be ignored along with the rest
  and report the instrument instead of agreeing when it does not come
  back: with `-z` removed, both fail with "this call is not answering the
  question and a pass here would mean nothing". That is the third time this
  stretch that the instrument was the defect.

### The guard was never asked: three finders narrower than their consumers

A fresh eight-plane sweep of the parts the last one did not cover. These
three are one defect: `ScopeGuard.check` is not wrong in any of them -
asked, it refuses every form below - but the code deciding WHAT to ask
about was narrower than the thing that receives the value.

- `analysis._URL_RE` was case-sensitive while the token loop beside it
  skipped anything matching `(?i)https?://` as "already handled above".
  With a case-sensitive finder, an uppercase scheme was handled by
  neither. Measured: `_args_scope_check` refused `http://evil.test/x` and
  PASSED `HTTP://evil.test/x`, while the guard refuses both. A URL scheme
  is case-insensitive by RFC 3986, and curl dials either spelling - with
  curl 8.x, `HTTP://127.0.0.1:1/` reaches `(7) Failed to connect`, which
  is curl reporting it parsed the argument and tried.
- The same scan skipped every token containing a path separator, and
  `host:port/path` is a URL curl accepts with no scheme at all. Measured:
  `evil.test:8080/path` passed the scan; curl dials it. Splitting the path
  off is not the same as deleting the skip - deleting it recovers
  `evil.test` from `evil.test:8080/path` by accident of the colon while
  leaving `evil.test/path` intact, because the host classifier rejects
  anything with a slash in it.
- `mcp_tools._url_args` collected URL arguments with a case-sensitive
  scheme test, and it is the only gate between an MCP argument and a
  fetch-type server's own socket. An uppercase scheme was collected by
  nobody and checked by nobody; the test now shows the fake server
  echoing the out-of-scope URL back when the fix is removed.
- Two more of the shape, both already failing CLOSED, so wrong messages
  rather than holes: an uppercase-scheme model `api_base` was refused as
  "over plaintext", and an uppercase-scheme proxy got "expected http:// or
  https://" while an uppercase SOCKS one got that message instead of the
  socksio one.

And a correction to this repo's own record. `tests/test_windows.py`
carried a note concluding that the separator skip was "defence in depth"
because deleting it changed no assertion there. Both measurements in that
note were right and the conclusion did not follow: those assertions are
about a path token, where the skip's effect genuinely is
indistinguishable, which says nothing about the other tokens that carry a
separator. "No test I have distinguishes these" is not "nothing
distinguishes these", and writing the first down as the second is how the
skip survived a sweep. The note now says so, next to the token that
distinguishes it.

The new test asserts both directions, and the second direction is the one
that matters: a scan tightened until it refuses ordinary tool arguments is
a scan the next person switches off. Nine real argument strings - wordlist
paths absolute and relative, target-list files, output paths, port lists,
a header value - still pass, because the host classifier makes a
single-label token prove it resolves before anyone calls it a target.

### One slash too many was a different path

`--exclude /admin` refused `/admin`, `/ADMIN`, `/x/../admin`, `/%61dmin`,
`///admin` and `/%2F%2Fadmin`, and allowed `//admin`, `/%2fadmin` and
`/\admin`. One rule behind all three: `posixpath.normpath` is
POSIX-faithful about a path beginning with EXACTLY two slashes being
implementation-defined, so it preserves `//admin` while collapsing
`///admin` to `/admin`. The guard was refusing more slashes than it
allowed - a normalization that disagreed with itself, not one that was
missing.

All three forms are inside the threat model the surrounding comments
already state. `//admin` goes on the wire as-is and nginx and Apache merge
duplicate slashes by default. httpx sends `/%2fadmin` raw
(`raw_path=b'/%2fadmin'`), so the target decodes it and lands in the same
place. `/\admin` is the IIS separator the case-and-backslash fold exists
for, and that fold produced `//admin`, which the same rule then spared.

- `scope._collapse` squeezes runs of separators before and after normpath.
  Sixteen hostile spellings now refused, including `/%5cadmin`, which was
  not in the report. Six legitimate paths still allowed, `/administrator`
  among them, because every comparison is `== prefix` or `prefix + "/"`.
- Over-blocking an operator-declared no-go area is the error this code
  already chose to prefer, which is what makes collapsing safe here.

### The judge's contradiction detector kept the coercion the value had dropped

`judge.py` exists so that "a judge can lower a grade or dispute a finding.
It can never raise one", and `_as_bool` exists because, in this module's
own words, "`bool("false")` is True, which is how a judge that disagreed
was recorded as agreeing". That fix landed on the value and not on the
comparison twenty lines above it, so the contradiction DETECTOR still read
`bool(d.get("agrees"))` - and the half left behind is the half that decides
whether a refusal is noticed at all.

Measured against `parse_verdict`: a reply refusing in words and then
restating the format - `{"agrees": "false", "reason": "only one response is
cited"}` followed by `{"agrees": true}` - came back `agrees=True`, no
error, carrying the refusal's own reason as the agreement's reason. Same
for `"no"` and `"0"`, which is every spelling in `_FALSE`. With a real JSON
`false` the contradiction fired correctly, and that is the only case the
existing test covered.

- `_as_bool` in the detector. It returns None for anything that is neither,
  and None is a distinct member of that set, so an unparseable answer
  beside a `true` is a contradiction too - no verdict, which is the
  fail-closed direction.

### A dead run read as clean, and a dispute reached nobody, in two of three artifacts

"A dead run looks clean" was fixed once in three readers.

- `render_html` took `extra` in its signature and read it nowhere in its
  body, while `render_report` passed it in. Measured: the same session
  rendered with `extra["error"]` set exactly as `loop.py` sets it, and
  without, produced two report.html files IDENTICAL after normalising the
  session id and timestamps. The dead run's page said "No findings
  recorded." and footered "every finding cites verbatim response bytes
  verified against the recorded transcript". report.md differed correctly.
  report.html is the file this suite calls the one handed to a reader.
- `render_sarif` was not even given `extra` - `markdown.py` called it with
  the session alone - and wrote the literal `executionSuccessful: True` on
  every render. A run that died on authentication emitted that with
  `results: []`, the wire shape of a scan that completed and found nothing.
  GitHub code scanning, Azure DevOps and most CI dashboards read that field
  to tell "scanned, clean" from "scan broke". It is now `not _run_error`,
  with the error carried as a `toolExecutionNotifications` entry.
- Neither renderer read any of the five fields `judge.apply_verdict`
  writes. A `proven` finding a second model disputed kept an unqualified
  green `PROOF: PROVEN` badge with no occurrence of "disput" anywhere in
  the file, and `kind: fail` / `level: error` / `rank: 9.5` in SARIF -
  breaking a build on a finding that model read as a different class. A
  severity the judge lowered vanished the same way: the reduced value shown
  with no record it had been claimed higher. HTML now carries a DISPUTED
  badge and a block naming the judge, its reason, what would settle it, the
  disputed class and the claimed severity; SARIF drops to `kind: review`,
  `level: none`, negative rank, and carries `argus-disputed` for a
  dashboard that wants to decide for itself.

### The redaction held for every field the recorder writes, and no other

`--secret` promises a value cannot persist. Measured on one session with
one declared secret: notes.md, meta.json and agent.log were clean, and the
two artifacts that get emailed were not.

- `record_exchange(note=...)` wrote the note RAW. It is a declared
  parameter of the `http_request` schema - "One-line note stored with the
  transcript entry" - so the value is whatever the model types. On the same
  transcript line, the cookie persisted as `sid=<redacted>` and the request
  body as `pw=<redacted>`, while the note persisted verbatim. The same
  string, scrubbed one field to the left and kept one field to the right.
- `add_finding` stored `title`, `description` and `remediation` raw into
  findings.json, which report.md and summary.json are rendered from. The
  excerpt was safe only INCIDENTALLY: it must be a verbatim substring of an
  already-redacted response, so a declared secret cannot match one. Free
  text has no such constraint, and the model routinely writes observed
  values into a title.
- `judge.render_case` scrubbed the url, the excerpt, the request line and
  both bodies, and interpolated the title raw - in the one function in the
  package that deliberately sends engagement data to a second vendor.

And a defence that preserved what it claimed to redact. `judge._scrub`
substitutes `"".join(m.groups()) + <marker>`, so a pattern's group is the
part to KEEP - `(bearer\s+)` keeps the scheme word and drops the token.
One pattern captured the WHOLE credential:

    AKIAIOSFODNN7EXAMPLE  ->  AKIAIOSFODNN7EXAMPLE<redacted>
    ghp_16C7e42F292c...   ->  ghp_16C7e42F292c...<redacted>

which is worse than no redaction, because it reads as redacted. Split into
three patterns that keep only the type prefix, so a reader still learns
which kind of credential was there. Found while verifying the title fix
rather than from the sweep.

### Closing an MCP server killed what it started, not what it spawned

The `run_capped` orphan, one plane over, and the reasoning in
`_kill_tree`'s docstring applies word for word: an orphan goes on talking
to the target with no scope guard, no rate limiter and no request budget,
nothing it does reaches the transcript, and the run's own record says the
server was shut down. An MCP server makes its own requests outside
GuardedClient BY DESIGN - that is the stated reason `mcp_call`
scope-checks URL arguments at all.

Two things were wrong and the second is the subtle one. The server was not
started with `start_new_session=True`, so there was no group to signal; and
`close()` reaped the leader with `wait()` before asking for its group, so
even with a group `os.getpgid` would raise and signal nobody. A graceful,
successful shutdown left the whole tree running. Measured with a stub
server that spawns a sleeper: the grandchild survived `close()` and
reported `PPid: 1`.

- `_kill_tree` now takes a `pgid` captured while the leader was still
  alive, and `MCPClient.close` captures it before terminating.
- **And refuses to signal its own process group.** The plant for the first
  half - removing the session flag - did not fail the test, it SIGKILLed
  the pytest process, exit 137, with no failure report and no output: the
  child shared the agent's group and `_kill_tree` sent SIGKILL to it. Every
  caller sets that flag, but it is one line away in another file from the
  signal, and if the two part company this helper kills the agent that
  called it. It now falls through to `proc.kill()` instead, which is the
  behaviour it replaced, so the degraded path is no worse than not having
  the helper. `test_kill_tree_refuses_to_kill_the_agent_itself` asserts by
  survival - a process that dies cannot report anything - and planting the
  guard back away takes the runner down with exit 137, which is the least
  debuggable way for a suite to tell you something.

### Removing evidence can only make a negative universal easier

The ledger is sold as the reader that cannot be talked round, "computed
from recorded evidence, so it does not drift with the conversation". It
originated a false positive by itself, with no model involved.

Rule 1 cites a candidate plus its +-3 NEIGHBOURS on the same endpoint - a
window added to bound cost after the whole-transcript version was measured
at over five minutes. `lockout`'s requirement is "a counted series of at
least five FAILED authentication attempts ... NONE of them refused", and
that is a negative universal: every exchange the window drops can only
help it pass. The window was a cost fix, and nothing re-checked the classes
whose requirement has that shape.

Measured against the live lab's `/login3`, which locks after five
attempts. r1-r5 answered 200 "Invalid credentials." and r6 answered 429
"Account locked - too many attempts". The window around r2 is r1..r5 and
omits r6. The same excerpt graded `proven` against the window and
`candidate` against all six, missing "none of them was refused" - and
`argus next` told the operator to record "this target has no lockout"
about a target that had just locked the account in the same transcript.

- The window stays as a FILTER and the grade is confirmed against every
  exchange recorded on that endpoint before anything is recommended. The
  cost argument survives: only a candidate that already passed the cheap
  window reaches the confirmation, so it runs at most once per call, where
  the whole-transcript version graded every candidate that way.
- `evidence_ids` is now the set the grade was computed from. It was
  `[entry.id]` alone while `grade_if_recorded` came from a multi-exchange
  citation, so for every class needing a pair or a series the promise was
  unreachable with the evidence offered. An operator who cites exactly what
  the ledger hands them now gets exactly what the ledger promised, and the
  test asserts that by re-grading those ids.
- The first version of that second test called the helper directly and read
  the citation off its return value, so it never touched the line that
  builds `evidence_ids` - putting the single-id citation back left it
  green. It drives `next_action` now. Fourth time this stretch the
  instrument was the defect, and the first of the four caught by planting
  rather than shipped.

### "Requests sent" was the record counter, in every reader that printed it

`_seq` is shared: `record_event` increments it too, under the same lock,
because the id sequence has to be authoritative over the whole transcript.
Every reader printing "requests sent" read it - report.md, report.html,
summary.json, the loop's own status line and the team summary - so a
scanner run (two events), an `mcp_call`, a `jwt_forge`, an `exploit_run`,
a `cross_verification` and the `artifacts_digest` seal all counted as
traffic to the target. The enforced HTTP counter, `GuardedClient.sent`,
was reported nowhere.

Measured: one request plus five offline `jwt_forge` calls gave
`client.sent == 1` and "Requests sent: 6" - a sixfold overstatement with
zero extra bytes on the wire, printed directly above a per-tool table that
honestly listed `jwt_forge: 5`.

- `Session.requests_sent` counts transcript entries carrying a response,
  DERIVED rather than stored. A counter would need restoring on every path
  that rebuilds a session, and there are two - `_reopen` and the hand-built
  one in `cli.py` - so the next one added would have been wrong and silent.
  `_seq` is itself restored there from the maximum id, which is not the
  number of entries once any were dropped.
- `coverage.requests_by_tool` counted every record too, under a column
  headed "Requests" and documented in docs/EXPERIMENTS.md as "wire
  requests per tool - shows where budget went". It counts exchanges now,
  so the table sums to the total it sits beside, and a tool that spends no
  budget contributes none. That agreement is the assertion that would have
  caught this without anyone measuring: two separately computed figures
  that disagreed in opposite directions.
- The coordinator's watchdog keeps reading `_seq` ON PURPOSE. It bounds
  total work, not the figure anyone reads, and narrowing it to HTTP would
  make it fire strictly later - a loosened safety bound traded for a
  tidier name.
- The committed `docs/sample-session` carries the old figure: 66 entries,
  64 with a response, `summary.json` saying 65. It is left alone. It is a
  faithful record of a real run made by the code that produced it, it
  still verifies, and no document quotes the number.

### Three more things the artifacts stated without measuring

- **report.md emitted the target's bytes into an HTML element it opens
  itself.** The `<details><summary>Transcript ...` line interpolated the
  recorded method, id and URL raw. report.md cannot be rendered with raw
  HTML disabled - its own collapsible transcript sections and its notes
  appendix depend on it - so any viewer that shows those also parses
  whatever the target put in the URL, and the target chooses those bytes:
  the crawler follows its hrefs and the probes build URLs from its
  parameter names. Driven end to end, a loopback target serving
  `<a href='/p?x="><script>alert(document.domain)...'>` produced a live
  `<script>` tag inside that `<summary>`. report.html escaped the same
  value with `_esc`, so the artifact opened in a browser was safe and the
  one read on a forge was not.

  The neighbouring defences were already right and the test now pins them
  too: `_fence` widens for a backtick run in a body and `_code` widens an
  inline span when a URL contains a backtick, so the endpoint line renders
  as ``` `` ...`<img ...>`... `` ``` and does not break out. The
  `<summary>` was the only gap, which is why this is three lines and not a
  rewrite.
- **Two artifacts dated a session to 1970.** `started` is 0.0 when
  meta.json is missing, corrupt or stampless. `markdown.py` guards that and
  prints "unknown (this session's meta.json carries no start time)";
  html.py and sarif.py did not, so the same session read
  `1969-12-31 19:00:00` in one and `1970-01-01T00:00:00Z` in the other -
  local time in one, UTC in the other, so the two did not even agree. The
  date is what an authorisation reviewer checks against the window the
  engagement was authorised for. SARIF now OMITS the key rather than
  faking it: a consumer can see an absent `startTimeUtc` and cannot see
  that 1970 means "no stamp".
- **The engagement-constraints block asserted five configuration facts
  from a file it never read.** Scope, exclusions, proxy, TLS verify and
  tool surface all fell back to definite negatives - "(target only)",
  "none", "no", "no", "all" - and `argus report` needs only
  transcript.jsonl. Measured on a real demo session: with meta.json deleted
  the block was identical to the one rendered with it present, except for
  the budgets degrading to `?`. A run constrained by a scope list, an
  exclusion and a tool subset re-rendered as unrestricted. "TLS verify: no"
  and "Tool surface: all" are claims about how the engagement was
  CONDUCTED, wrong in the direction of a broader, less careful test than
  was run - or, for scope, a narrower one than was authorised - and the
  only signal was a stderr line at render time, after which the re-render
  re-seals and `argus verify` prints OK and exits 0. Both renderers now
  state the absence where the claims would have gone. A present-but-empty
  meta.json still reads "(target only)", because that file recording no
  scope IS the claim that none was set.

### Four guards that held for the value they were given and nothing after it

- **A bundled PoC followed the target off scope, with the credential.**
  `run_exploit` scope-checks the argv and then runs the script as a
  subprocess - no ScopeGuard, no rate limiter, no transcript - and
  `urllib.request.urlopen` follows up to ten redirects by default,
  re-attaching the original headers to each new host. So the TARGET chose
  the final host. Measured: an in-scope server answering
  `302 -> http://127.0.0.1:<other>/api/me`, and that second port received
  `Authorization: Bearer <forged>` while the PoC exited 0 and printed the
  body as proof, with the `exploit_run` event naming only the in-scope
  argument. Both bundled PoCs now refuse to follow a redirect and name the
  host they would not follow; a PoC that needs a second hop has to be
  given that host, so the guard sees it.
- **An empty tool grant permitted every tool.** `AgentLoop.__init__`
  built it as `frozenset(allowed) if allowed else None` and `dispatch`
  reads `None` as "no restriction", so a card granting nothing advertised
  zero schemas and refused nothing. `mcpserver.py` already spells the same
  decision fail-closed, so the package carried both versions of it. The
  first version of the test for this built a Context by hand and proved
  only that `dispatch` was already correct - the conversion that was wrong
  happens before the Context exists, so the test now drives `AgentLoop`.
- **Two more falsy-empty reads in the same constructor.** meta.json
  recorded `"tools": "all"` for an empty grant, which the report prints as
  the engagement's tool surface; and `build_system` was called without
  `allowed` at all, so on the single-agent `--tools` path the delivered
  prompt instructed tools the dispatcher refuses by name. Measured with a
  three-tool grant: 8 instructed tools were refusable and
  `"YOUR TOOLS" in loop.system` was False. That function's own docstring
  says "Pass it. A prompt that instructs a tool the role cannot call
  spends the agent's turn on a refusal and, worse, tells it the engagement
  works in a way it does not."
- **`--exclude /` was stored, reported, and enforced against nothing.**
  `ScopeGuard` keeps `p.rstrip("/")` and skips a falsy prefix, so `/` and
  `//` became `""`: the entry excluded nothing while `exclude_paths`
  stayed truthy as `['']`, `describe()` printed "excluded paths: " with an
  empty value, and the operator's `/` survived into meta.json for the
  report to print as an enforced restriction. Every other malformed value
  in `load_config` raises; this one was silent, and silently not enforcing
  a no-go area is the worst direction for this flag to fail in. It raises
  now, and the guard drops an entry it cannot match so nothing reports an
  exclusion it is not enforcing.

### The evidence store's two gaps: a dedup key half-canonicalised, and a seal nothing compared against

- **One bug, two findings, because the model spelled the port.**
  `record_finding`'s contract is "same bug class + endpoint + params dedups
  to one finding", and the class side is keyed on `proof.canonical` so two
  spellings of a class collapse. The endpoint side used the raw netloc, so
  `http://shop.example/p?id=1` and `http://shop.example:80/p?id=1` - the
  same URI under RFC 3986 6.2.3 - keyed differently and both were recorded.
  `url` is free text ("Affected endpoint") that the model types. Measured:
  F01 and F02, `summary.json` counting `{'high': 2}`, report.md printing
  `| High | 2 |` over two cards for one bug - a severity count a client
  reads, inflated by a port number.

  Only the normalisations RFC 3986 calls equivalent: scheme and host case,
  and an elided default port. A trailing slash is not one of them and a
  relative URL has no authority to normalise against, so neither is merged
  - over-merging would hide a second real finding, which is worse than the
  duplicate it prevents. The SCHEME stays out of the key, which is
  pre-existing rather than overlooked: the old netloc carried no scheme
  either, so http and https already keyed the same. Measured while making
  this change and left alone, because a target redirecting http to https
  would otherwise produce two findings for one bug.
- **A file added after sealing was invisible.** The seal enumerates a
  whitelist resolved at seal time - `glob("agent*.log")` among it - and
  `verify_transcript` only iterated the names it recorded, so nothing ever
  compared the directory against the seal. A file created afterwards was
  invisible INCLUDING one matching that glob exactly: an `agent-ghost.log`
  dropped into a sealed session verified clean under a human line reading
  "artifacts sealed" that names nothing. Only `--json` ever printed the
  covered set.

  Reported, not failed. `ok` means the chain is intact and the sealed bytes
  still match, and an addition breaks neither - an operator may
  legitimately leave a screenshot beside the run. What it must not do is
  pass unmentioned while wearing the name of covered output. Measured on a
  real `argus demo`: the directory holds exactly the sealed files plus
  transcript.jsonl, which the hash chain covers instead, so the check has
  no legitimate occupant to cry wolf over.

### Two bounds applied one statement too late

- **The frame cap fired after buffering the thing it bounds.** `serve()`
  read `for line in self._in` and then checked `len(line) > _MAX_FRAME`.
  Iterating lines must finish buffering the whole newline-free run before
  `len` can be evaluated - and the comment above that check had the
  reasoning exactly right ("a host that sends megabytes without one buffers
  all of it") while the code did that very thing. Measured on the real
  `argus mcp-serve`, peak VmHWM against newline-free input, both ways:

  | input | before | after |
  | --- | --- | --- |
  | 8 MiB | 65,096 kB | 60,880 kB |
  | 64 MiB | 179,912 kB | 69,012 kB |
  | 192 MiB | 345,752 kB | 68,728 kB |

  `readline(limit)` is the primitive for this - it stops at a newline OR at
  `limit` characters. A fixed-size `read(n)` would be the wrong fix for the
  same reason it was wrong two bounds away in `httpclient`: it blocks until
  it has n characters, which would stall a line-oriented protocol between
  frames.

  The existing cap test feeds `"x" * (_MAX_FRAME + 1) + "\n"` through an
  `io.StringIO` that already holds the whole string, so it asserts the
  error wording and cannot see the memory. The new one hands the server a
  stream that GENERATES lazily and records the largest string it was ever
  given; with the old reader it reports being handed 67,108,865 characters
  for a 4,194,304 byte cap.

  And the test double had to be fixed first: `_Pipe` implemented only
  `__iter__`, which is what the old loop used, so it was modelling the
  implementation rather than the stream contract. A real `sys.stdin` has
  `readline`; now so does the double.
- **`mcp_call`'s timeout bounded only the second half of what it did.**
  `_start()` is lazy, so the first call on a server also runs `initialize`
  - and that RPC used `self.timeout_s`, the per-server value, which
  `MCPManager` accepts up to 600s. Measured against a server that starts
  and never writes: `timeout_s=5` returned after 30.0s with the default
  config and after 45.0s with a declared `timeout_s: 45`. Worse than one
  slow call, because `_start()` runs inside `self._lock` and the manager is
  shared by every worker thread, so one caller's handshake blocks all of
  them for a bound none of them asked for. `min()` with the server value,
  so a server declaring a shorter timeout still wins.

### Four numbers presented as measured

- **A crashed team worker was priced at $0.00 and counted as priced.**
  `_cost_breakdown`'s own rule is "every agent unpriced is not a free run:
  it is an unknown one" - applied to an unknown MODEL and not to unknown
  TOKENS. `_start_worker`'s crash handler stores
  `{"error": ..., "turns": 0}` with no `llm_tokens`, so an empty dict
  reached `spec.cost(0, 0)`, returned 0.0, incremented `priced` and was
  filed as a priced line - and `priced` is what decides whether the team
  total is a number at all. Whatever that worker spent before it raised is
  still sitting unread on `loop.llm.input_tokens`, so the figure was not
  merely unknown, it was known to be wrong.

  The existing test asserted `out["usd"] == 0.0` for agents that reported
  nothing, which encoded the defect rather than the property its name
  describes. It asserts None now, with the reason in the test so a reader
  can tell a correction from a convenience.
- **`compare --by-arm` medianed token figures over a subset.** The
  all-or-nothing guard held `usd` and not the quantities `usd` is computed
  from: `_flatten` makes `tokens_in`, `tokens_out`, `cache_read` and
  `cache_write` None the moment a trial's summary.json has no
  `llm_tokens`, and one real command reaches that state - `argus report`
  on a session whose summary.json is missing or unparseable takes the
  no-carry-forward branch and rewrites it without those keys. `llm_calls`
  was worse than unguarded: `s.get("llm_calls", 0)` defaulted a missing key
  to zero, so a fabricated measurement entered the median AND the guard
  could never fire, because the value list looked complete.
- **`argus judge` counted a judge it never reached as a dispute.**
  `apply_verdict` already distinguishes three states - "A transport failure
  or an unparseable reply is NO VERDICT, which this module's own docstring
  says is not a dispute" - and records `disputed` only when
  `not agrees and not error`. The CLI looked at `agrees` alone, which an
  error verdict sets to False, so an unreachable judge printed
  `DISPUTES F01` and summed into "0 agreed, 1 disputed" while findings.json
  carried no `disputed` flag and report.md said no verdict was obtained.
  The command exits 0, so nothing else said the cross-verification had not
  happened.
- **"about N probe calls" was a constant divided by a count.**
  `REQUESTS_PER_PROBE` is 12 for every probe; measured against the lab, one
  call records probe_reflection 1, probe_cmdi 3, probe_redirect 3,
  probe_ssti 8, probe_lfi 8, probe_sqli 11, probe_ssrf 11 - a 1-to-11
  spread across 26 probes. At 61 recorded probe_reflection requests, which
  on this lab is 61 calls, rule 5 printed "about 5 probe calls", and the
  action's detail carried the same figure under a key of its own - both
  named in `decide.py`, which the doc gate does not read, because the key
  no longer exists to be named here. The transcript carries no call
  boundary (an
  entry has chain, id, request, response, tool, ts), so calls are not
  derivable from the evidence at all. Both figures are gone; the message
  names the requests and the budget, which are. The constant stays as a
  budget, which is policy and not a measurement.

Three of these four tests had to be fixed before they could fail. The
by-arm one re-implemented `_values` locally and never touched the dict that
creates the defaulted zero; the judge one asserted the CLI's SOURCE, which
is the weak shape this log has recorded before; and the rule-5 one SKIPPED
when a higher rule fired first, which asserts nothing. All three drive the
real path now.

### The last two bounds the target set the cost of

- **The wall clock bounded the turn and not the batch.** `remaining_time`
  is computed once at the top of a turn and nothing inside the turn
  consulted it, so a whole `tool_uses` batch was dispatched sequentially
  to completion before the budget was looked at again - and the exhaustion
  branch then issues up to two more nudge turns, each answered with a full
  batch. The per-call cost is the target's: the 15s read timeout bounds
  one read, not the engagement. Measured against the lab's own sleep
  endpoint with a 1.0s budget and a model emitting three tool_use blocks
  per turn: **72.4s and 9 requests**, 72x, and it scales with the batch.
  After: 8.1s and 1 request.

  What that remaining 8.1s is, and what this does not fix: the call
  already on the wire when the clock runs out still finishes. Aborting it
  mid-flight is a different change; it is bounded by the read timeout.
- **An undeadlined DNS lookup per new in-scope host.** `getaddrinfo` takes
  no timeout and ran on the agent's own thread, and the target chooses how
  many new hosts there are - `include_subdomains` defaults to True and
  `crawl` queues every in-scope-looking href out of the target's HTML.
  Measured here: 15.0s for a fresh in-scope subdomain inside `check()`, and
  24.1s for a bare lookup where no resolver answers. Now a daemon thread
  with a 2.0s join, the pattern `analysis._resolves` already uses and for
  the reason recorded there: `setdefaulttimeout` is process-global and
  would leak into the target connections and the lab's own server.

  The lookup is also skipped entirely when `--allow-private` is set, where
  its answer cannot change the outcome - which is every lab run and every
  internal one, the runs most likely to touch many hosts. Measured: 0.000s
  through `check()` with a 30s resolver in place.

  **The verdict is deliberately unchanged, and that took two attempts.**
  Fail-closed went in first: a timeout returning "private" so a slow
  resolver could not carry a private address past the one check that
  catches it. Two things came of it.

  First, it broke the OTHER caller. The constructor reads the same function
  to decide whether the TARGET is private, and a target whose own lookup
  timed out then set `allow_private` for the whole session - one function,
  two questions, opposite conservative answers, the same shape as
  `_window`'s start earlier in this log. Caught because the test for the
  fix drove the real constructor and stopped raising.

  Second, and decisive: fail-closed refuses in-scope hosts in any
  environment without a working resolver. `test_subdomain_allowed_by_default`
  and `test_extra_hosts` both failed on it here, which is two real
  engagements' worth of behaviour rather than a test artifact - a 2s
  deadline cannot tell "no resolver" from "slow resolver", and this
  function already answered "unresolvable" with False on the stated
  grounds that nothing can connect anyway.

  So the COST is the defect and the bound is the fix. A timeout returns the
  same False, and warns once per host naming what was not checked, because
  changing a security posture as a side effect of bounding a lookup is a
  different change and the operator's to make. What that leaves open,
  written down rather than implied: an attacker who controls the
  resolution TIMING of an in-scope hostname can keep a private address from
  being seen here, since the connection that follows resolves
  independently.

  Four plants fire - no deadline, silent on an unchecked host, lookup runs
  under `--allow-private`, and the constructor coercion dropped... and the
  fourth does NOT, which is recorded beside it: with a timeout now
  returning False the coercion is inert, and it is kept to stop one
  specific mistake recurring rather than because a test can see it.

### Re-reading the sweep's own refusals

The 38 confirmed findings are closed. The adversarial verifiers were told
to default to `refuted: true` when they could not decide, so a false
refusal is expected by construction - and all 19 refusals begin with
"REPRODUCES". They were refused on consequence, on intent, or on
reachability, not on the mechanism. Two of them were worth re-reading, and
one of those was worth acting on twice.

- **A quote had to be contiguous in the joined evidence text, not in any
  part of it.** `_evidence_text_of_entry` built
  `"\n".join(headers-JSON, each "k: v" line, body)` and the gate tested
  containment against the join, so `"x-injected: yes\n<html>hello"` - half
  a header line and the start of the body - was "a verbatim substring of a
  cited response" while being a substring of no part of one.

  The refusal was right that this is not a false positive: `_echo_check`
  matches against `resp_body` alone, sits in every class's veto tuple, and
  a straddle swept across all 29 classes grades
  `{'unproven': 28, 'refused': 1}`. It was wrong that nothing follows. The
  grade is a different claim from the gate's: `findings_bad` is what
  `argus verify` and an `argus report` re-render use to decide whether a
  quote still verifies, and "N findings re-validated" is a statement about
  the EXCERPT. Containment is per part now, and the fix is free - a body
  quote, a wire-style `k: v` line and a fragment of the headers JSON each
  match a part exactly as they matched the join.
- **A rate the table knew was wrong, recorded instead of applied.**
  `models.json`'s entry for claude-haiku-5-5 read "0.10/0.50 per MTok for
  prompts up to 100K tokens and 0.50/2.50 above it - this table holds one
  pair, so a long-prompt run under-reports by 5x". Measured on the real
  `Model.cost`, 200K in and 1K out: $0.020500 against $0.102500, exactly
  5.00x.

  The refusal was "already known and recorded", and it is - in the note
  and in this file. But recording a wrong number in a note is not the same
  as not printing it: the note reaches a reader of models.json, the figure
  reaches the operator reading a cost in report.md. The schema holds
  `tiers` now and the entry carries the published pair, so the 200K run
  prices at $0.102500. The threshold is on the PROMPT - fresh input plus
  cache reads plus cache writes - which is a choice, so it is stated in
  the code and asserted in the test: counting `tokens_in` alone would put
  a cache-heavy run in the cheap tier on a prompt that was not cheap.

Checked and left alone: selftest's "the default model is priced and
current" check is not vacuous - planting a deprecated default and an
unlisted one both drop it to 157/158.

### "Unpriced is not free" was written once and applied to one input

A third refusal, re-read and acted on - and the third instance of one
shape, which is worth naming.

`AgentLoop._cost_stats` says it: "A cost that cannot be traced to a price
someone can check is a made-up number, so an unlisted model reports
`usd: null` and says so rather than guessing a rate." `TeamRun`'s version
says the same thing: "every agent unpriced is not a free run: it is an
unknown one." Both applied it to an unlisted MODEL and neither applied it
to absent TOKENS - so

- a crashed team worker, whose result dict carries no `llm_tokens`, was
  priced at `spec.cost(0, 0)` = $0.00 and counted toward `priced` (fixed
  earlier in this stretch), and
- a single-agent run whose provider or gateway omitted `usage` reported
  "Model cost: $0.0000 USD (0 in / 0 out / 0 cache-read tokens)".

The second was refused by the sweep as "already known and recorded", and
what is recorded is a different decision: commit 68ab807, "tolerate
non-object JSON and non-int usage fields from gateways", made the parser
not crash on a malformed `usage`. That is right, and it is not the same
call as pricing the result. Measured on a plausible deliverable: 4 LLM
calls, 3 wire requests, a written executive summary, `usage` omitted -
`$0.0000 USD`, `error: null`, no banner, and `argus verify` printing OK.

Calls-with-no-tokens is the signal rather than tokens alone, because a
call always has input: a run that made no calls really is free and still
reports `$0.00`. The report already had the branch for an unpriced run
("naming the reason beats printing 0.00, which reads as free") and now
reaches it: **Model cost:** not priced - 4 model call(s) reported no token
usage.

### An accepted residual that was also an invisible one

A fourth refusal re-read. This one was refuted correctly and still left
something to do.

That a re-render re-seals is documented in four places, and
docs/ARCHITECTURE.md states the residual in its own words: "`argus report`
recomputes the artifact digests, which is what makes a legitimate
re-render verify - and therefore what lets an edit made before the
re-render come out the other side digest-valid." The mitigations named
there are real - the grade is recomputed from the transcript, and
`--seal-key` closes the forgery case.

What was missing is that the only signal of the edit was a stderr line at
render time. The sequence measured end to end: `argus verify` prints
`TAMPERED: ['findings.json']`; `argus report` warns, re-renders and
re-seals; `argus verify` afterwards prints `OK: 68 chained entries
verified ... artifacts sealed` and names nothing. A reader of the session
later cannot see that a mismatch was ever there, which is the difference
between an accepted residual and a hidden one - and the same shape as the
file-added-after-sealing finding earlier in this stretch, where the signal
was also transient and the fix was to make it durable.

The transcript is an append-only hash chain, so an event recorded at
re-render time cannot be removed without breaking the chain. `argus
report` records `reseal_over_mismatch` naming the files, `verify_transcript`
surfaces it, and `argus verify` prints it as a note beside the OK:

    note: r66: this session was re-rendered and re-sealed while
    findings.json did not match the seal - the digests above cover the
    edited bytes, and the grades were recomputed from the transcript

This does not close the residual and does not change the exit code: the
seal really does match now, and the chain and the recomputed grades are
the signals the documentation already names. It stops the residual being
silent.

The test's first version set `severity = "critical"` on a finding that was
already critical, wrote identical bytes back, and asserted a mismatch that
never happened - caught because it failed unplanted.

### Two source-grep tests replaced, and four kept for a measured reason

A fifth refusal re-read: "both tests guarding the SARIF unknown-grade
default assert a substring of the function's source". The refusal proved
the behaviour IS guarded - it mutated `sarif.py` at source level and both
tests failed - so the central claim was false. What it did not address is
that there are six `inspect.getsource` assertions in `tests/test_proof.py`,
and this repo has already recorded that shape as weak: a grep passes while
the behaviour is broken in a way that keeps the substring.

**Two were replaced.** `test_sarif_never_defaults_an_unknown_grade_to_a_
build_break` was two lines and a substring assertion - the same substring
the test above it asserted, so a duplicate of a source grep rather than a
second check of anything. Both now render SARIF over hand-built findings
and assert the rows: an unrecognised grade (absent, empty, `"bogus"`, None,
7, a list) must come out `kind: review`, `level: none`, negative rank.

Writing it behaviourally found something the grep could not. A first draft
listed `"PROVEN"` among the unknown grades and FAILED, because `sarif.py`
reads `str(...).strip().lower()`: case and surrounding space are folded, so
`"PROVEN"`, `" Proven "` and `"\tproven\n"` are the proven grade and
render as `fail`. That folding was asserted nowhere. Both behaviours are
pinned now, and both plants fire.

**Four were kept, and the reason is measured.** The obvious next move was
to delete the rest as redundant with the proving table, which drives every
probe against the live lab. Planting says otherwise. Removing the canary
from `probe_method`'s written body fails its source assertion and leaves
`test_the_probe_collects_what_its_class_requires[probe_method-method]`
PASSING - because `method` has two routes to `proven` and the table needs
only one honest quote to reach it, so the class still proved via TRACE:
"argustr1n6b6pwk was sent as a request header and came back in the body".

And the write route is not merely unpinned there - it never runs against
the lab. `probe_method` gates its PUT on `if "PUT" in allow.upper()`, and
the lab's `/files/` answers OPTIONS without advertising PUT: the only
exchanges a run records are `OPTIONS /files/` and `TRACE /files/`. So the
verifier side of that route has synthetic coverage, the probe side has a
grep, and nothing drives the two together.

Both facts are written at their own sites - beside the grep, so it is not
deleted as redundant, and in the proving table's docstring, because "a
class with two proof routes cannot be pinned by a table that asks whether
SOME quote grades" is a limit of that table and not of this one class.
Closing it needs a lab endpoint whose `Allow` lists PUT and which stores
the body, which changes what `probe_method` sends in every proving-table
run - so it is named rather than done as a side effect.

### A fix that created the precondition for another finding

The sweep refused "a team report prints the priced subset's total as the
run's cost" on reachability: the state needs an agent that cannot be
priced BESIDE agents that can, and it got there with an agent whose MODEL
is absent from `models.json`, which the real spawn path cannot produce.
That refusal was correct about the tree it was written against.

It is out of date because of a fix in this same stretch. Making a crashed
worker UNPRICED - because pricing its missing `llm_tokens` at
`spec.cost(0, 0)` = $0.00 and counting it toward `priced` was worse - is
exactly how a run reaches "one agent unpriced, the others priced". A
worker raising is ordinary.

And the renderer's behaviour was already measured by the refusal itself:
"does report.md mention the unpriced agent at all? False". The cost line
read `unpriced` only on the branch where there is no figure at all, so
with a figure present a reader saw a definite number and nothing saying it
covered part of the run.

The figure now carries the disclosure where the figure is:

    - **Model cost:** $0.0140 USD (200000 in / 7000 out / 0 cache-read
      tokens, model table v2) - PARTIAL: 1 agent(s) could not be priced
      (exploit-1 (no token record: RuntimeError: boom))

A fully priced run is unchanged, and the no-figure branch still names its
reason. The lesson is the one worth keeping: a fix that creates the
precondition for another finding has to close that one too, and a refusal
on reachability expires the moment the reachability changes.

### A proof route that was unreachable by construction

Documenting the `method` write route as uncovered turned out to be the
wrong stopping point: it was not merely untested, it could never have
graded. `verify_method_effect` has two routes to `proven` - a TRACE that
echoes a header the probe sent, and a PUT whose bytes a later GET returns
- and only the first had ever run. Three things had to be true at once
before the second could, and none of them was:

1. `probe_method` sent PUT only when `Allow` advertised it
   (`if "PUT" in allow.upper()`), while the verifier counts a write method
   only when the endpoint should have REFUSED it (`unadvertised =
   advertised is not None and method not in str(advertised).upper()`). The
   probe sent PUT exactly when the verifier would not count it, and never
   when it would.
2. The lab had no endpoint honouring a write verb. A run against `/files/`
   records exactly `OPTIONS /files/` and `TRACE /files/`.
3. The probe asked OPTIONS of the COLLECTION and wrote to a child, and the
   verifier reads `Allow` from an exchange with the same endpoint shape -
   so `advertised` stayed None and the check could not fire even against a
   vulnerable endpoint.

That is the shape AGENTS.md names: "the probe announced a signal whose
evidence could never grade, because nobody read the requirement while
writing it". So the whole write half of that verifier - the body
read-back, the nonce that ties it to this run, and the ordering check
added earlier in this stretch - had never run against a target.

- `/dav/` in the lab answers the same `Allow: GET, POST, OPTIONS, TRACE`
  as everything else and honours PUT and DELETE anyway. The disagreement
  IS the bug. A first version advertised PUT and the class correctly
  refused to grade it: a REST resource honouring PUT on its own path is
  the service working, which the synthetic test for this class already
  says in as many words, so advertising it would have made the lab teach
  the wrong thing.
- `probe_method` sends the PUT whether or not it is advertised - that is
  the test - and asks OPTIONS of the path it will write to. The canary
  file goes to a path that did not exist and is DELETEd, which this probe
  already did on the advertised branch; the cleanup is now asserted.
- A bug of mine in the lab, caught by the gate: `do_PUT` answered 405 for
  a non-`/dav/` path WITHOUT reading the body, so with keep-alive the next
  request parsed the leftover bytes as its request line. The following
  TRACE came back without the header it echoes and the whole class dropped
  to `unproven`. Two tests failed and neither was looking for a desync.

And a check retired for the right reason. The source assertion on
`probe_method`'s body was kept an hour earlier with a measurement saying
it was load-bearing - removing the canary failed it and left the proving
table green. Making the route run retired it: the behavioural test fails
on that plant too, so the grep is redundant and over-constrains what it
duplicates. The reason it was kept expired, and the note where it stood
says so.

### The proof gate graded three classes on evidence that did not prove them
A route audit of every multi-branch verifier - "which branches does the lab
exercise, which are unreachable, which are merely untested" - returned four
false proofs. Each was reproduced against the live lab before being touched,
and each fix was planted back and required to produce the named symptom.

- **`sqli` graded `proven` on a page with no database behind it.** The
  fingerprint check scanned the whole cited set and was tied to nothing, so
  ONE request - `GET /search?q=sqlite_version SELECT x FROM users` against
  the lab's reflected-XSS search box - passed all six checks: `DBMS_RE`
  found `sqlite_version` in the RESPONSE because the response was the
  request coming back, `TABLE_RE` found `users` in the request, the quote
  was the page's own `Results for:`, and nothing ever asked whether the body
  held rows. A genuine `sqlite3.OperationalError` from `/item?id=1'` plus
  that same reflection graded `proven` too: the banner was real, and real
  about a different endpoint. The banner is now suppressed when the request
  carries it - the suppression written three lines below for `records` and
  not for `banner` - and has to be on the endpoint the rows come from. The
  honest pairing is untouched: the probe's own run still grades `proven`,
  `data store fingerprinted | sqlite3.OperationalError in r2`, and
  `argus verify docs/sample-session` still re-validates all 6 findings.
  `verify_operator_injection` was split out of this function to escape this
  exact shape and its docstring has said so since; the rule had been applied
  to one of the two places it is true.
- **`csrf` graded `proven` with nothing changed.** The before/after pair
  required "the SAME resource" and asked `_endpoint_shape`, which collapses
  record ids on purpose - without that, idor is unprovable on any API whose
  ids are not integers. So GET `/api/user/1`, a cross-origin POST to
  `/api/config` which never touches `/api/user`, then GET `/api/user/2`,
  quoting `"username": "alice"`: six checks, six PASS, "absent in r1 before
  the write, present in r3 after it". Alice was always user 2. New
  `_resource_key` keeps the ids; `_endpoint_shape` still answers the idor
  question about the same two URLs, and a test pins both answers.
- **Half the payloads `probe_deserialize` sends could not satisfy the
  class's floor.** `SERIALIZED_RE` gates "a serialized payload was sent",
  and 5 of 10 were invisible to it - including the probe's own
  node-serialize payload, because the alternation was `$$ND\b` while the
  real marker is `_$$ND_FUNC$$_`, so the character after `ND` is a word
  character. Also missing: the base64 pickle and Ruby Marshal magics while
  the Java one was present, the raw Marshal magic, and `$type` - Json.NET
  type resolution, the common real .NET vector - while three .NET gadget
  NAMES were there. Both base64 prefixes are derived from the bytes:
  b64(`\x80\x04\x95`) = `gASV`, b64(`\x04\x08o:`) = `BAhvOg`. The
  payload list is now the module constant `probes._DESER_PAYLOADS` and a
  test grades the real list against the real pattern, so a payload the
  pattern does not know fails the suite. The agreement table could not see
  this: it asks whether SOME quote reaches the ceiling, and the lab
  executes the yaml payload, which always matched.
- **Two status tests counted an exchange the target never answered.**
  `status_of(e) < 400` is also true of 0, which is how `GuardedClient`
  records a transport failure; four of the six status tests in `proof.py`
  bound the range below with `200 <=` and `verify_data_extraction` and
  `verify_graphql` did not. Latent, not reachable - the same branch records
  an empty body, so the excerpt check fails first - and fixed where it is
  written rather than left standing because it happens to be unreachable.
  The first attempt at this dropped the `bool(entry)` guard every other
  status site in the module opens with, and `_witness` hands `build` a
  `None` candidate when nothing is cited:
  `test_no_spec_declares_a_check_its_verifier_never_emits` caught the
  AttributeError.

Still open and measured, not closed: the route audit's 37 verify agents died
on DNS, so its remaining claims are unverified.

### A redirect does not need a Location header to leave the origin
Follow-through on the audit finding above, which is the same shape as the
`verify_method_effect` write route: the lab plants a bug, the probe reports
it, and no verdict can be recorded for it.

- `/jsredirect` answers 200 with `<meta http-equiv=refresh>` carrying the
  destination from the query - vulnapp.py calls it "client-side open
  redirect: no Location header at all" - and `probe_redirect` reports it as
  "open redirect (client-side, via meta-refresh/JS)". Both of the class's
  checks read `header_of(entry, "Location")`, so the best honest quote over
  the whole probe run graded `unproven` while `/redirect` and `/safedirect`
  graded `proven`. New `_redirect_destination` reads the header first and
  the body second - a meta refresh or a script assigning `location` - and
  the detail line says which route it took. The "host we supplied"
  requirement is what keeps this from grading every page with a CDN in a
  script tag; a hardcoded vendor host in the same shape still does not
  grade.
- `_redirect_host` ended with a line that read a schemeless value as a host.
  It could not run for any input: `urlparse` populates `netloc` only for a
  value starting `//` or carrying a scheme, and both branches above it
  already took those, so its own guard fired for everything that reached it.
  Measured over 12 Location shapes. Had it run it would have been a false
  positive - `Location: example.org/path` is a relative reference, which a
  browser resolves against the current origin - so the line is gone and a
  test pins the answer instead. Putting the line back does NOT fail that
  test, which is the evidence it was dead; the test says so.
- The lab plants three redirect shapes and the proving table drove one.
  `/safedirect` (protocol-relative `//host`, past a filter that allows it)
  and `/jsredirect` are now driven by a test in the same module, which
  asserts the probe still reports each shape AND that the matrix grades it -
  not a table row, because every row's first element has to name a tool in
  the registry and these are extra endpoints for one tool.

### A cross-origin handshake and an answer from a different socket
`verify_websocket_channel` tied the frame to the handshake with
`_endpoint_shape`, which is the same URL and nothing more - so a
cross-origin handshake that framed nothing paired with an answered frame
from a DIFFERENT connection, and the verdict said "the channel answered a
message" about a channel that never carried it. Measured: two
`probe_websocket` runs against the lab's `/ws`, citing run 1's handshake
with run 2's frame, graded `websocket` **proven** on "argusws4v1faio8 sent
and returned on r4".

Nothing in the record could tell the two halves of one socket apart: the
frame carried the same URL as its handshake and nothing else, though
`send_ws` has always known both exchange ids and returned them to its
caller. It now stamps the frame with its handshake's id (`on_handshake`, a
recorder field, not a wire header) and the verifier requires the frame to
have ridden the handshake whose Origin the claim rests on. The failing
detail names the pair: "r4 rode r3, not r1 - the frame has to be on the
same socket as the cross-origin handshake, not merely the same URL".

Two consequences, both deliberate:

- a frame recording no handshake cannot be correlated and does not pass, so
  a transcript written before this field existed reaches `candidate` here
  rather than `proven`. The detail says to re-run the probe on this build.
  No shipped artifact is affected - `docs/sample-session` has no websocket
  finding, and `argus verify` still re-validates all 6 of its findings.
- the Origin search now collects every foreign handshake instead of
  stopping at the first. It stopped at the first and then looked for a
  frame, so one foreign handshake that framed nothing hid a second one that
  did.

`_ws_frame` in the tests takes `rode` as a required keyword-only argument,
for the reason `_ex` takes `ts`: a real frame always carries one, and a
fixture without it is not the shape the recorder writes. Defaulting it to
the handshake id would have hidden the requirement it exists for.

### Two audit findings that were wrong, and the one under them that was not
The route audit classified branches as EXERCISED, UNTESTED or UNREACHABLE.
Three UNREACHABLE claims were checked by hand before anything was deleted,
and two of them were wrong in a way that would have cost real coverage.

- **The percent-encoded traversal branches are live.** `req_text` unquotes
  once, so the audit's reasoning was that `%2e%2e` never reaches
  `TRAVERSAL_RE` - and for a singly encoded payload that is exactly right:
  `?file=%2e%2e/etc/passwd` arrives as `../etc/passwd` and matches the plain
  branch instead. The conclusion does not follow. One unquote of a DOUBLY
  encoded payload leaves `%2e%2e` standing, which is the whole reason the
  alternation exists - it is what gets past a filter that decodes once.
  Measured, each branch firing one layer deeper than the last:
  `%252e%252e/etc/passwd` matches `%2e%2e`, `..%252fetc` matches `..%2f`,
  `%25252e%25252e/x` matches `%252e`. A test pins the ladder with the
  measurement next to it, because the next reader of that audit would
  delete three live branches.
- **`/graphql-strict`'s ungradeable suggestion leak is recorded as
  deliberate.** The lab plants "introspection disabled BUT did you mean
  still leaks schema names", `graphql_introspect` reports it, and no route
  grades it - which reads like the `verify_method_effect` write route and is
  not. `/graphql-strict` is the CLEAN row of the proving table, so the suite
  asserts that driving it does NOT reach proven: introspection refused is a
  lead for the operator to follow, not a proof of this class. Measured, both
  reasons it cannot grade: the suggestion response is `asked=False` and
  `declined=True`. Adding a route would have broken the row that records the
  decision.
- **Under the second one, a real false negative.** `asked` matched
  `\bquery\s*\{`, which needs `query` followed by whitespace and a brace -
  and in `{"query": "{users{id email role}}"}`, which is how every GraphQL
  client sends a query, the next character is a quote. Introspection still
  matched via `__schema`, so the class's first half worked and its second -
  "or a query returning records outside scope" - was unreachable through
  the standard transport, because `records` is gated on `asked`. Measured
  False on three real shapes, one with `variables` and one with
  `operationName`. The pattern now matches the envelope only when the value
  is a selection or an operation: matching `"query":` alone would have
  graded every search API that names its parameter `query`, and
  Elasticsearch's `{"query": {"match": ...}}`, as having sent a GraphQL
  query - and `records` would then have done the rest on any JSON listing.
  All three stay False, and both graphql rows of the proving table still
  grade as before.

The lab answers `{"data": {}}` to any non-introspection query, so no lab
endpoint drives that second half, which is why nothing noticed. Driving it
needs a lab endpoint that answers a data query - recorded, not built.

### A control on a different record is not a control
Found by grepping the callers of a helper whose own docstring explains why
it is lenient. `_endpoint_shape` collapses record ids deliberately -
without that, idor is unprovable on any API whose ids are not integers -
and it had three callers asking the strict question instead.

- `verify_state_change`'s read pair, fixed above.
- `verify_operator_injection`'s control filter. Measured: `POST
  /api/user/1 {"id":{"$ne":null}}` answered 200 with a document, plus `POST
  /api/user/99999 {"id":"99999"}` answering 404 because that record is not
  there, graded `nosqli` **proven** on "r2 was refused 404 and r1 answered
  200". The 404 is what that endpoint says about any missing id; it had
  nothing to do with the operator. The filter now uses `_resource_key`, and
  a control on the same record without the operator still proves.
- `verify_unkeyed_input`'s poisoner/victim pair, checked and **kept
  lenient**, with the reason now written next to it: for an unkeyed cache
  the marker crossing into ANOTHER record's response is a wider blast
  radius for the same poisoning, not weaker evidence, and the excerpt also
  has to be absent from the victim's own request.

The same collapsing is correct in one of the three and wrong in two, which
is why the question has to be asked per caller rather than globally. Third
instance this session of one helper answering two questions whose
conservative directions are opposite.

### Two more reads that were cited as evidence of something they never saw
Same family as the control fixes above, in the two verifiers whose proof is
a contrast.

- **A `before` read that TIMED OUT proved a state change.** "The excerpt
  was not there before" is trivially true of a read that returned nothing,
  and `GuardedClient` records a transport failure as status 0 with an empty
  body. Measured: a read recording `ReadTimeout: timed out`, a cross-origin
  POST, and a successful read after it graded `csrf` **proven**, with the
  detail "absent in r1 before the write, present in r3 after it" about an
  exchange that observed nothing at all. A single flaky timeout before the
  write was the whole proof. `_answered` guards it now - on that side only,
  because `after` requires the excerpt to BE in the body, which a status-0
  entry cannot satisfy, so a guard there would be one no test could tell
  from its absence.
- **`verify_file_read`'s control was not required to be the reader.** It
  was any cited exchange whose request was traversal-shaped and whose body
  lacked a sentinel, anywhere in the set, so a 200 on `/search` served as
  the control for a read on `/download`. That leaves unruled the one thing
  a control exists to rule out - the docstring's own words, "so the
  sentinel is shown to come from the file and not from the page" - because
  a page on another endpoint says nothing about this one. The realistic
  shape is a file-manager page that documents `/etc/passwd`; the first
  version of this verifier was fixed for exactly that, with a blog post,
  and the control was that fix scoped to the citation instead of to the
  reader. Here `_endpoint_shape` IS the right question, unlike in the three
  callers corrected above: `/download?file=X` and `/download?file=Y` are
  one reader with two paths, which is the contrast itself.
- **And the same edit closes a false negative.** The control had to match
  `TRAVERSAL_RE` itself. An absolute-path witness does - `/etc/passwd` is
  in the known-path list - while its honest control `/etc/nope` matches
  nothing, so citing a real read with its own 404 graded `candidate` and
  nothing said which half was missing. On the same reader, any answered
  response without the sentinel makes the point, including the harmless
  baseline the probe already sends.

### A credential in `API-Key:` was written to the transcript verbatim
Two lists describe the same thing and disagreed about one header.
`proof._CREDENTIAL_HEADERS` names the headers a request can present a
credential in, and has included `api-key` all along.
`httpclient._SENSITIVE_REQ_HEADERS` had `x-api-key` and not `api-key`, and
it decides two separate things: whether a value is redacted before the
transcript is written, and - through `credential_fingerprints`, which gates
on the same set - whether a digest is recorded for it.

Both halves measured through the real recorder:

- `API-Key: sk-live-...` persisted to `transcript.jsonl` **verbatim**,
  while the same secret in `X-Api-Key` was redacted. That file is the
  hash-chained artifact an operator hands to a client, so the leak is
  sealed in rather than merely present. Re-measured after the fix: the
  secret appears 0 times on disk, where it appeared once.
- no digest was recorded for that header either, and
  `verify_token_forgery` links a mint to the request that carried it BY
  that digest - the mechanism whose missing half is described at
  `credential_fingerprints`. A forgery sent in `api-key` could not be
  correlated at all, so the class's second check was unreachable through
  that header.

One set, both consequences; `apikey` went in beside it, since it is the
same header as many APIs spell it. `_credential`'s list is now the module
constant `proof._CREDENTIAL_HEADERS` and a test asserts the subset
invariant against the real lists, so a header added to either one cannot
silently go uncovered. Redacting more REQUEST headers cannot cost a
finding: evidence text covers response headers, bodies and event output,
never request headers, which is the invariant recorded at the set itself.

### Payloads two classes could not see, found by sweeping probe against gate
Generalising the deserialize finding: for every probe, does the request-side
check that gates its class recognise the payloads the probe scores as hits?
Swept all 27 probes; 18 mismatches claimed, and these are the ones that
survived being reproduced here by hand.

- **Two of the five template families `probe_ssti` sends were invisible to
  the only gate into their class.** Every opener in `TEMPLATE_MATH_RE` was
  two characters, and measured over `probes._SSTI_TEMPLATES`:
  `{{41234+5678}}` matched, `${41234+5678}` matched, `${{41234+5678}}`
  matched, while **`<%= 41234+5678 %>` (erb/ejs) and `{41234+5678}`
  (smarty) matched nothing**. That pattern is the only route into
  `verify_template_eval` - an exchange whose request it does not match is
  `continue`d past before anything looks at the response - so against a
  Rails, Express or Smarty target the probe sent the payload, the engine
  computed the sum, the probe scored the hit, and both required checks
  failed: `unproven`, not even candidate. The single-brace opener is last
  in the alternation so the two-character ones still win at the same
  position, and it cannot carry a proof alone: the verifier still requires
  the PRODUCT in the response and refuses it when it equals either operand.
  A test reads the probe's real family list, so a family added on one side
  only fails the suite.
- **`Origin: null` read as the site's own origin, in two classes.** A
  sandboxed iframe, a `data:` URL and a local file all send it, and
  `urlparse("null").hostname` is `""`, so `bool(o_host) and o_host != host`
  came out False in both `verify_cors` and `verify_websocket_channel` - and
  the CORS detail said it out loud: "the reflected origin is the site's own
  - that is an allowlist working". `probe_cors` sends it deliberately; its
  docstring calls the sandboxed-iframe case "trivially exploitable" and it
  scores the hit as "null origin trusted WITH credentials". So the probe
  reported it as a headline finding and neither class could grade it. Now
  one shared `_origin_is_foreign` for both callers, because two copies of
  that test is how they came to disagree with the probe in the same way.
  The site's own origin is still an allowlist working.

Also measured, and the sweep's claims were WRONG: three of its surviving
findings said `SERIALIZED_RE` still cannot see the php-object, Json.NET and
raw-Marshal payloads. Driven against the live lab, all ten match on the real
recorded `req_text` - r2 through r11, each with its matching substring
printed. Those agents had conflated "the lab does not EXECUTE this payload"
with "the gate cannot SEE it"; the gate sees every one, and the lab
correctly answers a parser error. One fixture of my own was unfaithful in
the same measurement: a bare `+` written into a test URL is turned into a
SPACE by `req_text`'s own `unquote_plus`, so the operator vanished. The real
probe sends `%2B` and the recorded text is right; the test builds its URLs
with `urlencode` now and says why.

All of the sweep's remaining claims have since been triaged by hand. Four
were real and are fixed in the commits that follow - `probe_idor`'s body
mode, `probe_lockout`'s series floor and credential-field pattern, and the
two template families. **Six were refuted by measurement**, and the pattern
in how they were wrong is worth more than the claims were:

- `probe_xxe`: the SSRF-via-XXE payload asks for a URL, not a file, so the
  `xxe` gate correctly does not see it - and the probe's own run grades
  `proven` anyway on the file-read marker it scored. The SSRF direction is
  capped at `candidate` by a recorded decision (`cap_reason: no
  out-of-band collector the target can reach`).
- `probe_disclosure`: `/.git/HEAD` is not a credential, which is the class
  floor working as designed; the probe's run grades `proven` on `/.env`.
- `probe_smuggle` and `probe_ppoll`: both grade `proven` on their own runs.
- `probe_cache`: graded `proven` by its own row all along. My measurement
  helper did not offer the quote the class needs, which
  `tests/test_probe_matrix_agreement.py` already documents - "`ppoll` and
  `cache` both reach `proven` on `<marker>` and `unproven` on the line
  containing it".

Every one of those six was a true observation about a PAYLOAD with no
consequence for the CLASS. The sweep asked "can this payload satisfy the
gate?" when the question that decides a defect is "can the probe's own run
reach the class ceiling?" - a payload the gate cannot see only matters when
no other route in the same run carries the proof. The three
`SERIALIZED_RE` claims noted above failed the same way, in the other
direction: they read "the lab does not EXECUTE this payload" as "the gate
cannot SEE it".

### The probe could be asked for fewer attempts than its class accepts
`probe_lockout` clamped `tries` with `_ival(tries, 10, 3, 15)` while
`verify_no_throttle` needs `_LOCKOUT_FLOOR` (5) attempts before "never
refused" means anything. So an agent asking for a gentle 4 got a run the
probe reported as a finding - "no lockout or rate limit after 4 failed
attempts - online password guessing is possible" - and the class could
never grade. Measured against `/login2`, the endpoint the VULNERABLE row
drives: tries=3 and tries=4 grade `unproven` on "only N authentication
attempt(s) on one endpoint - send at least 5", tries=5 and tries=10 grade
`proven`. The lower bound is the class's constant now, imported the way
`latency_ramp` already was - that sharing happened because the probe used
to measure the same ramp with its own derived quantity, and the COUNT was
left behind when the ramp moved.

Two measurement errors of my own on the way to that, both worth recording
because each would have become a false finding:

- I first drove `probe_lockout` at `/login`, where the lab answers 200
  "Unknown user." to a bogus name, and read "10 attempts but only 0 failed"
  as a defect. `/login` is not the row's endpoint; `/login2` answers 401
  and the class grades `proven` there. The endpoint was wrong, not the
  code.
- The first version of the test asserted `_ival`'s own clamping and the
  probe's call-site string. Planting the defect back failed only the
  source-grep half: the behavioural lines tested a generic clamp and never
  reached the probe. It drives the probe and counts what was actually sent
  now, and the plant fails on "asked for 3 tries and the probe sent 3,
  below the 5 its own class needs".

### Six requests that send no password are not six failed logins
Two more in `probe_lockout`'s neighbourhood, both measured against
`/login2`, the endpoint the VULNERABLE row drives.

- **The probe claimed logins it never attempted.** `data` is the caller's
  body template and the only place a credential field comes from. With
  `data="username=x"` the probe reported "no lockout or rate limit after 6
  failed attempts - online password guessing is unthrottled" while
  `verify_no_throttle` counted ZERO authentication attempts and graded
  `unproven`: "no cited request carries a credential field". The probe
  already had this correction one branch over, for attempts that got no
  answer, with the rule written out there - "A caveat under a wrong
  headline is still a wrong headline" - and the credential-less case was
  the other way the same thing can happen. It names it now, and the
  pattern it tests with is the class's own, imported, so the probe's idea
  of a credential field cannot drift from the one that grades it.
- **`pw` was not a credential field.** It sits beside `pwd` and `pass` in
  every real login form, and this repo's own lab fixtures use it
  (`{"user": "admin", "pw": "hunter2"}`). `_is_auth_attempt` reads
  `_CREDENTIAL_FIELD_RE` and nothing else, so a target spelling its field
  that way had every attempt fall out of the series: measured,
  `user=x&pw=y` gave 0 recognised attempts out of 6 and the class could not
  grade a lockout finding at all. It stays a FIELD and not any occurrence
  of those letters - `username=pwx`, `showpw`, `a=pwned` and `pwd_hint=`
  all still fail to match.

One fixture of the existing suite was unfaithful in the same way mine was:
`_drive` hands every probe the placeholder body `q=1`, which carries no
credential field, so the dead-target test for `probe_lockout` was asserting
"after 6 failed attempts" on a run that sent no password. Its subject is a
target that answers nothing, so it passes a credential body now rather than
letting the placeholder change the subject.

### An object reference could not ride in a request body
The `verify_method_effect` shape again: the lab plants it, the probe finds
it, and no verdict could be recorded for it.

`probe_idor`'s own docstring advertises the mode - "or inside a POST body
template when `data` is given" - and the lab's header documents the
endpoint it plants: "POST /api/order  IDOR in a JSON body ({"order": N}
served)". Measured: the probe drives it correctly, four exchanges returning
`"owner": "user-5"`, `"user-6"`, `"user-4"` and `"user-0"` - plainly
another subject's data - and reports "idor candidate: neighboring object
ids return 200 with different content". The class capped at `candidate`,
missing exactly "two distinct object references on one endpoint", because
`_object_refs` read the URL only and returned `set()` for all four, and
`OBJECT_REF_RE` matched `name=value` and never JSON's `"order": 5`.

Both halves were needed and both are planted back. Widening cannot loosen
the check it feeds: `verify_differential` requires the ref sets of TWO
cited exchanges to be non-empty and different, so no single request can
carry the pair by itself. The pattern stays a FIELD matcher - `identity=`,
`"orders":`, `"total":` and `x=1` all still yield nothing.

The first version of the fix broke two long-standing tests, and they were
right: it concatenated url and body with a space, which put a trailing
space after `/api/user/1`, and the path branch ends `(?=/|$|\?)` - so `$`
no longer matched and EVERY url-mode reference disappeared. The pagination
test and the opaque-id test both dropped from `proven` to `candidate`. A
bound defeated by something the caller introduced; the two strings are
scanned separately now.

### Six classes had no clean row, and nothing said so
The clean direction of the proving table is the one that catches a FALSE
POSITIVE - its own header says it: "The same probes where the lab has no
such bug. `proven` here would be the verifier accepting something it should
refuse." It is also the direction that silently lagged. Re-deriving the
coverage per class: 28 of the 29 classes are driven against a vulnerable
endpoint (`dos` is recorded in `NOT_DRIVEN`) and only 22 against a clean
one, because `test_both_directions_are_exercised_for_the_classes_that_have_both`
pins a TEN-class minimum rather than completeness. The defects found in this
stretch were mostly false proofs, which is exactly what a missing clean row
cannot catch.

Three of the six are driven now, each measured below its ceiling before its
row was added: `idor` at `/item?id=1` (`unproven`), `upload` at
`/api/register` (`unproven`), `xfh` at `/search?q=widget` (`candidate`).
Two of those probes still report something, which is the point -
`probe_idor` says "neighboring object ids return 200 with different
content" about `/item`, where the differing content is two products and no
subject, and the class refuses it.

The other three cannot have a clean row on this lab, and the reason is
measured rather than assumed - each was found by driving the probe at a
candidate endpoint and reading why `proven` came back:

- **`cors`**: the lab reflects the request `Origin` plus
  `Access-Control-Allow-Credentials: true` on EVERY response, so no
  endpoint here has a correct allowlist.
- **`method`**: `do_TRACE` answers on every path, so every endpoint is a
  cross-site-tracing finding and none is clean.
- **`disclosure`**: `probe_disclosure` scans the ORIGIN rather than the
  path it is given (`root = f"{p.scheme}://{p.netloc}"`), and this lab
  serves `/.env` and `/.git/HEAD` at that origin.

They are in a `NO_CLEAN_ROW` map carrying those sentences, and a new test
holds the two tables to it: a class driven in the proving direction with no
clean row and no recorded reason fails the suite. Both halves are planted
back - removing the `xfh` row and removing the `cors` reason each produce
the named failure.

Worth recording that all three of those "no clean endpoint" answers first
looked like false positives in my own measurement, and each was my endpoint
choice rather than a defect. Driving a probe at an endpoint that is not
actually clean produces exactly the output a real false positive would.

### Two of those three "cannot" answers were about the lab, not the class
The section above said `cors` and `method` could not have a clean row
because the lab plants both globally - every response reflected the request
`Origin`, every path answered `TRACE`. That was true, and it was a fact
about the LAB rather than about either class, which makes it something to
fix rather than to record. Both now have a clean twin in the lab's own
`-strict` idiom, beside `/ws-strict` and `/graphql-strict`:

- **`/cors-strict`** serves the same data as `/api/data` behind an
  allowlist that works: it answers with its OWN origin whatever you send.
  `verify_cors` asks `allow == origin`, so a foreign `Origin` never
  matches. `do_OPTIONS` had to learn the same rule, or `probe_cors` reports
  "preflight reflects foreign origin WITH credentials" on the clean path and
  the row driving it means nothing.
- **`/method-strict`** refuses `TRACE` with a 405 and takes no write verb.

Measured before the rows were added: `probe_cors` against `/cors-strict`
grades `unproven` and says "no cors issue"; `probe_method` against
`/method-strict` grades `unproven` and just lists the methods. And the
vulnerable rows still grade `proven` - that is the half a clean twin can
quietly break, so it was measured in the same run. Planting each twin back
fails the clean row with the module's own sentence: "That is the verifier
accepting something it should refuse."

`NO_CLEAN_ROW` is down to one entry, and it is the one whose reason is
about the probe rather than the lab: `probe_disclosure` scans the ORIGIN
rather than the path it is given, so no path on a server that serves
`/.env` at its root can be its clean twin. Five of the six gaps closed;
`dos` remains the one class driven in neither direction, recorded in
`NOT_DRIVEN` as it already was.

### The lab and the demo can now be pointed at a separate machine
The evaluation chapter needs the target on another host. An agent attacking
127.0.0.1 and an agent attacking another machine are the same code path, and
only the second is evidence that the system works over a network - so until
this, every artifact the project could produce was a loopback one.

- `make_server` takes a `host`. The default stays `127.0.0.1`, which is what
  every test and the whole CI matrix wants: a deliberately vulnerable app
  with a command executor should not become reachable by accident. The bind
  comment enumerates what IS exposed when you opt in - `/ping` runs argv
  through `_EXEC_ALLOW` (`id`, `whoami`, `uname`, `hostname`, `pwd`, `echo`,
  and `cat` confined to a fake tree by `_within_root`), never a shell, 3s
  timeout, at most `_EXEC_MAX_SEGMENTS` commands per request.
- `argus demo --target URL` runs the same scripted sequence against a lab
  someone else started instead of spawning one. An unreachable target is an
  operator error with a message, not a traceback.

Measured against a real second machine (Ubuntu 22.04.4, Python 3.10.12, on
its own LAN address): 6 findings over 64 requests, 5 `proven`, and
`argus verify` reporting "66 chained entries verified ... 6 findings
re-validated, artifacts sealed". The `rce` excerpt is `uid=1000(lab)` - the
TARGET's identity rather than the attacker's, which a loopback run cannot
demonstrate and which is the point of the parameter.

Both halves are planted back: hardcoding the bind fails the loopback test,
and ignoring `--target` fails the demo test with the locally spawned port
beside the requested one.

### bWAPP graded `proven` on `<!DOCTYPE html>` while its UNION had failed
A residual this file recorded earlier as "narrow" and left open. It is not
narrow, and a third-party application found it within minutes of being
installed - which is the argument for testing against applications this
project did not write.

Measured against bWAPP's `sqli_1.php`, with the quote `<!DOCTYPE html>`:

```
PASS data store fingerprinted      | 5.5.9-1ubuntu in r1
PASS the query named its target    | users in r12
PASS rows returned                 | quoted from r12
GRADE: proven
```

The banner was genuine (a real MySQL version, on the same endpoint, not
echoed - so the two correlations added earlier both held). The request did
name `users`. And the only line r12 carried that the baseline did not was
*"Error: The used SELECT statements have a different number of columns"*:
the UNION had FAILED and nothing was extracted. Nothing asked whether the
quoted bytes were data or the page's own furniture, and furniture is in
every response an endpoint sends.

The fix is the control the nosqli half has required since it was split out
of this verifier: a cited exchange on the same endpoint, answered, whose
request carries no table, whose body does NOT contain the quoted bytes. The
check is named - "the rows are not what the page serves anyway" - so the
operator reads the reason rather than inferring it, and it is in
`SQLI_REQUIRED`, so `missing` names it too. The FAIL branch of "rows
returned" was also saying "returned no document shape", which is a nosqli
sentence that tells a SQL operator nothing; it now says the quoted bytes
are in a control too.

What it cost, and why that is the right trade:

- `docs/sample-session` had to be regenerated, because F01 cited only the
  500 error and the dump: a 500 is not a control (`status_of(e) < 500`),
  so the finding read as overgraded and `argus verify` said TAMPERED. The
  demo's citation now includes the BASELINE the probe already sends first,
  which is what an agent should cite anyway, and both demo paths were
  changed, not one.
- Seven existing tests cited sqli evidence with no baseline. Each grew one,
  and they are more faithful for it: `probe_sqli` sends the baseline first
  in every real run, so a fixture without it was never the shape the
  recorder writes.
- A real probe run needs nothing added: the probe's own quote-error
  exchange is already a valid control - same endpoint, no table, answered -
  which a test now records so nobody adds a redundant request for it.

Planted back two ways: `fresh = True` returns bWAPP's boilerplate to
`proven` on the real recorded transcript, and fails the unit test that
carries that transcript's shape.

### Three limitations the third-party targets exposed, in the probe this time
The `sqli` gate fixes above were about the VERDICT. Measuring the same four
targets end to end exposed three in the PROBE, each one a false negative:
the target was vulnerable, the probe's own output said so, and the class
could not be proven because the evidence never arrived in a gradeable shape.

- **The quoted bytes for an execution class were not required to BE the
  output.** Every check in `verify_command_output` is about the EXCHANGE,
  so the excerpt only had to be real bytes from some cited response. The
  best quote this system's own chooser found was `DOCTYPE` on DVWA and
  bWAPP and `127.0.0.1:` on the lab - meaningless in 3 of 3 rce cases,
  while the execution was real every time. It is the supervisor-facing
  half of the class ("the evidence must be the output of a harmless
  command such as `id`"), and a report quoting a doctype does not show it.
  New required check, "the quoted bytes are the command output"; after it,
  the three quotes are `uid=1000(lab)`, `uid=33(www-data)`,
  `uid=33(www-data)`.

  That fix caused a regression of its own and it is worth recording:
  putting the name in `required` changed which exchange `_witness` SELECTED,
  and the two-exchange rce attack (a request that sent `id` and got nothing,
  plus an unrelated debug page printing an identity line) moved from
  `unproven` to `candidate`, because the debug page now outscored the
  request. The excerpt check is a property of the CITATION rather than of
  any one exchange, so it stays in `spec.required` and is kept out of the
  tuple `_witness` scores on.

- **`probe_sqli` knew two injection contexts and bWAPP is in a third.** Its
  `title` parameter is interpolated into `WHERE title LIKE '%...%'`, where
  neither `1'` nor `1` opens a statement boundary the way the probe
  expects. A third family, `argus%'`, is tried after the first two, and the
  one that ENUMERATES wins - a family that fails at n=1 has not found a
  boundary, it has found that this is not its context. The extraction's
  prefix follows whichever family enumerated.

- **And the enumeration was being defeated by a page that merely MENTIONS a
  database.** `SQL_ERRORS` recognises an engine naming itself, which is
  what an error page does and also what bWAPP's search chrome does: it
  carries the word "SQLite". So `ORDER BY 1` scored as a failure on a
  response **byte-identical to the baseline** - measured, similarity 1.000 -
  the enumeration aborted at n=1, `out["union"]["columns"]` came back 0,
  and the extraction silently fell back to the two columns the caller
  named and built a two-column UNION against a seven-column SELECT. The
  signal is a DIFFERENCE from the baseline now, the way every other
  differential in that file already was: an error pattern that matches the
  baseline too cannot be this request's failure. With that, the
  enumeration finds 7 and the extraction returns bWAPP's `bee`/`bug`.

  The column discovery also ran only when the caller asked for it, while
  the extraction below depends on its result - so it now runs whenever an
  extraction is requested. The capability was there; it was not wired to
  the thing that needs it.

### The presentation page named three commands that do not exist

The evidence pack carries `presentation.html`, an interactive page written
for a reader outside the project. Writing it, three commands went onto the
page from memory rather than from a run: an "open" subcommand, which has
never existed; the real `check` subcommand given a class argument and a
quote argument, neither of which it takes - it checks API connectivity; and
an `argus proof sqli` transcript whose text did not match the real one. All
three are now the output of running the command.

The reason none of them was caught is the part worth keeping. The doc gate
checks that documentation names only things that exist - and its file set
was markdown-only, so an HTML page escaped every check in it, the same way
`docs/VERIFICATION.md` escaped by being the one `docs/*.md` outside the
hand-written list. A page that invents a command is precisely the defect
this gate exists for, and it was the document most likely to be read by
someone who cannot check the claim themselves.

`_html_as_doc_text` translates the page's two command-carrying shapes -
`<code>` and the terminal block - into the backticks and fenced blocks the
existing rules already read, instead of adding a second set of rules that
could drift from the first. Prose outside those two elements stays prose,
so Vietnamese text reading "argus chay o day" is not mistaken for a
subcommand claim, which is the lesson the markdown version had already
learned. The globs that derive the gated set now cover
`docs/nckh-evidence/*.md` and `*.html`, so the next file added there cannot
escape the same way.

Turning it on failed immediately on a real defect: the evidence pack shipped
a script whose name began with the probe-tool prefix, which reads as a
claim about a registered tool of that name. Renamed to
`thirdparty_probes.py`.

Each of the three defect shapes was then planted back into the page and
watched being named - the
missing subcommand, an invented one, and an unregistered probe-shaped
identifier, each reported against `presentation.html` - because a check
that has only ever been seen passing is not yet known to be a check. Two
earlier attempts to plant proved nothing: the anchor they matched on
occurred twice, the assertion stopped them, and the run they produced was
of an unmodified file.

No new check was added, so the selftest count is still 160; the existing
checks simply reach further.

### The two capped classes were capped for one missing thing

`xss` and `ssrf` were the only classes the matrix held at `candidate`
whatever the evidence said. Their cap reasons read as different problems -
"no browser ships with this package", "no out-of-band collector the target
can reach" - and they were the same problem. Each class could see half its
evidence in the bytes: a payload reflected unencoded, a response that
differed from a control. Neither could see the other half, which in both
cases is a REQUEST the payload causes when it actually runs.

`argus/collector.py` is a listener that records what reaches it. Not what
the browser says about itself: the obvious design, and the one the code's
own comment suggested, was to drive a browser and cite the nonce it
reports - but that answer reaches the gate through the probe, and a
probe's account of its own success is the thing `record_finding` refuses
for every other class. So the payload is written to DO something instead,
and the hit arrives on a socket this package owns. It is the arrangement
`id; echo <nonce>` already uses.

Four conditions, each refusing a way of proving nothing. `direction ==
"inbound"`, because without it a request argus SENT to its own collector
is an entry with a `request` key carrying the nonce, indistinguishable
from a hit RECEIVED. The same nonce in an outbound request, because a hit
nobody caused is a hit from somewhere else. The hit AFTER that request,
compared with `>`, because an equal stamp has not shown which came first -
the opposite of the conservative direction for "did these overlap", which
is a different question. And for `ssrf` only, arriving from another
machine: the one condition here that does not rest on trusting argus's own
probes, so the class that can demand it does. `xss` cannot - the browser
runs here - and says so in its own words rather than borrowing that claim.

Measured before any of it was written: two pages carrying the same nonce
in the bytes they return, one inserting the payload into the DOM and one
entity-encoding it. Driving `agent-browser` produced one callback and
zero. Reflection cannot separate those pages. End to end against the lab,
`xss` grades `proven` on a quote of the reflected payload, with the detail
naming the request and the hit.

`ceiling` is replaced by `needs_tool` for this, and the difference is the
point: a ceiling is a lid held whatever the evidence says, while a tool is
a fact about the machine that installing something changes. The verdict
now separates "`agent-browser` is not on PATH" from "it IS installed, so
this is a statement about the target" - the same grade for opposite
reasons, which used to share one sentence.

THREE OLDER DEFECTS the emptying exposed, none caused by it:

`_ceiling_reason` never read `cap_reason`. The field exists to say why a
class is held down and `argus proof <class>` printed it, while the verdict
- the string sealed into the artifact, read by someone who cannot run the
CLI - carried `requirement`: what the class would need, rather than what
this system lacks.

`decide.py` identified "a gap probing cannot close" by `ceiling` alone.
There are two ways to be in that state, and the class that genuinely never
closes is `dos`, which is refused and has no ceiling - so the ledger would
send an operator to close a gap whose whole purpose is to stay open. One
concept, two mechanisms, and the missing member looked like nothing at all
until the other mechanism emptied.

`test_every_verifier_either_orders_its_pair_or_says_why_not` detected
ordering by searching a verifier's own source for `_ordering(`. The new
verifier orders inside a helper, so the check demanded it be declared
order-free - the one answer that is simply false. The detector was fixed,
not the answer. In the other direction the same test caught
`verify_browser_execution` still listed as order-free, correct when its
second check was a hardcoded `False` and wrong once it compared timestamps.

The probe drives the browser itself now, on by default, because the
opposite default is how the class spent its life at `candidate`: the
equipment existed and nothing reached for it. An early draft of that
navigated to the bare endpoint - `_send` returns no URL to read back - so
the browser loaded `/search` with no payload on it, reported success, and
the probe concluded "reflected but did not execute" about a page it had
never visited. A confident negative is the worst shape of wrong.

Capped classes: 3 to 1, and the one left is not about equipment. 755
tests, selftest 160/160.

### Every coverage figure counted what ran; none said what came back empty

`requests_by_tool`, `endpoints`, `probes` - three tallies of what the run
DID, and nothing answering the question a reader of a report actually has,
which is what was looked for and not settled. A probe that runs and finds
nothing had no way to be reported, so it vanished, and a report could say
"six findings" about a run where fourteen other things were tried with
nobody able to say what happened to them. The data was all recorded. The
subtraction was missing.

`open_proof_gaps` is that subtraction, sealed into `summary.json` with the
rest of the coverage block and rendered as its own section.

The first run of it returned 41, and most were not gaps: a disclosure
probe fetching `/wp-config.php~` and getting a 404 has its answer. Which
exposed the real hole - every field on a ProofSpec describes what PROVES a
class and none describes what RULES IT OUT, and that is the half false
negatives come from. `ruled_out_by` is that field. It defaults to empty,
meaning "a negative settles nothing here", because a blind sqli looks
exactly like no sqli; only `disclosure` and `idor` can name one, since
both ask whether a thing is served and 401/403/404 answers that. All of
the probe's responses have to satisfy it, not any: one 404 among several
200s says the target declined one path, not that the question is closed.
41 became 3.

Turning it on found a defect in the session this package SHIPS as its
example. The demo's disclosure finding was titled `Exposed /.env and
/.git/HEAD at web root` and cited one exchange, for `/.env`. The exchange
showing `/.git/HEAD` returning 200 was never cited - a report asserting
something its own evidence did not carry, which is the defect this whole
package exists to prevent, sitting in its own sample. The proof gate did
not catch it because the gate grades the EXCERPT against cited exchanges
and the title is prose that nothing compares to the citation. The title
now claims only `/.env`, and `/.git/HEAD` appears in the gap list, which
is the true statement: the sweep touched it and nothing settled it.

Two measurement defects on the way, both mine, both overstating. A probe
walking `/api/user/1..3` against a finding naming `/api/user/2` reported
two gaps that were one endpoint already settled - fixed by reusing
`_endpoint_shape`, which collapses identifiers. And a finding settles
every endpoint it CITES, not only the one in its `url` field; counting the
name alone was what reported `/.git/HEAD` in the first place, and both
halves of that turned out to be worth knowing.

The section says three different sentences for three different states: a
class whose negative would settle it but did not, a class where no
negative ever settles it, and nothing left open at all. Collapsing those
into one line would put "we checked and it is fine" and "we checked and
cannot tell" under the same words.

762 tests, selftest 164/164.

### xss proved itself on the DOCTYPE, and the first two fixes were both wrong

Measured on DVWA the moment the class could reach `proven`:

    DVWA  xss  6  proven  '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML'

Third time for this shape. `sqli` graded `proven` on `<!DOCTYPE html>`,
`rce` on the word `DOCTYPE`, and now `xss` on a doctype with a public
identifier. The check asked whether the quoted bytes carry a raw `<` or
`"` - whether they COULD break out of their context - and never asked
whether this probe put them there. Three classes, three separately
written correlations, the same hole each time: a gate needs one shared
correlation or every new class is a fresh chance to rebuild it.

FIRST FIX, too strict. The class requirement says "executing the payload
and reporting the probe nonce", so the excerpt was made to carry a
collector nonce. It refused the doctype correctly and also refused the
canary that a browserless run legitimately reflects, which carries no
nonce at all. The shipped sample session stopped verifying: its `xss`
finding fell from `candidate` to `unproven` and `argus verify` reported
TAMPERED on this package's own example. That is how it was caught - not
by reasoning, but by a real artifact ceasing to be valid. The mistake was
conflating "the excerpt is the payload" with "the excerpt carries a
collector nonce"; the second is stricter than the claim.

SECOND FIX, still too strict. Reflection means the bytes went out and
came back, so the excerpt had to appear in the request as well as the
response. Correct in principle and wrong at the edges: a tester quoting a
reflection takes the surrounding markup with it, and demanding the whole
quote be in the request refused exactly those natural quotes. The
probe-agreement run caught it.

THIRD FIX. Some run of at least four characters, carrying a
metacharacter, has to appear in what was sent - decoded, since requests
percent-encode. A first attempt put that floor at eight and refused
`x<>'"`, five characters and three of them metacharacters, a payload by
any reading. Four does not match by accident in a request that never
carried a `<`.

Measured after, on the real targets: the payload proves, the payload with
twenty or sixty characters of surrounding page proves, the doctype does
not. A gate fix is right only when it removes the false proof WITHOUT
removing the true one, and the first two attempts each failed that second
half in a different way.

`xss` now grades `proven` on three targets, two of them third-party
applications, quoting the reflected payload whose nonce came back to the
collector. The results table goes from 7/8 to 9/10 at the class ceiling.

764 tests, selftest 160/160.

### A run refused everywhere read as a run with nothing to report

Found by reading another project's vocabulary rather than this one's code.
PentestCode (MIT, TypeScript) tracks attack vectors through
`attempted | confirmed | resolved | blocked`, and `blocked` is a state this
gate did not have. Measured here immediately: five probe requests, every
one answered 403, produced zero findings AND zero open proof gaps - so the
report said "nothing was left open" about an engagement where nothing was
tested at all.

The cause was treating two different negatives as one. 404 and 410 are
statements about the TARGET: the thing is not there. 401 and 403 are
statements about US: we were refused. On a single path the distinction is
academic, and a 403 to "is /.env served" really is the control working.
Across a whole run it is the difference between a measurement and a wall.

So a refusal settles a class only when the run shows we were not being
refused wholesale - `anything_got_through`, which asks whether anything in the
engagement came back as something other than 401/403. The same differential
this gate keeps needing: "was this path refused" and "are we being refused
everything" are different questions, and only the second is answerable by
comparison.

Gaps that were never tested now carry `blocked` and say so in their own
sentence, because "we tested and cannot tell" and "we never got to test"
read identically in a list of endpoints and mean opposite things to
whoever reads the report next.

Three scenarios pinned: refused everywhere (every endpoint an untested
gap, marked), absent everywhere (404 is an answer, settled), and a refusal
among answers (not blanket-blocked, so the 403 is the control working).

1021 tests, selftest 164/164.

### The hybrid fan-out was 1500 lines nothing could reach

`argus/orchestrator.py` runs several scanners at once and merges what they
found. It was written, tested to 67 cases, reviewed, and imported by nothing:
a repo-wide grep found it named only in its own test file. No tool entry, no
CLI path, no registry row. Everything it claimed was exercised only by tests.

`argus/tools/sweep.py` puts it on the table as
`recon_sweep(url, tools, wordlist)`, and the design question it had to answer
was where the AGENT half goes. The
orchestrator takes an injected `agent_fn` so its second pass can ask a model
for more paths; in an engagement the model IS the caller, so wiring that back
in would re-enter the agent loop from inside a tool call. So the hybrid is
realised one level up and it is the same hybrid: `recon_sweep(url)` returns
what the scanners found, the model reads the shapes and writes candidates,
and `recon_sweep(url, wordlist=...)` runs them. The generating half happens in the
model's own turn, where its reasoning is in the transcript rather than buried
in a subprocess. The reply says so rather than reporting an agent half that
did not run.

Every invocation is recorded as its own exchange, so a finding can cite the
sweep that found its endpoint and `read_response` reaches the raw output.

A MODEL-WRITTEN WORDLIST IS TARGET-INFLUENCED INPUT. It is derived from bytes
the target chose, so it is filtered like any other: 400 words, 120 characters
each, no control characters, and nothing beginning with `-`, because ffuf
reads a value starting with a dash as the next option and a word like `-oOUT`
turns a scan into a file write. What is dropped is reported, because a caller
that sent 300 words and got 40 will keep sending them otherwise.

AND THE DEFECT DRIVING IT FOUND. An out-of-scope target returned
`endpoint_count: 0` under the sentence "no endpoint came back - either
nothing is there, or the wordlist did not name it". The orchestrator had
refused correctly and spawned nothing; the refusal was sitting in each run's
`skipped` field, under a summary that contradicted it. A model reading that
widens its wordlist and retries forever instead of learning its target is out
of scope. A refusal is a decision and has to be the headline. Measured both
ways: restoring the single-branch version fails two tests.

IT WAS CALLED `sweep` FOR AN HOUR. The grant check caught it: `recon.md`
says "`probe_disclosure` for the sensitive-artifact sweep", and a tool named
after a common English word makes every prose use of that word read as a
tool reference. Third time this package has hit the shape: a doc-gate regex
reading a two-letter fragment of Vietnamese prose as a subcommand, and a
helper whose name began with the prefix of an existing tool family being
read as a tool - and the fix is the same each time: name the thing so it cannot be
confused with the language around it. `recon_sweep` also says what it
sweeps, and matches the orchestrator function it wraps.

A TOOL NO CARD GRANTS IS AS UNREACHABLE AS ONE NOTHING IMPORTS. The registry
entry alone left it uncallable in team mode; `test_every_registered_tool_is_
granted_to_some_role` said so immediately. Granted to recon, which is whose
job it is, and `recon.md` now teaches the two-pass shape rather than just
listing the name - a role that holds a tool and is not told what it is for
holds it the way the registry held the orchestrator.

### A skill card taught a cap the matrix had dropped

`argus/skills/ssrf.md` still read "the class is capped at `candidate` here on
purpose - proving it needs an out-of-band collector, and none ships with this
package" two days after the ceiling came off and `argus/collector.py` became
that collector. These cards are loaded into the model's prompt at runtime, so
this is not a stale document - it is an instruction. An agent loading it
before probing was told the class tops out at candidate by design and had no
reason to collect the one artifact `proven` now requires.

A selftest check now asserts that no module teaches a cap the matrix does not
impose, over the 24 class modules. Planted back, it fails; removed, it
passes. The scan found exactly one card wrong, which is the number that
matters: the check was written because one had already drifted, and it had.

1021 tests, selftest 164/164.

### An oracle argus cannot write

Every number this package produces about itself is this package marking its
own work. The proof gate makes that marking honest; it cannot make it
independent, because `proven` means the evidence met a requirement argus
wrote.

Some deliberately vulnerable applications keep their own score. OWASP Juice
Shop serves `GET /api/Challenges` - 118 challenges, each with a `solved`
flag the application sets from its own view of its own state. Nothing in
argus can write that flag. `argus/groundtruth.py` reads it before and after
a run and reports what the target confirmed beside what argus claimed.

IT IS DELIBERATELY NOT A TOOL. An agent that can read the scoreboard can
read the answers, and the measurement would then be of a system that was
told what to find - a different and much weaker claim. A test asserts the
module appears nowhere in `tools/registry.py`.

IT DOES NOT REDUCE TO A SCORE. Juice Shop's categories ("Injection", "XSS")
and this package's proof classes (`sqli`, `rce`, `xss`) are different
vocabularies with no exact mapping, so the correlation is labelled
approximate and the per-challenge keys are kept beside the counts. A solve
argus claimed nothing for is reported separately rather than folded in:
either the run tripped it blind or the mapping is too narrow, and both want
a human instead of a number that splits the difference.

THE READ IS DIFFERENTIAL, like everything else here that works. The
scoreboard is cumulative, so a target someone exercised yesterday would
otherwise credit this run with work it did not do.

AND IT WALKED INTO A DEFECT THIS REPO ALREADY HAD WRITTEN DOWN. The first
read raised "Unterminated string at char 11978": `GuardedClient.send` hands
back `body[:12000]` to bound what reaches a model while recording
`body[:200000]`, and the scoreboard is 69KB. `probes.recorded_body` exists
with a docstring about exactly this, and a new module reached for the
returned value anyway. The failure was loud this time; the case that is not
is a cut landing on a record boundary, which parses cleanly and yields a
SHORT list - a measurement module reporting a wrong total with no error
anywhere. It reads the recorded body now, and refuses outright if even that
was truncated, because a count taken from a cut list is not a count.

Measured against the live target: 118 challenges read in full, 1 solved
before the run, 0 newly solved, nothing credited.

### Three skill cards instructed what the repository refuses

The eight `*-refs.md` depth modules that arrived with the two-tier skill work
are returned by `load_skill` into the model's prompt, and an entry skill
routes to its refs module the moment a class is confirmed. Verified at the
runtime level before changing anything: `load_skill('ssrf-refs')` resolves to
class `ssrf` and `ssrf.md` names `ssrf-refs`, so the chain is live. These are
instructions, not documents - the same reading that made the stale `ssrf.md`
cap a defect rather than a typo.

CLAUDE.md names what this repository will not help with: "persistence,
lateral movement, credential dumping, data exfiltration, or any demonstration
whose proof is the damage", and settles the principle for execution -
`id; echo <nonce>` and it stops there. Three cards crossed it:

- `ssrf-refs.md` handed the model `…/iam/security-credentials/<role>` and
  `…/service-accounts/default/token` under "high-value first targets", a
  table of internal services to enumerate once inside, and "cite the
  recorded response body verbatim" for a credentials response.
- `sqli-refs.md` taught `INTO OUTFILE '/path/shell.php'` and
  `sp_configure 'xp_cmdshell',1` - a webshell drop, and changing the
  target's configuration so your own exploit works.
- `xss-refs.md` sent `document.cookie`, a CSRF token's value and
  `JSON.stringify(localStorage)` to the collector.

THE TEST APPLIED WAS "WHAT DOES THIS ADD TO THE PROOF", not "does this sound
dangerous". A 200 from the metadata root already establishes that the target
fetched a URL it should not have and that its IMDS is exposed; the severity of
an exposed IMDS does not depend on anyone holding the keys, so following the
credential path adds nothing to the finding and everything to the damage. An
internal port that answers differently from a closed one establishes the
request left the target's stack; `/_cat/indices` adds nothing. A privilege
that can be named from a recorded query - `secure_file_priv` empty, the role
holding superuser, `xp_cmdshell` already on - is a reportable fact; dropping
a file is persistence. A callback carrying `len=42` proves the script ran in
the victim's origin with that access; the value proves nothing further.

SO THE READ-SIDE CAPABILITY STAYED. `LOAD_FILE('/etc/passwd')` and
`pg_read_file('/etc/passwd')` are kept, for the same reason `id` is the
execution proof: world-readable, no secret in it, and its arrival through the
injection settles the question. Blanket-refusing the area would have removed
real capability, and a test now asserts those artifacts are still present.

AND THE CARD HAD ALREADY GOT ONE RIGHT. `xss-refs.md`'s HttpOnly line sent
`d.length` - the measurement, not the data - while the three beside it sent
values. The fix was not a standard imposed from outside; it was the three
lines made to match the one the author wrote correctly.

The check that holds this is mechanical and had to be rebuilt once. Its first
version read line by line and reported a refusal's own second line as an
instruction, because "DO NOT follow the credential paths -" and the paths it
names do not fit on one line. A line is the wrong window to judge a
prohibition in; the unit is the paragraph. The cookie pattern needed the same
care - `document.cookie` is fine and `document.cookie.length` is the shape
that survives, so the pattern is `\+\s*document\.cookie(?!\.)`. Plant-tested
by restoring each pre-merge file from git: ssrf-refs fails 1, xss-refs fails
2, sqli-refs fails 1, all three restored passes 20.

### The second site of a comment that claimed a protection it did not have

`argus/web/api.py` built `ScopeGuard(target)` and checked that same target,
under the comment "fail-closed: private addresses are only allowed when the
target itself is private". The target is always itself, so the sentence is
vacuous; `prompts.py` carries the same measurement for the same mistake, and
this site was found by reading that note rather than by a test.

MEASURED: `ScopeGuard.check` has five raise branches and exactly ONE is
reachable when the guard was built from the target it checks - scheme and
parse, which refuses `ftp://` and `file:///`. The host is the whole
allowlist, `exclude_paths` is empty, and `allow_private` is forced True for
a private target, so `http://169.254.169.254/latest/meta-data/`,
`http://10.0.0.1/`, `http://192.168.1.1/admin` and `http://[::1]/` all pass
with `allow_private=True`.

No test asserted otherwise, so only the comment was wrong - which is the
point. A comment that states a protection the code lacks is worse than none,
because a reader stops looking. It now says which branch is live and which
four cannot fire.

ONE CLAUSE OF IT WAS TRUE AND IS KEPT: no `extra_hosts` is accepted over
HTTP. That protection is structural rather than conditional - there is no
parameter for a scope list to arrive in, so there is no branch for it to
pass through - and scope beyond the target comes from the operator's own
invocation or not at all.

A test pins the pair: the measured behaviour, and that the construction line
carries no trailing claim. Plant-tested in both directions - restoring the
vacuous comment fails it, and handing the guard an `extra_hosts` from the
request body fails it.

THE TEST ITSELF TOOK THREE TRIES, each a different way of being wrong about
its own subject. It built the guard outside the `try`, so the constructor's
`ScopeError` for `file:///` escaped instead of being counted. It asserted
`"extra_hosts" not in source` when the word appears in the comment
explaining its absence. And it asserted the vacuous sentence was gone when
the replacement QUOTES that sentence to say what was wrong with it - the
third time in this session that a checker read a mention as an assertion,
after the doc gate read a helper name quoted in a CHANGELOG example as a
claim that such a tool is registered, and the skill-policy check read "DO
NOT follow the credential paths" as an instruction to follow them. The fix
is the same shape every time: check the claim's FORM, not the presence of
its words. Here that is a trailing comment on the construction line.

A FOURTH instance arrived while this entry was being written. The paragraph
above originally quoted that helper's name to illustrate the problem, and
the documentation gate read the quotation as a claim and failed - inside the
sentence explaining the three previous times. The gate is right to not
distinguish them: it cannot, and a reader of a document cannot always
either. Which is the argument for naming the shape rather than the string.

TWO ITEMS ON THE SAME LIST TURNED OUT NOT TO BE DEFECTS, and saying so is
part of the work. `ARGUS_WEB_ALLOW_REMOTE` is undocumented outside the
source, but the refusal that sends an operator looking names it and warns
against it - "Pass allow_remote=True (or set ARGUS_WEB_ALLOW_REMOTE=1) to
override, and do not do that on a network you share with the target" - and
an override for a safety gate is better hard to find than advertised, so
long as the gate explains itself when it fires. And the 415 reply is sent
without draining the body, but it is sent with `close=True`, which is the
correct handling and cheaper than draining: the 413 path drains because a
legitimate operator must be able to read that refusal, while 415 is the
cross-site form-POST path that was just refused. The asymmetry is
deliberate and the comment on the 413 drain already explains it.

### The oracle gets a caller, and `engagements/` gets a guarantee

`groundtruth.py` had no caller, which is the defect this session spent its
length fixing in `orchestrator.py` - so finishing it meant giving it one.
`argus groundtruth <session> --target <url>` reads the target's own
scoreboard, correlates it against the session's findings, and prints both
halves. It is a SUBCOMMAND and not a tool entry, for the reason the module
exists: an agent that can read the scoreboard can read the answers.

Three things it had to get right, and it got two of them wrong first.

WHERE THE READ IS RECORDED. Not in the session being measured - appending to
that transcript would change the evidence this command exists to check, and
the sealed bwapp session still verifies its 24 chained entries afterwards.
The first version put it in `sdir.parent`, which for a sealed session under
`docs/` meant writing runtime output into a committed directory; `git status`
showed it untracked straight away. It goes to the runtime area now, and the
path is printed, because a measurement taken off the record is one nobody
can check.

A FLAG THAT DID NOTHING. `--allow-private` was added and then measured as
inert against exactly the targets it was meant for: `ScopeGuard.__init__`
sets `allow_private = allow_private or target_private`, and the only request
this command makes goes to the target itself, so a private scoreboard host
grants itself and a public one has no private host to reach. Running it
against the lab's Juice Shop without the flag produced the same full output
as with it. A flag in `--help` that does nothing is a false statement about
the program, so it is gone - the third instance of this shape in one
session, and the first that was mine.

WHAT A MISSING `--before` MEANS. The scoreboard is cumulative, so without a
snapshot taken before the run there is nothing to difference and the command
says so in words rather than printing a zero: "no --before snapshot, so
nothing is attributed to this run". A missing input and a measured zero are
different facts.

AND `engagements/` WAS NEVER IGNORED. CLAUDE.md says "`engagements/` is
runtime output. Never commit it." Nothing enforced that: `git status` listed
it as untracked, so a single `git add -A` would have staged an engagement's
evidence, including a target's recorded response bodies. What had been
holding the instruction up was the habit of naming paths explicitly on every
commit - discipline, not a guarantee. It is in `.gitignore` now and a test
asserts it, which is what found the gap: the new command writes there, and
writing there made the absence visible.

Measured against the live target: 118 challenges read in full, 1 solved
before, 0 newly solved, nothing attributed. Plant-tested in three
directions - un-ignoring the runtime directory, restoring the inert flag,
and putting the oracle on the tool table each fail one test.

### The oracle confirmed a real exploit, and then showed its own hole

The scoreboard reader had never seen a challenge actually flip - every run
of it so far read 118 published, 1 solved, 0 newly solved. That is a
plumbing test, not a validation, so the exploit was driven directly: argus's
own `GuardedClient` against the lab's Juice Shop, no model in the loop,
because the probes are deterministic and the baselines are still waiting on
a key.

`POST /rest/user/login` with a wrong password returned 401 and 26 bytes.
The same endpoint with `{"email": "' OR true--"}` returned 200, 784 bytes
and a token for `admin@juice-sh.op`. The token was not used for anything:
the proof is the authentication bypass and the witness is the target's own
record, which is where this stops - the same shape as `id; echo <nonce>`.

The board then moved on its own: solved 1 -> 2, `newly_solved` naming
exactly `loginAdminChallenge` [Injection, difficulty 2], and `correlate`
reporting it CONFIRMED against a `proven` `sqli` claim. That is the first
independent confirmation in this repository of anything argus produced -
independent because no part of argus can write that flag.

AND THE SAME EXPERIMENT FOUND THE HOLE. Run against the same two snapshots
with five claims instead of one - sqli, xss, rce, idor, ssrf - the output
was identical: `confirmed=['loginAdminChallenge']`, nothing to separate a
run that claimed the right class from one that claimed everything. Breadth
was free, in the one instrument that exists to be independent.

The missing piece was the third quadrant. Target solved and argus claimed is
`confirmed`; target solved and argus silent is `unclaimed`; a claim the board
does not corroborate had nowhere to go at all. It is reported now, and the
shotgun claim reads `uncorroborated_classes: [idor, lfi, ssrf, xss]` against
`[]` for the focused one.

THE CORROBORATION COUNT IS AN UPPER BOUND AND SAYS SO IN ITS NAME. One
category maps to several classes, so `loginAdminChallenge` corroborates any
of sqli/nosqli/rce/ssti/xxe that was claimed - measured at 2/2 for a
`sqli`+`rce` claim off a single SQLi login bypass. Hiding that would make a
generous number look like a precision score, so the field is
`claims_corroborated_upper_bound`, a test refuses the unqualified name, and
`newly_solved_matched` carries the count that IS exact, because a challenge
is a challenge.

AND AN UNCORROBORATED CLAIM IS NOT CALLED A FALSE POSITIVE. The board covers
only this application's own challenges, so a real finding outside that set is
uncorroborated rather than wrong, and a class whose challenges were already
solved before the run cannot be corroborated at all. A test asserts the
caveat says so and that the words "wrong" and "invalid" stay out of it.

Three classes in the same Injection group were left alone on purpose, and
their own names say why: "User Credentials", "NoSQL Exfiltration", "NoSQL
DoS". CLAUDE.md refuses all three.

### The gate and the oracle disagreed, and the gate was right

The experiment the whole design points at: when the proof gate says
`proven`, does the target agree - and when it says less, was it right to?

`jim@juice-sh.op'--` on `/rest/user/login` against the lab's Juice Shop:
401 for the control, 200 for the payload. The board flipped
`loginJimChallenge`. The gate graded the class **`candidate`**.

A disagreement between the instrument and independent ground truth, and the
first instinct - that the gate is too strict - was wrong. The sqli
requirement is "the DBMS fingerprint plus at least one row from a named
table, bounded to what proves the read", and the three failing checks named
themselves: no engine named, no cited request carrying SQL that names a
table, and the rows never quoted from an exchange that named one. The gate's
own detail said it in one line: **"a boolean differential proves the
channel, not the read"**. An authentication bypass proves the channel and
reads no rows, so `candidate` is the correct grade for what was actually
done, and Juice Shop's challenge is "log in as Jim", which is a different
claim. Two instruments measuring different things, agreeing about the world.

That the gate could be resolved in one step rather than argued about is
worth noting on its own: the failing checks carried their reasons, so the
question "is this a false negative" had an answer in the output.

AND IT EXPOSED THE FOURTH BUCKET. With only `proven` counted as a claim,
that pair came out `unclaimed` - "the target solved a challenge argus
claimed nothing for". A report quoting that number would say the oracle
found a bug argus missed. argus found it, graded it `candidate`, and named
the three checks it was short of. A withheld grade is a DIFFERENT FACT from
silence, and conflating them scores the gate's deliberate strictness as a
miss, which is the opposite of what an independent oracle is for.

`withheld_but_corroborated` reports it now: agreement at the channel level,
with the gate holding `proven` back on a stated shortfall. The three cases
are distinguishable - a proven claim confirms, a candidate claim is
corroborated-but-withheld, silence is unclaimed - and a proven claim
outranks a candidate one for the same challenge so nothing is counted twice.

THE SUMMARY LINE NEEDED THE SAME CARE. It read "challenges matched: 0/2"
while two challenges were corroborated at `candidate`, so a reader saw no
agreement where there was agreement the gate had deliberately not called
proof. It is labelled by which claim was matched now: 0/2 proven, 2/2
withheld.

### The oracle found a false negative in the gate, on a real engine

Pushing the SQLi class to `proven` against the lab's Juice Shop - the
supervisor's criterion, and a deliberate test of whether the gate can be
satisfied at all by evidence this repository is willing to collect - stopped
on one check and stayed there through two attempts.

The injection point is real: `q='))--` on `/rest/products/search` returns the
whole product table, `q='))` returns `SQLITE_ERROR: near ")": syntax error`,
and the engine names itself in that error unprompted. A UNION read of ONE
row from `sqlite_master` - the schema of `Products`, bounded with `LIMIT 1`,
no credentials and no user table - passed six of seven checks. The seventh,
"data store fingerprinted", could not pass.

`DBMS_RE` had `sqlite3?\.\w*error`, which catches the Python driver's
`sqlite3.OperationalError`. Nothing caught `SQLITE_ERROR` - the node/C
driver form, and what this target returns. Meanwhile the one SQLite token
that WAS recognised, `sqlite_master`, is one the attacker's own payload
almost always carries, and the echo guard correctly vetoes it as a
reflection. So on a real SQLite target an error-channel fingerprint was
unreachable: the recognised token was always a reflection and the unreflected
token was unrecognised. A false negative, found by independent ground truth,
which is what the oracle is for.

With the form added, the same evidence grades `proven`, all seven checks.

AND THE GATE TAUGHT THE PROOF SHAPE ALONG THE WAY, in two steps that were
each a real requirement rather than an obstacle. First it refused a
fingerprint from one request paired with rows from another - it wants both
in the same witness, so a banner cannot be borrowed from a different
exchange. Then it refused the read without a control: "a request to the same
endpoint WITHOUT a table in it is what separates a read from the page's own
furniture". Both are right, and the second caught the first unit-test
fixture, which had the error and the read but no benign control.

A NEAR MISS WORTH RECORDING. The 10-column UNION returned a 500 of 1991
bytes against 1078 for the others, which read as a measurable differential -
and it was the error page echoing a longer payload in its own title, with
"sqlite" and "UNION" in it because they were in the URL. Reading that as
evidence of the engine is exactly what the echo guard exists to stop, and it
was nearly done by hand. The real column count came from the engine instead:
`SQLITE_ERROR: SELECTs to the left and right of UNION do not have the same
number of result columns` for 6 through 9, data at 10.

THE FIX'S OWN LOOKAHEAD WAS INERT. It was written as
`\bsqlite_(?!master\b|version\b)[a-z]+\b` to keep the attacker-carried
tokens out, and both are matched by their own alternatives earlier in the
pattern, so the alternation takes those first and the lookahead never
decides anything. Measured by deleting it: 241 tests, no change. The echo
guard is what protects, and the ordering is what lets it. Dead complexity
implying a protection it does not provide is the same defect as a comment
that claims one, so it is gone - the fourth instance of that shape in this
session, and the second that was mine.

THE BOARD DID NOT FLIP for `dbSchemaChallenge`, and that is the right
outcome to leave alone: Juice Shop wants the whole schema, the gate rewards
"extraction stayed minimal", and one row is what proof needs. Taking more in
order to satisfy a scoreboard would be optimising for the scoreboard. So the
two instruments now disagree in both directions, and each disagreement was
informative: the board flipped where the gate said `candidate` because a
bypass proves the channel and not the read, and the gate says `proven` where
the board wants more taken than proof requires.

### Was the fingerprint gap systematic? Three shapes, and only one was missing

The SQLite false negative raised the obvious question, so the rest of the
list was audited rather than assumed. A web application leaks a store error
in one of three shapes:

| shape | example | matches | and that is right because |
|---|---|---|---|
| Python driver | `sqlite3.OperationalError: no such table: x` | yes | it names the engine |
| node/C driver | `SQLITE_ERROR: no such table: x` | yes, now | it names the engine |
| bare message | `no such table: x` | no | it names NO engine |

The bare form must NOT match, and that is the half of the audit worth
stating. "no such table", "incomplete input" and "unrecognized token" are
things several engines say, so matching them would let one store's message
be reported as a fingerprint for another - and "data store fingerprinted"
exists to say WHICH store answered. A test plants those three strings into
the pattern and fails, so the next person cannot add them as a kindness.

The six messages in that test are GENERATED by running real statements
against an in-memory database in the test process, so it cannot drift from
what the driver emits. The fix was exactly one shape; the other two were
already correct, one covered and one correctly excluded.

NOT MEASURED, AND SAID SO IN THE TEST: the MySQL and PostgreSQL forms. The
lab's MySQL targets answer 302 to an unauthenticated request, and neither
driver is installed because this package is standard library only. Those
alternatives in `DBMS_RE` are unverified by this audit rather than confirmed
by it.

### The MySQL side was measurable after all, and the harness was the obstacle

The fingerprint audit recorded the MySQL forms as unverified because bWAPP
and DVWA both answered 302 to every request. That was true of the harness,
not of the targets.

The differential settled it in one request: `login=bee&password=bug` on
bWAPP returns 302 to portal.php, while a wrong password returns 200 and the
login page again. Authentication plainly worked - so the 302s afterwards were
not an authorisation failure, they were the session being lost between
requests.

`GuardedClient` keeps a cookie jar, and a `Cookie` header passed in `headers`
REPLACES it. Reading Set-Cookie from the successful login and sending it back
by hand - the obvious thing, and what was done five times - loses the
session. The same sequence with no Cookie header at all reached portal.php
(200) and the SQLi endpoint behind it.

The schema had always said "Session cookies are kept by the client". What it
did not say is the consequence, which is the operationally important half: a
target that looks unreachable right after a login that returned its success
redirect is this, not the target. A model would reach exactly that false
negative. The tool description and the `headers` parameter now say not to set
Cookie and why, and a test drives a local server to pin all three facts -
nothing sent on the first request, the jar's cookie on the second, and an
explicit header replacing it on the third.

SO THE MEASUREMENT CLOSED. bWAPP and DVWA both return "You have an error in
your SQL syntax; check the manual that corresponds to your MySQL server
version" on a quote, `DBMS_RE` matches it, and the class reaches `proven` on
bWAPP from one row of `information_schema.tables` - metadata, not
credentials, and `LIMIT 1`. The sqli class is now proven on two engines
against two independently written applications, with evidence this
repository is willing to collect.

The test docstring is corrected rather than left alone: "unverified" and
"verified" are different claims and the file must not keep the stale one.
PostgreSQL stays unverified and says so - no PostgreSQL target is in this lab
and the driver is not installed, since this package is standard library only.

### The callback nobody was producing

`ssrf`'s ceiling came off and `argus/collector.py` was written to be the
out-of-band witness, and the wiring between them was never done.
`routable_host()` - the function whose whole job is to pick an address a
callback can come back to - had **no caller anywhere**, which `collector.py`
stated in its own docstring. So the class was freed and unreachable at the
same time, and freeing a cap is only real if the class can then be proven.
Third orphan of this session, after the orchestrator and the oracle.

THE MECHANISM WAS NEVER THE HARD PART. Measured before writing anything:
bound to the address `routable_host` returns for the lab host, that host
fetched a nonce URL and the hit was recorded with `peer=192.168.223.221` and
`witness_is_remote` true. The network path works; nothing drove it.

AND `routable_host` FAILED SILENTLY IN THE SHAPE THAT HIDES. Passing the
natural thing - a target URL, which is what this package holds everywhere -
made `sock.connect(("http://192.168.223.221:8080", 9))` raise, and the old
fallback answered `127.0.0.1`. The callback URL then pointed at the TARGET's
own loopback, nothing arrived, and zero hits reads as "the target did not
call back": a refusal that reads as an empty result, in the measurement
plumbing itself. It takes a URL, a `host:port` or a bare host now, and it
RAISES when a non-local target has no non-loopback route - a plumbing
failure must not be reported as a clean negative.

`probe_ssrf_oob(url, param)` is the caller, and tool 58. It starts the
collector on a routable address, injects a nonce URL, waits, and records
every hit as a transcript exchange with its peer - so a finding can cite the
injected request and the callback together, which is what the gate pairs by
nonce. `probe_ssrf` keeps its job: it diffs bodies, establishes the channel
and reaches `candidate`; this produces the artifact that settles it.

NO CALLBACK NAMES WHICH HALF FAILED. "The target did not fetch" and "the
collector was unreachable" are different facts and only one is about the
target, so the note states the collector address that WAS reached. Measured
against bWAPP's `rlfi.php`: status 200, no callback in 4s, collector
reachable at the LAN address - PHP's `allow_url_include` is off, which is a
fact about the target. Measured the other way against a fixture that does
fetch: one callback, recorded, peer and remoteness reported.

The host comes from `url`, not from a context field - the first version
reached for `ctx.target`, which `Context` does not have and which would
have raised on the first call. Plant-tested four ways: restoring the silent
loopback fallback, dropping URL parsing, not recording the callback, and
blurring the two halves of the no-callback note each fail.

`ssrf.md` names the new probe, since a card that says the artifact is
"yours to collect" was accurate only while no tool collected it.

AND THE SAME THREE-WAY MISS AS LAST TIME, caught by the same three gates.
Adding the tool to the registry left it ungranted to any role, unattributed
in the decision ledger, and named by a skill card no role could satisfy -
exactly what happened when `recon_sweep` went in earlier in this session.
The ledger one matters most: a probe in neither `PROBE_CLASS` nor
`UNATTRIBUTED_PROBES` is invisible to it, so the class reads as never tried
however often the probe runs, and this is the call that produces the
artifact `proven` needs. Attributed to `ssrf`, granted to exploit.

### An audit for orphans, and the other half of the orchestrator

Three components in this session turned out to be complete, tested and
reached by nothing, so the question was asked properly: which public
function in this package does nobody call?

The first pass over-reported badly - thirty-odd names, almost all of them
`verify_*` functions that the proof matrix calls through a table in their
own file, which the audit was excluding as "the owning module". That is the
same mistake a coverage audit here made before: the UNREACHABLE verdicts are
an audit's unreliable half. Counting same-module use, including dispatch
tables, the real answer was TWO out of several hundred.

**The orchestrator's fan-out entry point** - its other half. One result
per endpoint, all endpoints worked concurrently, each in its own directory
because sqlmap keys session files by host and two endpoints on one host
would corrupt each other's state. Written, tested, called by nothing.
`fanout_sweep` is tool 59 and the caller - named outside the
`exploit_` prefix on purpose, because registering an `exploit_*` tool made
the doc gate read three legitimate identifiers as tools: a transcript event
kind, a parameter of `run_exploit`, and the orchestrator function itself.
Third time in this session that the fix for a checker confusing things was
to name the thing so it cannot be confused with the language around it. Measured on the lab with a
deliberately mixed list: four submitted, one refused as not a URL with the
reason, one out-of-scope endpoint refused by the guard before any process
existed, nine tool runs completed across the three in scope.

Two things it got wrong first. `scope_refused` listed the same endpoint
three times - once per tool, because the guard refuses before each one -
which reads as three problems; it is one entry per endpoint now. And the
`target` argument was reached for as `ctx.scope.target`, which `ScopeGuard`
does not have: a `hasattr` dance implying it might would be a sentence that
gets believed, and the orchestrator's own docstring says that argument is
context for the agent prompt and is never dialled, so the first endpoint is
passed plainly.

The cap is 24 endpoints per call, not the orchestrator's 500, because a
MODEL picks this list - and the cap is reported, since a caller who sent 80
and got 24 would keep sending 80.

**`schemas_for`** - "tool schemas restricted to a name set (a role card)",
in `registry.py`, called by nothing at all while `loop.py` wrote the same
filter out inline. Two expressions of one concept, where a change to how a
role gets its surface would have had to find both. `loop.py` calls it now.

AND THE THREE STEPS PAST THE REGISTRY ENTRY WERE DONE IN THE SAME EDIT this
time - grant, ledger, card - after being missed twice earlier in this
session. The ledger needed no change and the reason is in `decide.py`
already: the attribution partition only reaches tools named `probe_*`,
because mapping `fingerprint` to a class would make reading a banner count
as probing, and a fan-out is the same case. `exploit.md` teaches it as step
3, for several leads on one host, with "for one, probe it" - a tool that
earns its cost on a list and not on a single URL.

A test that could never run was replaced rather than left. The cap test
began as `pytest.skip("list parsing is inline")`, which is a test that
passes forever on nothing; it stubs the orchestrator and asserts on what the
list became.

### All three freed classes verified reachable, and the last one was blocked
### by the same root cause twice

Three proof classes had their ceilings removed. Removing a ceiling is not
the work - the work is showing the class can reach the top grade on a real
target - so each was taken end to end.

| class | proven on |
|---|---|
| `sqli` | SQLite via Juice Shop, AND MySQL via bWAPP |
| `ssrf` | mechanism measured: the lab host fetched a nonce URL, `peer=192.168.223.221`, `witness_is_remote` true; `probe_ssrf_oob` wired |
| `xss` | bWAPP, a real browser executing two of three payload shapes |

`xss` needed `agent-browser`, which is deliberately external like sqlmap and
nuclei. It is 320KB unpacked and a Playwright browser cache was already
present, so it went into an isolated directory with npm's install scripts
suppressed and `AGENT_BROWSER_BIN` pointed at it - no global install,
nothing persistent. (That sentence named the npm flag at first and the
documentation gate refused it, correctly: it checks that every flag the docs
name is one an argus parser accepts, and a flag belonging to another program
is indistinguishable from an invented one. Seventh instance this session of
a checker reading a mention as a claim, and the seventh time the fix was to
write the shape instead of the token.)
The verdict's two reasons were checked first and both are right: with the
tool absent it says "`npm i -g agent-browser` ... without it a reflected
payload can be shown to reflect but not to execute", and with it present
"drive it at the reflecting URL ... if it still does not call back, the
payload did not execute". Same grade, two different facts, which is what
`needs_tool` replaced a hardcoded ceiling for.

AND THEN IT STILL REPORTED `executed: False`. Three payload shapes, all
three navigated, zero callbacks - on a page whose reflection was confirmed
with `< > " ' &` all unescaped.

`_prove_execution` hands the probe's session to the browser, and read it
from `ctx.client._default_headers`, which is `{}` after a login because
`GuardedClient` keeps cookies in the httpx client it wraps. The transfer
never fired. The browser visited bWAPP's authenticated XSS page with no
session, landed on the login screen, nothing reflected, nothing executed -
and the result read as the payload not running.

That is exactly the false negative the comment directly above that code was
written to prevent: "driving it at an authenticated page without one lands
on a login screen, nothing executes, and the result reads as 'the payload
did not run' when the browser never saw the page". The code knew the hazard
and reached for the session in the wrong place.

SECOND SITE OF ONE ROOT CAUSE. The first was manual: probing bWAPP by hand,
a Cookie header was set from Set-Cookie and REPLACED the jar, which read as
"target unreachable" through five attempts. Both halves of that fact matter
and only one was documented - that the client holds a jar is written down;
that `_default_headers` does not hold it was not. `_client_cookie_header`
reads the jar now, tolerates a renamed internal rather than raising (an
attribute name is not a contract), and keeps the old path as a fallback
instead of deleting it.

Measured after: `cookies_set: 2`, two shapes executed and called back, and
the gate graded `xss` **proven** on all four checks. Plant-tested three
ways - restoring the `_default_headers`-only read, removing the tolerance,
and deleting the fallback each fail.

### The one class that needs an external tool now says so where operators read

`xss` is the only proof class whose requirement names an external tool, and
`docs/USAGE.md` did not mention `agent-browser` anywhere. The runtime verdict
says it - with both of its two reasons - but an operator planning an
engagement finds out by failing to prove a class. The *External tools*
section covers it now: why execution cannot be read off the bytes, the two
install shapes including the one that does not touch the global prefix, and
the measured result on bWAPP.

AND THE DOC GATE REFUSED THE INSTALL LINE, twice, which is the eighth and
ninth instance of one shape this session: it checks that every flag the docs
name is one an argus parser accepts, and npm's flags are indistinguishable
from invented ones without knowing whose they are.

The gate already had the right mechanism and was missing a member. It
decides PER LINE and skips a line that mentions another program - the set is
`_ALLOWED_TOOLS` plus `docker` and `pip `. `npm` joins that line-level list.

It does NOT join `_ALLOWED_TOOLS`, and the difference is the point:
`_ALLOWED_TOOLS` is what `run_external` may invoke, so putting `npm` or
`agent-browser` there would hand the model a new subprocess - a capability
change dressed as a documentation fix. `agent-browser` is driven by
`argus/tools/browser.py` with a fixed argument shape, not by `run_external`,
and that stays true.

Plant-tested that the exemption is scoped and not blind: an invented argus
flag on an ordinary line still fails the check, and an unknown flag on the
npm line is excused - which is the line-level rule working rather than a
hole.

### The audit that found nothing, turned into the check that would

Three times this session a class was freed or a component completed while
nothing could reach it, so the question was asked of the whole matrix: is
every PROOF CLASS reachable by something?

The existing partition asks the opposite - "is every registered `probe_*`
tool attributed to a class" - and its own comment says why that direction is
the safe one: it "cannot fail by neglect". The direction that can is a class
with no way to try it, and nothing checked that.

AUDITED: 29 classes, 27 with a probe attributed, and the two without are
both correct. `dos` has no required checks at all, which is how a
refused-by-construction class looks. `jwt` is deliberately absent from
`PROBE_CLASS` - `jwt_decode` and `jwt_forge` SEND NOTHING, so attributing
them would mark the class tried on an offline call, the same reason
`fingerprint` is excluded - and `CLASS_TOOL_CHAIN` covers it instead, naming
decode, forge, then the request that carries the forgery. The comment there
records that the ledger used to answer `http_request` alone, which is the
last step of the chain with no hint that the first two exist.

So the audit came back CLEAN, and saying that plainly is part of the result:
there was no defect to fix anywhere else in the matrix, and manufacturing
one to have something to report would be worse than nothing. (That sentence
first gave the count of the remaining classes, and the count gate read it as
a claim about the total - tenth instance this session of a checker reading a
mention as an assertion, and the gate is right to be literal: a number
beside the word is a claim about the number, whichever subset the writer
meant.)

What it produced instead is the invariant. A class must have one of three
things - a probe in `PROBE_CLASS`, an entry in `CLASS_TOOL_CHAIN`, or no
required checks - so the next class added without any of them fails loudly
rather than sitting unreachable. A second check holds that a chain names
only registered tools, because a chain naming a removed tool recommends a
call that cannot be made, which is the same defect as a document naming a
command that does not exist.

Plant-tested three ways: emptying the chain table, pointing a chain at a
tool that does not exist, and removing a probe's attribution each fail.

The ledger itself was measured on real transcripts from this session's
probing rather than a fixture, after the fixture turned out to be the wrong
instrument - `next_action` reads the session DIRECTORY, so in-memory
exchanges produced "the transcript holds no request/response pair yet" for
both the empty and the full case. On the real directories it answers
specifically: login.php "carries 4 named input(s) ... and no probe has
tested any class against it", and products/search "has been probed, but not
for xss".

### The other direction of the documentation gate, and what it found first

The documentation gate's whole claim is that these documents name only
things that exist. That direction cannot fail by neglect - it fires when
somebody writes a command that is not there. The direction that CAN is a
thing that exists and is documented nowhere, and nothing checked it.

Applied to the two user-facing surfaces: every tool appeared in a gated
document. One of the 18 subcommands did not - **`argus web`**, the console
that binds a port, starts scans with no authentication, and renders bytes a
target chose. Its refusal explains the bind guard when it fires, and nothing
told an operator the command existed at all. The riskiest surface was the
undocumented one, which is the argument for checking this direction rather
than trusting that anything worth documenting got documented.

`docs/USAGE.md` covers it now, from the real `--help` rather than from
memory: the loopback default and why it should stay, `--bind` with the
override that the refusal itself names, the two modes and the interlock that
re-locks when the target is edited after confirmation, and the sandbox CSP
the evidence-rendered report is served under.

The check is `real - named`, reusing the extraction the forward direction
already does - three patterns including fenced blocks - rather than a second
regex of its own. Two directions that disagreed about what "named" means
would be two concepts wearing one name, which is a shape this repository has
been bitten by. It also matters here specifically: "web" occurs in four
gated documents as an ordinary English word, so a bare substring search
would have called it documented.

Plant-tested in both directions, and each catches a different thing:
deleting the new section fails "every subcommand is documented", while
adding an invented subcommand to a code block fails "docs name only real
subcommands".

(This paragraph named that invented subcommand at first, and the forward
check failed on the sentence describing the plant - eleventh instance this
session of a checker reading a mention as a claim, and the first where the
mention was of a deliberately invented name. The conclusion drawn in the
moment was also wrong: the gate's failure looked like a plant that had not
been restored, and the plant had been restored. The gate was reading this
file.)

### Two more reverse directions: one real gap, one audit that over-reported

The same question applied to the two remaining one-way checks.

**Every flag is documented.** Every other flag in this tree already was, so
the norm is the project's rather than one imposed here - and the first thing
the check found was `--app` on `argus groundtruth`, added in the same session
and written up nowhere. Documented, and the check holds it: a flag a parser
accepts and no gated document names now fails. `--help` and `--version` are
exempt because argparse supplies them.

**Every gradeable class is taught by some card** - and this audit
over-reported before it was right, the second time in this session that an
audit's negative verdicts were its unreliable half.

Asking only whether a card's STEM resolves to the class flagged six. Five of
them are taught by a card with a different name, which `load_skill` already
knows: `_also_taught` derives the extra classes from the driving tools a
module names, through the same tool-to-class mapping the ledger uses for
evidence attribution. `auth-enum` teaches `enum`, `auth-session` teaches
`lockout`, `jwt` and `massassign`, and `triage` teaches `method` - and that
function's own docstring names those five, because it was written for
exactly this gap on the runtime side.

Counting the way the runtime counts, only `dos` has no card, and `dos` has
no required checks either, which is how a refused-by-construction class
looks. So the real answer is no gap, and the result is the invariant: a
class added with no card at all, by name or by driving tool, fails instead
of handing an agent a requirement with no methodology behind it. The five
that depend on `_also_taught` are also asserted BY NAME, so the mechanism
cannot quietly stop working and leave the check green - planted by making
that function return nothing, which fails.

Two audits, one real finding, and the finding was mine from earlier the same
day. That is the argument for the reverse direction rather than for trusting
whoever added the thing.

### The count gate was not reading the document about checking

Two documents state counts that no count check covered, and one of them was
`docs/VERIFICATION.md` - the file that tells a reader how to verify this
system. Its selftest figure was three short and its pytest figure was
nearly three hundred short, and both had been wrong for long enough that
nothing noticed.

(The numbers are described rather than quoted, and that is forced. A
CHANGELOG's job is to record what was wrong, which means naming wrong
values; the gate's job is to catch wrong values; and widening the gate's
denominator in this very entry made it read this entry. Twelfth instance
this session of a checker reading a mention as a claim, and the only one
where the two jobs are genuinely in tension rather than one of them being
careless. A regex cannot tell a quotation from a claim, so the quotation
goes.)

TWO INDEPENDENT REASONS IT ESCAPED, and they are different in kind.

The selftest-count check built its own text from a hardcoded five files -
CHANGELOG, README, AGENTS, USAGE, ARCHITECTURE - while every other count
check uses the whole gated set. A check whose denominator is narrower than
the set of documents that state the thing hides whatever it never covered,
and the file it was not covering is the one about checking. It reads every
gated markdown document now, the same denominator as its neighbours.

And both patterns were keyed to ONE phrasing. The prose form is "164 offline
checks"; VERIFICATION.md writes a shell comment, `selftest.py  # 164 offline
end-to-end checks`, where words sit between the number and the noun and the
number follows the command. Both forms are matched now - and both are still
keyed to the COMMAND, which is what keeps the CHANGELOG's historical counts
out: narrative like "633 tests" has no command in front of it.

Plant-tested by restoring each stale number: 161 fails the selftest count
with "docs state [161, 164]", and 762 fails the pytest count. Measured, not
assumed - the numbers were corrected first and then the old ones put back to
watch them be named.

`docs/EXPERIMENTS.md` was outside that narrow list too, and its tool count
was right - because the TOOL count check already uses the wide set and
caught it when the number moved earlier in this session. Two checks, two
denominators, one of them silently smaller.

### The one skipped test, and why it was skipped

Every run reported one skip and nothing said what it was. It turned out to
be `test_a_capped_class_still_reaches_candidate_on_real_evidence`,
parametrised over the classes capped for want of EQUIPMENT - and that set is
empty, because every one of them has been freed. pytest then skips with its
own wording, "got empty parameter set", which says nothing about why.

The surrounding design is sound and was left alone: `CANNOT_BE_PROVEN_HERE`
holds one entry, `dos`, with the reason that the proof of a denial of
service is the denial; the test above it holds that every class either has a
test asserting `proven` or is in that list with a declared reason AND a spec
that caps or refuses it; and `dos` is excluded from the parametrised test
because a class refused by construction has no candidate floor to hold.

Two things changed. The skip says why IN THIS REPOSITORY'S WORDS now, since
a refusal here always says why - an explicit single parameter carrying the
reason, rather than an empty set and pytest's generic message. And the empty
state is CLAIMED rather than inferred from a skip: a new test asserts no
class carries a ceiling and that the list holds only the
refused-by-construction entry, so a cap returning is a failure somebody
reads instead of a skip count going from one to zero.

That second part matters because the skip was load-bearing in the wrong
direction: a reader seeing "1 skipped" forever learns nothing, while a
reader seeing it drop to zero learns nothing either. Plant-tested both ways
- restoring a ceiling on `xss` fails six tests, and adding an entry to the
list with a reason that is not about evidence fails two AND removes the
skip, because the parametrised test wakes up.

### The hybrid's agent half gets its caller

`argus/orchestrator.py` runs the scanners and ALSO takes an injected
`agent_fn(prompt) -> text`, starts it CONCURRENTLY with the tools still
running, and turns its words into a second ffuf pass. That half was complete,
tested to twelve cases - overlap, a hung agent, a raising agent, scope
checking every word, capping, a daemon thread - and it had no caller. Both
adapters passed `agent_fn=None`, so the tool half always ran alone. Fourth
orphan this session, and the one that was costing the most: the tool half is
bounded by the wordlist it was given.

MEASURED on the lab, one ffuf run against OWASP Juice Shop. Tools alone: 6
endpoints. Tools plus an agent half supplying five words: 10 - `/api-docs`,
`/api-docs/`, `/ftp` and `/rest` added, nothing lost. It is additive by
construction, because the agent contributes a wordlist and a wordlist can
only find more paths. The fan-out measured the same way: three endpoints,
three calls, three distinct thread ids starting within 0.53s of each other,
the whole thing finishing in 37.9s rather than three times that.

A new module beside the two adapters is the caller, and every line of care
in it answers a hazard that was read out of the code it has to live beside
(its name is not spelled here: the doc gate reads an identifier in that
shape as a claim that a tool by that name is registered, and this is a
module, not a tool - thirteenth instance this session of a checker reading a
mention as a claim):

- **Its own client, built on the CALLER's thread.** `resolve_auth` writes a
  temp file named only by PID and `os.replace()`s the operator's real
  credentials file, so two concurrent refreshes collide on one path. The
  credential is resolved once, before any worker thread exists.
- **Its own token counters.** The clients count with `self.input_tokens +=`,
  a non-atomic read-modify-write; sharing the agent loop's client across
  threads corrupts the run's cost line, and a private client instead makes
  the spend invisible because nothing aggregates a second client's counters.
  So it keeps its own under a lock and hands them back for the tool result,
  named with the model that was actually billed - folding them into the
  loop's totals would price them at `cfg.model`'s rate, and the report's
  claim is that every figure traces to a line someone can check.
- **One attempt.** The orchestrator abandons the agent thread after as
  little as five seconds because a Python thread cannot be killed, and five
  attempts carry 2+4+8+16+32 = 62 seconds of `time.sleep` regardless of the
  timeout - so the abandoned call would keep retrying and keep SPENDING
  after its result has nowhere to go. `max_attempts` is now a constructor
  argument on both providers, defaulting to the old five so no existing
  caller changes.
- **Its errors carry no provider bytes.** The adapters embed up to 500 bytes
  of a provider's response body in `LLMError`, that message reaches the
  sweep's note and the session artifacts, and the redaction only replaces
  operator-declared secrets. Only the exception TYPE leaves the module -
  plant-tested with `401 {...'key':'sk-ant-LEAKED123'}`, which does not
  appear in the stats.
- **The model comes from the table by role.** `breadth` is the table's own
  name for cheap wide work, which is what generating path candidates is.
  `for_role` returns a Model, not a name: the first version did
  `str(picked or "")`, which is the dataclass repr - a name the table would
  not find, routed to Anthropic as nonsense. Caught by checking the return
  type rather than by a failed call, and a test now asserts that
  `str(model) != model.key` so the trap cannot become invisible.

AND A MISSING KEY IS REPORTED AS ITSELF. With no credential the client still
constructs - the CALL is what fails - so the orchestrator sees an empty
string and notes "agent_fn returned no text", which reads as "the model ran
and had nothing to say". The adapter replaces that note with which model
could not be reached and why, and says the tool half's results stand on
their own. A refusal reading as an empty result, one layer up from where
this repository usually finds it.

THE MOST USEFUL PLANT WAS THE ONE THAT FAILED TO APPLY. Three defects
planted into the agent half were caught; a fourth - reverting an adapter to
`agent_fn=None` - missed its anchor, never planted, and the suite passed.
That pass was the finding: nothing asserted the WIRING, only the parts
either side of it, which is exactly how the orphan survived in the first
place. Two tests now hold it, and the plant lands.

### A multi-value header was a Python literal in the artifact

`_header_dict` preserves multi-value Set-Cookie with
`resp.headers.get_list(...)`, because collapsing it loses cookies. The
redaction then coerced any non-`str` value with `str()` - right for a
model-supplied header dict, where a JSON array is legal input, and wrong for
this one. Two cookies became a single string holding a Python list literal,
which is what a report prints as the evidence for a cookie-flag finding.
Each element is redacted on its own now and the list stays a list.

AND THE PART THE READER OF THAT CODE GOT WRONG IS RECORDED TOO, because the
next person should not re-fix it. The claim was that the mangling leaked the
values. It does not: the cookie redaction splits on "; " and finds "=" in
`'sid=secretvalue1`, so the value was masked even inside the literal.
Measured both ways through the real client against a local server sending
two Set-Cookie headers - no credential either way. The defect is the SHAPE
of the artifact, not a disclosure, and the test says so.

The first measurement of this was also wrong and in a way worth naming: it
called `str()` and `split("; ")` BY HAND on a recorded value, reproducing
what the claim said the code does rather than running the code. The recorded
value was already an intact list, so the mangled output came from the
measurement, not the tree. The honest path was a local server and the real
`GuardedClient`, which is also what showed `record_exchange` does no
redaction at all - that happens in the client, so a test that calls
`record_exchange` directly measures nothing about it.

### A bug-bounty shaped report, and three things it will not print

The existing renderers answer "what did this engagement find". A triager
asks something narrower and in a fixed order: what is it, how bad, how do I
reproduce it, show me the bytes. `report-h1.html` renders that shape - one
section per finding, strongest proof first - and `render_report` writes it
beside the others under the same convenience contract as the HTML one, so a
failure there cannot cost the canonical markdown report. It is served as the
`h1` format under the same sandbox CSP, which is why it carries no script
and no external resource of its own.

Three refusals, each from reading what the recorder actually holds rather
than from taste, and each with a test because a refusal nobody checks is a
comment.

NO REPLAY COMMAND IS COMPOSED. A `curl` built from a recorded exchange would
carry the redaction marker where twelve request header names and
`Set-Cookie` are masked, so it would be wrong to READ and wrong to SEND -
and a reader would reasonably assume a command in a PoC was the command that
ran. The literal recorded request is printed instead, and where the client
captured raw wire bytes those are the PoC, because they are what went out. A
rebuild from the recorded parts is LABELLED as a rebuild, since a
reconstruction must not be taken for a capture.

NO URL EVER REACHES AN ATTRIBUTE. Every byte in a finding is
target-influenced, so text nodes only - the same reasoning the operator
console uses for having no `innerHTML` at all rather than escaped
`innerHTML`. Checking this the obvious way was wrong and is recorded:
grepping for `href=` found 101 hits and reported a defect, because the
TARGET's own recorded HTML body is quoted, escaped, inside a `<pre>`.
Parsing settles it - the only attribute names in the whole document are
charset, class, content, lang, name and style. Fifteenth instance this
session of a checker reading a mention as a claim, and the checker was mine.

ABSENCE IS PRINTED. The existing HTML renderer shows a missing field as an
empty cell - an empty `<pre></pre>` under "Proof (verbatim excerpt)" - which
reads as "no proof" when it means "no field". Here every section that cannot
be built says which piece was missing. A finding may cite an EVENT id with
no request at all, and the shipped sample's jwt finding does exactly that:
it gets a sentence saying the event carries no request and is therefore not
a step, with its recorded output still shown as evidence.

AND THE RESPONSE WINDOW IS CENTRED ON THE QUOTED BYTES, taken from the
markdown renderer rather than the HTML one. `html.py` prints
`response.body[:4000]` from the start, so on a longer body whose proving
bytes are later the HTML report omits the proof while the markdown report
shows it. The offset is stated rather than implied.

Steps to reproduce are DERIVED from the cited exchanges and nothing else -
argus stores no reproduction prose, a search of the tree finds no such
field, and composing it would be the thing this whole system refuses.
Remediation is left out with the reason, because fix advice nobody observed
to work is the same failure as an invented finding.

Plant-tested four ways: emitting a curl, un-centring the window, dropping
the no-request sentence, and offering generic remediation each fail.

### The bug-bounty report joins the seal, and the documentation

Two things the suite and the gate caught after the renderer worked.

THE NEW ARTIFACT WAS OUTSIDE THE SEAL. `render_report` writes
`report-h1.html`, and `Session.seal` enumerates the artifacts it hashes by
name - so a freshly sealed session reported `report-h1.html` as an unsealed
ADDITION, which `test_a_file_added_after_sealing_is_named` failed on
immediately. An artifact outside the seal is an artifact nobody can check,
which is the opposite of what sealing is for. It is in the list now, and the
list carries the note that a new renderer missing from it produces exactly
that failure.

AND IT WAS DOCUMENTED NOWHERE, which the reverse-direction check added
earlier today exists to catch. `docs/USAGE.md` names it in the artifact
listing and explains the three refusals as refusals rather than as missing
features, because a reader who does not know why there is no `curl` will
reasonably assume it was an oversight and add one.

ONE MORE INSTANCE OF A SHAPE THIS SESSION KEPT HITTING, and a new guise:
the sentence "argus stores no reproduction prose" happened to begin a LINE,
and the subcommand check reads a line starting with `argus <word>` as a
command claim - so it reported a subcommand named `stores`. Not the content,
the line wrapping. Sixteenth instance, and the fix was to rewrite the
sentence so no line opens with that word.

### The agent whose job is the narrative was the one denied the evidence

`read_findings` is a dedup view and its docstring says so: "workers only
need class+endpoint+id to skip already-proven work". The REPORT role used
that same tool for a different job. `report-writing.md` instructs it that
"every claim traces to an id" and that "the grade is not decoration" - and
the slim view carries no evidence id, no grade and no excerpt.

So a role was told to trace claims to ids by a card whose tools could not
show it one. `report.md` documented the dead end honestly rather than
hiding it - "no tool of yours returns them ... write the sentence without
the quote" - which is why this survived: the contradiction was written down
as a limitation instead of read as a defect.

The data was never missing. It is in findings.json, the deterministic
renderer reads all of it, and the one agent whose whole job is the narrative
was the one that could not see it.

`read_findings_full` is the view that job needs: the evidence ids, the
grade, the excerpt, and for a grade below `proven` the requirement and the
checks it was short of - so a sentence about a candidate can name the reason
instead of hedging. "Candidate because no row was read from a named table"
is a result a reader can act on; "possible SQL injection" is not.

NOT BY WIDENING THE SLIM VIEW, and a test holds that too: every recon and
exploit worker pays for whatever that view returns, which is why its
narrowness is deliberate. A separate tool, granted to the roles that write
prose - report, and lead for the fallback summary - so the restriction stays
in the card where `dispatch` enforces it rather than in a prompt.

All three steps in the same edit this time: registered, granted, and taught
as START HERE on the card, because a role that holds a tool and is not told
to use it holds it the way the registry held the orchestrator.

AND THE INVARIANT THAT GUARDED THE OLD BULLET CAUGHT THE NEW ONE. A test
asserts the report prompt promises only fields the tool returns, parsing
only that tool's bullet - and its docstring warns why: the card names
`excerpts` in order to say they are NOT in the slim view, "which a
word-level check would read backwards". The new bullet said the slim view
"carries no evidence id and no grade", so the check read those words as
promises. Seventeenth instance this session of a mention read as a claim,
and the first where the test's own docstring predicted the failure mode
before it happened. The bullet points at the other tool instead of naming
what it lacks, and a parallel invariant now guards the new bullet, measured
by CALLING the tool rather than reading its docstring.

Plant-tested four ways: dropping evidence_ids from the new view, widening
the slim view instead (the wrong fix), not granting it, and granting
without teaching each fail.

### I ran my own gate twenty times and never ran the project's

The repository's CI is ten jobs: five Python versions across ubuntu AND
windows. The gate I ran all session was `pytest` plus `selftest` on Linux,
and it was green every time. Windows had been red since my first commit of
the session, and the README carries the badge that says so.

Found because the user asked why it was failing. Measured from the API: the
last green run was the remote commit I merged in; the first red one was my
merge, and the commit it brought was mine. Thirteen consecutive failing
runs, every one of them after a local gate I had just watched pass.

That is the `count-the-gate-against-reality` shape, and this time the
denominator was not a check's file list - it was my idea of what "the gate"
meant. A subset measured carefully is still a subset.

THREE FAILURES, ALL WINDOWS-ONLY, AND NONE A PRODUCTION DEFECT.

Two were one line of a TEST FIXTURE: `write_text("# report\n",
encoding="utf-8")` with no `newline=""`, so Windows translated the newline
and every byte-level assertion about that file was off by one per line.
`test_reports_listing_names_the_formats_present` failed with
`b"# report\r\n" != b"# report\n"` and
`test_head_is_routed_and_sends_no_body` with a Content-Length of 10 against
9 - two failures, one line.

The third is more interesting, and it is a measurement smaller than its
instrument. `test_exploit_fanout_really_runs_endpoints_concurrently` proves
concurrency twice: a barrier a serial implementation deadlocks on, and then
the recorded `[started, started+seconds]` windows, which must intersect.
Windows' `time.monotonic()` has ~15.6ms granularity against ~1ns on Linux,
and the runs recorded `[(260.89, 0.016), (260.89, 0.016), (260.906, 0.0)]` -
a run faster than one tick records a duration of ZERO, and a zero-length
window cannot strictly intersect anything.

The fix is NOT a looser comparison. A tick of slack on both sides would make
the SERIAL case overlap too, and that is the direction that matters - the
test next to it exists to fail if the overlap check could pass without
concurrency. So the measurement was made resolvable instead: the barrier
already proves all three are in flight, and the mock now holds for 150ms
after it, which is about ten ticks of the coarsest clock in the matrix.

Verified by simulating the coarse clock rather than by pushing and hoping:
quantised to 15.6ms, the held windows intersect, the old unheld ones do not
(which is the CI failure reproduced), and the serial windows still do not.

### Twenty-nine checks could not see three quarters of the file disappear

Reported by the parallel session that owns `argus/web/dashboard.html`: a bad
slice deleted 521 of the stylesheet's 672 lines and all of its checks still
passed. Taken as work on this side, because the test file is not that HTML
file and a suite blind to a deletion that size is a gate defect, not a style
question.

Why they were blind: every one of the twenty-nine asks a QUALITATIVE
question - is there an external resource, is there an HTML sink, are the two
modes confusable, can an engagement launch without its authorisation fields.
151 lines of stylesheet answers all of them exactly as 672 lines do. The
checks were sound; what they were silent about was the SIZE of the thing
they were checking. Same hole as a proof gate that grades a finding with no
evidence attached.

Two checks, and the second is the one with diagnostic power. A structural
floor - stylesheet lines, rules, tokens, file bytes, @media blocks, each set
near half of the committed values so a rewrite never trips it - plus brace
balance. The first version of those figures was taken from a MID-EDIT state
of a parallel session's file and matched no commit; the floors sat below
every version either way, so a number cited as the basis was false while
the check was sound. Then: every `var(--x)` WITHOUT a fallback must resolve to a token
defined in the stylesheet or in an inline `style=` attribute. A cut that
removes the `:root` block is 1863 bytes and 38 lines, leaves the braces
balanced, stays above the line floor, and breaks every colour on the page,
because an unresolvable `var()` is invalid at computed-value time.

AND THE CHECK'S FIRST VERSION REPORTED A DEFECT IN CORRECT CSS. It read
`animation-delay:var(--d,0s)` as a requirement for a token named `--d` and
found it undefined. But that reference carries a fallback, and `--d` is set
per element by an inline `style="--d:.1s"` to stagger the entrance - a
conditional reference, counted as an unconditional one. Eighteenth instance
this session of a mention read as a claim, and the first caught BEFORE the
test was written, by going to look at the single violation instead of
accepting the count. Every grep for it came back empty, which is what said
the measurement was wrong rather than the file.

Then the comment on the new check over-claimed in the other direction - it
said the var() check was the only one that catches a `:root` deletion, and
the plant showed the token floor catches it too, since 32 of the 36 tokens
live in that block. Corrected to what it is: not the only check that fires,
the one that names WHICH references broke instead of reporting a number that
got smaller.

Plant-tested four ways against a REDIRECTED COPY, never against the file
itself, because another session has uncommitted work in it: a 521-line cut,
a `:root` deletion, a mid-rule cut, and the real file passing. Wiring as
well as logic - the test module's `DASH` constant was pointed at each
gutted copy and the function called directly, so the proof is that the check
reads the file, not merely that its arithmetic is right.

### AGENTS.md named a gate that was not the gate

Three defects in seventeen lines of the contributor-facing document, all of
them the class this repository's doc gate exists to catch - documentation
naming something other than what is true:

- "Windows-compatible" as a flat claim, while Windows CI was red.
- Three commands presented as the verification step, when CI runs ten jobs:
  those checks on five Python versions across ubuntu AND windows, plus a
  `wheel` job none of the three commands exercises.
- "Both must stay green" counting two for a list of three.

A contributor following that document is blind exactly where I was blind,
which is how a local gate stayed green for twenty runs while five of ten CI
jobs were red. Rewritten to name the real gate, to say what the local
commands cannot see (newline translation and a ~15.6ms clock on Windows),
and to give the wheel job as three runnable lines - including `cd` out of
the repo first, because Python puts the tree on `sys.path` and you measure
the tree while believing you measured the wheel.

RAN THE WHEEL JOB FOR THE FIRST TIME. It passes: 107 files, all six data
files the tools resolve, the console script works from site-packages, the
demo produces a summary.json, and the checked-in sample session still
verifies (66 chained entries, 6 findings re-validated).

And measuring it produced three measurement errors in a row, each caught by
going to look at the specific instance rather than accepting a count:

- `TOOL_SCHEMAS` is a LIST of 60 schemas, and `"read_findings_full" in
  TOOL_SCHEMAS` asked a containment question of the wrong container type.
  Reported the new tool as missing from the wheel; it ships.
- The first check ran with the repo on `sys.path`, so it read the tree while
  claiming to read the installed wheel - which is now a warning in AGENTS.md.
- `'nmap '`, `'the '` and `'of '` were extracted as CSS class prefixes for
  sitting before a `+`, and a 400-character window attributed `className =`
  to seven functions that do not set it.

Then the edit that fixed the document broke the document gate: an invocation of the GitHub CLI, with its
own flag, went into a file the check reads for argus's own flags. Twentieth instance this session, introduced while
writing about naming only what is true. `gh ` joins `docker`, `pip ` and
`npm ` in the line-level exemption and NOT `_ALLOWED_TOOLS`, which is what
`run_external` may invoke.

### A floor cannot see a three-rule cut

The session that owns the dashboard read the structural floor and named its
limit precisely: it catches a 521-line deletion and is blind to the same
mistake at a tenth of the size.

The complement is `test_every_grade_and_severity_name_has_a_rule`, and it
fails at any size. It reads `var GRADES` and `var SEVS` out of the file's
own script - 9 names, not a list typed here - and requires each to have a
CSS rule. They reach the DOM by concatenation (`el('button', 'cell ' + g)`,
`setCls(root, 'row ' + g)`), so a missing rule is not a style regression: a
`proven` finding renders identically to an `unproven` one. That is a false
verdict in a tool whose whole claim is that it does not assert what it has
not proven.

Scoped to grades and severities and NOT to `.panel` or `.hero`, although
those were suggested. Those are layout classes, that session is mid-redesign,
and a check that forbids renaming them is a check against work. Grades are
argus's vocabulary: rename one and `var GRADES` has to move too, and the
check follows.

### The checker read lines; the discriminator was in the sentence

`docs name only real flags` reported `--workflow` as a flag argus does not
accept. It does not: the text was `gh run list --workflow test.yml`, the
GitHub CLI's own flag, in AGENTS.md's new paragraph about reading CI after a
push. The first fix added `"gh "` to the line-level other-program exemption,
beside `docker`, `pip ` and `npm `, and AGENTS.md was then excused
correctly.

IT STILL FAILED, from the CHANGELOG sentence describing that fix. The
sentence names `gh run list`, and it WRAPPED, so the line began with
`--workflow test.yml` and carried no `gh`. The checker reported a flag argus
does not accept, out of a sentence explaining that exact mistake.

So the durable fix is neither keying on the token nor keying on the command:
the token and its command were in one SENTENCE and two LINES. The unit was
the defect. The check now runs per paragraph - lines joined until a blank
one, the smallest span that holds a whole sentence in these documents -
which closes the `gh` case, the `docker build --platform` case nobody has
written yet, and the case this repository already hit where a wrap put a
subcommand name at the start of a line, away from the quotation marks
that made it an example - the fix there was the same one as here: do
not let the example wear the punctuation of a command.

Twenty-fourth instance this session of a mention read as a claim, and the
third to arrive by line-wrapping specifically. Every earlier fix treated the
WORDS; this one treats the unit the words are read in, which is why it
covers the cases not yet written.

PLANT-TESTED, AND ONE PLANT NAMES THE COST. A fake `--invented-flag` in an
argus-only paragraph is caught. `gh run list --workflow` with the sentence
wrapped passes. And a fake `--invented-flag` in the SAME PARAGRAPH as a
`docker build` line is now EXEMPTED, which the line-based version would have
caught.

That hole is kept deliberately. A flag check that cannot survive a line wrap
produces false failures on correct documentation, and a false failure costs
more than this hole: it teaches the next reader to edit the check instead of
reading it. The same reasoning as declining to freeze `.panel` and `.hero` -
a check that fires on correct work gets edited, and then it is not a check.

### A flag belongs to the command it follows, not to a list of names

The paragraph fix above made the unit right and left the exemption an
ad-hoc list of program names: `docker`, `pip `, `npm `, and `gh ` added
that same hour. A name list closes one program per failure, forever, and
the next failure was already written - a document line reading `pytest
--last-failed`, whose flag belongs to the program this repository's own
gate instructions invoke, reported as a flag argus had invented.

So the exemption now asks who the flag belongs to. In a fenced block that
is the first token of its line; in an inline span, the first token of the
span; a flag in bare prose has no command and stays argus's, which keeps
the sentences that really are claims about argus under the check.

AND `python` IS NOT A PROGRAM FOR THIS PURPOSE. First version read
`python -m pip wheel . --no-deps` as argus's, because its first token is
`python`, and reported pip's flag as invented. `python -m argus` is the
canonical argus invocation and has to stay argus's, so the module after
`-m` is the discriminator and the interpreter is not.

Plant-tested serially - six shapes, one selftest run each - after two
concurrent plant loops mutating one document returned OPPOSITE verdicts for
the same planted line. Two measurements that disagree are two measurements
to discard, not one to pick.

### The subcommand check was right and the markup was mine

Reported as the same defect needing the same fix: `docs name only real
subcommands` failing on `stores`. It is not. That check keys on markdown's
own convention for "this is a command" - a backtick, then `argus`, then a
word - and the sentence that tripped it was mine, written minutes earlier,
with backticks around an example of a thing that is NOT a command.

The repository had already decided this, in the entry recording the first
instance: the fix there was to take the backticks off and let the example
wear quotation marks instead. Applied the same way rather than widening a
check that was reading the markup correctly. Twenty-fifth instance, and the
third where the text explaining the defect reproduced it.

### The evidence table could clip a timestamp and nothing would say so

Reported from a real regression by the session that owns the dashboard:
collapsing nine font sizes into three steps clipped `Started` to
`01:53:...`, and two runs forty seconds apart read as the same instant.

Not a style regression. The display asserted something the data does not
support, which is the failure the proof gate exists to prevent - recorded
there, rendered here.

`table-layout: fixed` is why nothing connected the two: a cell's own width
is ignored, the `<colgroup>` in the markup is the only control, and a
font-size change in the stylesheet silently outgrows it. Nothing links them
but arithmetic, so the arithmetic is the test. Every quantity is read from
the file - the character count summed from `clock()`'s own return
expression, the font size from `td.mt`, the padding from `tbody td`, the
width from the column whose HEADER SAYS `Started` rather than from an index,
so reordering the table cannot leave the check measuring a different column
while still passing.

TWO OF MY OWN ERRORS, BOTH CAUGHT BY ASSERTIONS ON DERIVED VALUES:

- The character count came out as 2. `clock()` opens with an early
  `return '--'` guard for a missing timestamp, and the first `return` is
  that one. Without the `chars == 19` assertion this test would have
  demanded room for two characters and passed forever.
- The negative direction asserted that a one-pixel font increase breaks the
  column. It does not: 172.2px needed against 174px declared.

AND THE CORRECTED VERSION WAS ALSO WRONG, IN THE OTHER DIRECTION. From
13.2px of headroom it concluded the reported regression could not have been
one step on `td.mt` alone. Measured in the live page by the session that hit
it: 174px is the width that session had ALREADY WIDENED THE COLUMN TO while
fixing it. It was 158px when it broke. At 158px, 11.5px needs 155.1px and
fits, 12px needs 160.8px and clips by 2.8px - so the trigger was 11.5 ->
12px, a HALF step.

The anchor was the defect, and the anchor was a post-fix value. A fixed file
cannot reproduce its own regression: anyone measuring that column now reads
13.2px of headroom and concludes it was never tight, when it was tight by
2.8px in the other direction four hours earlier. Two independent
measurements of the bound AGREED - 160.8px needed, 13.2px spare, breaks at
two steps - while the history those numbers were used to reconstruct was
wrong. Agreement on a quantity is not agreement about what it explains.

One figure neither side had claimed, and it is the one worth keeping: one
step up is 13px, needing 172.2px against 174px. That is 1.8px of margin,
not a comfortable step, and 12px and 13px are now adjacent in one scale -
so `.mt` joining the body tier is a single plausible edit that fits by less
than two pixels.

### Having just named a pattern is not having internalised it

The stylesheet floor was labelled `file bytes` and measured `len(text)`,
which is CHARACTERS. The dashboard's comments are in Vietnamese, so the two
quantities diverge by 2,367 - 105,550 bytes against 103,183 characters,
from 1,534 multi-byte characters. Nothing failed, because both sit far
above a 60,000 floor, but the drift is one-directional: characters stay
flat as non-ASCII prose is added and bytes grow. The floor now reads the file's length in
bytes rather than in characters, because a deleted stylesheet is a loss of
bytes on disk and that is what the floor protects.

A floor whose name and quantity disagree is the `--workflow` defect one
level in: the number is right and the thing it claims to measure is not.

AND THE DIAGNOSIS WAS ONE PARAGRAPH LATE. Two sessions measured that file
and reported 36 tokens against 43, and 105,550 bytes against 103,183. The
token pair was correctly identified as one value and two questions - 36
inside `:root`, 43 declarations in the stylesheet - and both denominators
were written into the test so nobody would correct one into the other.

Then the byte pair, in the next sentence, was read as a discrepancy in the
other session's measurement, and written up as its measurement failing to
match the commit it came from. Five methods settle it: `git cat-file -s`,
`git show | wc -c`, `wc -c`, and reading the path as bytes all say
105,550. Only measuring its decoded length in characters says 103,183.

So the pattern was named accurately and applied to the next instance
anyway, by the same reader, in the same paragraph. That is worth recording
separately from the fix: `one-value-two-questions` is not a lesson that
stays learned by being stated. The operational form is narrower - when two
careful measurements of one file disagree by a fixed amount, the question
is which quantity each one answers, BEFORE the question of which is wrong.

Also corrected: a claim about another session's measurement, written into
this file while that measurement was right.

### Nothing asserted that a registered tool was reachable by anybody

Registering a tool and granting it to a role are separate edits in separate
files. The registry is what dispatch resolves; the card is what decides
whether a worker may ask. A tool in the registry that no card grants is
reachable by nobody - it imports, it passes its own unit tests, and no
worker can call it.

This tree has shipped three components in exactly that state, one of which
said so in its own docstring. It nearly shipped a fourth twice in one
session: `recon_sweep` and then `fanout_sweep` were each registered without
a grant, and each time the miss was caught only because a skill card
happened to name the tool and a different check reads skill cards. Nothing
checked the relation itself, so the catch was a side effect both times.

Now asserted in both directions, which is the same statement read
backwards. A card granting a tool the registry does not have is the more
dangerous half: dispatch refuses it, so the role is promised a capability
that fails at the moment it is used.

Measured before writing it: 60 registered, 60 reachable, four roles, zero
orphans and zero ghosts. The invariant held, so this closes a hole with no
current occupant.

A check whose first run finds nothing reads as wasted work and is the
opposite. Adding it while it would still fail means arguing about the
findings instead of installing the invariant: somebody has to triage a
backlog before the check can be green, and a check that is not green yet
does not gate anything. Zero occupants is the only moment when the first
run tells you nothing you did not already know, which is exactly what
makes it cheap.

AND THE TWO NEAR-MISSES WERE MINE, which the record had briefly wrong.
`git log -S` settles it: `recon_sweep` entered at a183382 and
`fanout_sweep` at 1dd14f1, both orchestrator-wiring commits from this
session. The parallel session that found the shape attributed it to itself
from a plausible reconstruction, having every particular right - two tools,
registered without grants, rescued twice by a check that was not looking
for them - and the owner wrong. Fourth instance today of agreement on the
facts with the wrong story attached, and the first where the disputed
quantity was authorship.

### CI confirms the Windows fixes, which nothing local could

Run #566 on `c3641c1`: 11 of 11 jobs green, including all five Windows
jobs that had been red for thirteen consecutive runs. The newline fixture
and the clock-resolution fix are verified by the only instrument that can
verify them, since no local run on this machine executes Windows at all.

### A race that only CI could see, and the test was the thing that was wrong

CI on aea6273: 8 jobs green, 3 red, and the pattern ruled out every simple
explanation. ubuntu 3.10, 3.11 and 3.13 failed while ubuntu 3.12 AND 3.14
passed between them, and all five Windows jobs passed on the same
versions. A version boundary cannot skip 3.12; a platform cannot be the
cause when the other platform passes everywhere. So: a race.

`test_a_chunked_body_is_refused` raised BrokenPipeError inside
`conn.request()`, before `getresponse()` was ever reached. The test is
older than this commit and the previous commit passed 11 of 11, so it had
been flaky all along and nothing had looked.

AND THE SERVER IS RIGHT. It answers 411 and closes as soon as it sees no
Content-Length, which is exactly what the test asserts. `http.client` with
an iterator body performs four separate writes - head, chunk-size line,
chunk, terminator - and if the close lands between two of them the client
fails on the write, discarding a response the server had already written.
A correct refusal broke the test that checks the refusal.

Rewritten at the socket, tolerating BrokenPipeError and ConnectionReset on
the write, then reading to EOF because 411 closes the connection.

MEASURED, BECAUSE 15 GREEN RUNS PROVE NOTHING HERE. The race reproduced
locally at 1 in 12. At that rate fifteen consecutive passes happen 28% of
the time by luck, so the fix was run 60 times: 60 green, which luck would
manage 0.7% of the time.

AND THE FIRST PLANT PASSED, WHICH WAS THE PLANT'S FAULT. Replacing the
chunked test with `if False:` let control fall to the next check, where a
chunked request has no Content-Length either - so the server still
answered 411, with a different message that also contains the words
`Content-Length`. The plant had not created the shape it was named for.
Planting the real shape - the server accepting a chunked body and
answering 200 - fails the test as it must. Fifth time in this repository
that a plant's own failure to apply was mistaken for a check that cannot
fail.

### Proven by the matrix, read by nobody else

Raised as a supervisor's objection to agent findings in general: an agent
can invent a command's output and call the exploit a success. Measured
against this gate first, because the answer decides what is worth building.

THE FABRICATION CASE IS ALREADY CLOSED, and demonstrably. Grading an `id`
output that no recorded response contains:

    [x] proof read from the wire
    [ ] the target produced the quoted bytes
    [x] a benign command was sent
    [ ] identity output returned by the target
    [ ] the quoted bytes are the command output
    [ ] the probe nonce came back in the output
    -> unproven

An invented excerpt cannot reach `proven`, the gate names the three checks
it failed, and `tests/test_proof.py` already asserts that universal check
for every class in the matrix. The same evidence with the bytes really on
the wire grades `candidate`, held back by the nonce check - the gate wants
the value to have been SENT in an earlier recorded request, not merely to
appear.

WHAT WAS NOT CLOSED is the second half of the objection. The matrix reads
BYTES; it does not read the INTERPRETATION. Bytes that really came off the
wire can still be the wrong class, a reflection presented as execution, or
a severity nobody can support. `argus/judge.py` exists for exactly that -
a model from another family reads the cited evidence records and never the
first model's reasoning, because "two models that agree because they share
a prior are not a check" - it has 39 tests, and NOTHING EVER ASKED FOR IT.

Three measurements of that gap:

- `argus judge` is a manual subcommand. No code path calls it after a
  finding is recorded.
- A sealed, verifying session's `proven` finding carries no `judge` key at
  all. Its bytes are verified; its reading was never reviewed.
- `next_action` rule 2 skips a `proven` finding as finished, and rule 7 -
  "the only exit" - said every recorded finding is "graded". Graded is not
  reviewed, and that sentence was the whole of the difference.

Rule 6b now stands in front of the only exit: a `proven` finding no model
from another family has read is unfinished work, named by id. Placed there
and not earlier on purpose - breadth stays the engagement's job, so
`widen_surface` and the class-gap rules keep their priority; what changes
is that an engagement can no longer SEAL while a finding it will report has
been read by one model only. A judged finding exits normally whether the
judge agreed or disputed: a dispute is a completed review, and asking again
until a judge agrees is shopping for the answer.

A VERDICT CARRYING AN ERROR IS NOT A REVIEW. The judge was asked and could
not answer - no credential for that family, a refusal, a timeout - and
counting a failed call as a completed check is how an unchecked finding
would look checked. Same shape as a dead run that seals and verifies clean.

### And the absence had to be printed on all three artifacts

The renderers disagreed about a finding nobody cross-read, each silently:

- markdown discussed a verdict that exists and printed nothing when none did
- `html._judge_html` returned the empty string for that case
- the bug-bounty artifact never mentioned cross-verification at all, while
  printing a `PROOF: PROVEN` badge

So on the one artifact that leaves this machine for an outside reader, a
proof badge stood alone and read as the whole verification. All three now
say it: "Cross-verification: not performed - the proof grade is the matrix
reading the recorded bytes", and the badge row carries NOT CROSS-VERIFIED,
CROSS-VERIFIED BY <model>, or DISPUTED BY <model>, with a dispute
outranking any later agreement.

The badge row was extracted from `_one` into `_badges(finding)` to be
callable alone, because a unit nobody can call alone is a unit nobody tests
alone - and the first version of that test called a markdown helper that
does not exist, which is the same defect one layer out.

Plant-tested four ways: markdown silent again, html returning "" again, a
judge error counted as a review, and a later agreement hiding an earlier
dispute. Each fails.

AND ONE TEST ASSERTED THE OPPOSITE, correctly, until now.
`test_an_unjudged_finding_renders_exactly_as_before` required the string
"Cross-verification" to be ABSENT from an unjudged finding. That was the
right guard when the judge was introduced - it proved the new feature
leaked no markup into findings with no verdict - and it is the wrong guard
once silence is the defect. Rewritten rather than deleted, with the retired
premise written into it, and keeping the half that still holds and always
mattered: an unjudged finding must not read as AGREED or DISPUTED. Saying a
check was not performed and implying its outcome are different claims.

### The second CI-only flake, and a precondition is not a claim

CI on e239843: 10 jobs of 11 green, one red on ubuntu 3.14 - the version
this machine runs, with the local gate green.
`test_many_sequential_runs_do_not_accumulate` failed `assert 429 == 200`.

429 is the console's own concurrency cap, and it is RIGHT. The four slots
are released by each run's WORKER THREAD, so a POST issued before the
previous thread has released its slot is refused correctly. Whether that
happens is thread scheduling against the speed of a test loop.

THE FIX IS TO SEPARATE THE PRECONDITION FROM THE CLAIM. That test claims
four things - n runs on disk, live records bounded, dead threads reaped, an
evicted run still readable through its sidecar. `status == 200` is how it
REACHES n runs; it is not what it asserts. So the precondition retries and
every claim stays strict.

And the retries are COUNTED, with `retries <= n`, because a blind retry
loop turns "the server refuses every request" into a slow pass. Plant-
tested both ways: a server that 429s everything fails the test, and the
concurrency cap lowered to 1 - the worst scheduling case - passes.

### Then the amplifier found a third, and the third was the instrument

Two race flakes in one file, both green locally and red on CI, is a reason
not to wait for CI to find the next one. Ten local runs of the whole web
suite: 80 passed, ten times, no flake. That is WEAK EVIDENCE and worth
saying so - the local gate is the instrument that missed both of the known
ones.

So the race was amplified deterministically instead: concurrency cap 4 ->
1, which is the worst case for slot contention, five runs of the suite. It
found `test_the_lifetime_run_cap_stops_an_unbounded_post_loop` failing one
run in five.

THAT FAILURE WAS MY OWN INSTRUMENT. The test patches the LIFETIME cap and
spawns with the module default for the concurrency cap, so lowering that
default put it in a configuration it never runs in. At the real cap it
passes ten times out of ten.

But the sensitivity it exposed is real and worth fixing: a test about the
lifetime cap depended, unstated, on the concurrency cap being at least two.
Its claim was already exact - `"lifetime cap" in errors[0]` distinguishes
the two 429s, so a slot refusal could never satisfy it - and only the
precondition needed to be robust. Now 8 of 8 with the cap at 1, where it
was 4 of 5 before, and unchanged at the real cap.

A deterministic amplifier is worth more than load for this: load produced
three timing failures in one gate run on this machine and told me nothing
about which were real, while one changed constant named the coupling
exactly.

### Fixing one assertion per CI round is a losing pattern

Three CI-only races in one file, found one at a time over three runs, and
the third was the same test as the second failing on a DIFFERENT line. That
is the point to stop patching and characterise the shape.

ALL THREE ARE ASSERTIONS ON STATE A WORKER THREAD WRITES, read in the same
breath as the request that started it.

- `assert 3 <= (0 + 1)`: the thread-list check compared
  `len(_threads) <= len(alive) + 1` with `alive` computed AFTER `wait()`
  joined everything, so `alive` is always 0 and the assertion meant `<= 1`.
  That holds only while runs finish faster than the loop creates them.
  Replaced with the DETERMINISTIC invariant: reaping happens inside
  `create()`, which filters to live threads and appends one, and
  concurrency bounds the live set - so the list is bounded by
  `max_concurrent + 1` always, and would be 80 if reaping were broken.
- `assert 'running' == 'failed'` at the SIDECAR, not at the API row. The
  row is derived from the directory and is terminal as soon as the runner
  returns; the sidecar file is flushed by the worker thread. The test
  already polled for the row and then read the file immediately.
- the 429 precondition, fixed in the previous commit.

A `_until(cond, timeout)` helper now carries the pattern, returning the
condition's last value so a failure message shows the real state rather
than `False`.

THEN THE SWEEP, AND ITS FIRST ANSWER WAS WRONG. Grepping for assertions
that read background-written state found 15 with no preceding wait - and
most read PLANTED sessions, which have no worker thread at all. The
syntactic shape is not the hazard, which is the same error as reading a
mention as a claim, this time in my own analysis.

Narrowed to assertions inside tests that actually POST /api/runs: ZERO
remain. So the three fixed are the complete set of that shape, which is a
stronger statement than ten green local runs - those found nothing while
the local gate was the instrument that missed all three.

It is one shape, not every race. The chunked-body failure was a
client-versus-server write race and this sweep would not have found it.

AND THE VERIFICATION ARRIVED BY ACCIDENT, in the best form available. The
gate run that confirmed these fixes took 16,832 seconds - 4 hours 40
minutes against a normal 380, forty-four times slower - because the machine
was swapping: 160,083 pages out, 452 MB free of 7,938.

That is the worst timing environment this machine produced all session, and
every interleaving a race needs is stretched wide open in it. All three
formerly-flaky tests passed, and the suite was green: 1098 passed, 1
skipped, selftest 164/164.

A 44x-slower run is better evidence for a race fix than ten fast ones, and
the instinct is to discard it as noise.

### Asking the target again, with no model in the loop

The matrix reads a finding's BYTES. A judge from another family reads its
INTERPRETATION. Neither asks whether the target still does it, which is the
question a reader of a report cannot answer for themselves and the one an
outside reviewer applies first. `argus replay` sends the cited request
again through the same scoped, recording client and reports whether the
quoted bytes come back.

Three outcomes, and `inconclusive` is first-class rather than a soft
`not_reproduced`. A finding that fails to reproduce may be entirely real -
a target patched between the run and the replay, a stateful exploit, a
value that occurs once - and reporting those as refutations would make a
verification tool a generator of false retractions.

REDACTION MAKES MOST REAL ENGAGEMENTS INCONCLUSIVE, and the measurement
decided the design before a line was written:

    argus-lab        64 requests,  2 carry a credential   (3%)
    argus-lab-team   74 requests,  2 carry a credential   (2%)
    bwapp           23 requests, 23 carry a credential (100%)
    dvwa            18 requests, 18 carry a credential (100%)

A recorded request keeps `credential_sha256_16` - the HASH - so an
authenticated request cannot be replayed from the record. The self-written
lab barely authenticates; both third-party applications authenticate on
every request. A naive implementation would have reported both bwapp
findings as `not_reproduced` and retracted two real ones; the command
reports what it is, names the header that would settle it, and sends
nothing. Credential headers are dropped rather than replayed: the recorded
value is a hash, and a 16-hex string where a session cookie belongs is a
different request refused for a different reason.

FOUR SHAPE ASSUMPTIONS, EACH CAUGHT BY RUNNING IT RATHER THAN READING IT,
and the third would have been the worst defect in the module:

- `client.default_headers` does not exist; it is `_default_headers`. Every
  supplied credential was reported missing, so an authenticated finding
  could never reproduce. A test now pins the attribute name.
- `session.meta` and `session.target` do not exist on a reopened session.
  The target is in meta.json.
- **THE CLIENT DOES NOT RAISE ON A TRANSPORT FAILURE.** It returns
  `{"error": "ConnectError: ...", "status": 0, "body": ""}`, measured
  against a dead port on a real socket. So the `except` branch never fired
  for the commonest reason a replay cannot be performed, and an unreachable
  target produced `not_reproduced` for every finding - a target that was
  merely DOWN would have retracted an entire engagement. Only the error's
  TYPE is repeated, because a transport message can carry a URL and a URL
  can carry a credential.
- `verify_transcript` returns the FLAGS, not a verdict. Reading a `v["ok"]`
  that does not exist made the command refuse every session it was pointed
  at.

That last one had a second half worth more than the fix. The success
criterion was computed inline inside `argus verify --json` as nine
conditions, so a second reader had to restate it - and restating it is how
two callers come to disagree about what "verifies" means. Now
`session.chain_ok(res)` is the single definition and both use it.

AND THE COMMAND BROKE THE SEAL OF EVERY SESSION IT TOUCHED. `record_event`
appends a transcript entry, the tail moves past the chain head recorded in
summary.json, and `argus verify` answered MISMATCH - a command whose whole
purpose is verification invalidating the record it verifies. Re-render and
re-seal, the same trade `argus judge` makes. Now 26 chained entries verify
where there were 24, and a test holds it.

Reported in `next_action`'s exit and NOT blocking it, unlike the cross-read
rule. A judge needs only its own API credential; a replay needs the network
and, on an authenticated target, a credential the transcript deliberately
does not keep. A rule that blocked the exit on that would strand every
engagement whose target went down.

### A flat sleep is a cliff, not a bound

Windows CI failed `probe_ssrf_oob`'s callback test on `attempted and
fetched` while ten other jobs passed. The probe sent the payload, the
target's fetch had not arrived, and the probe had already decided.

`time.sleep(settle_s)` then check ONCE was wrong at both ends. A target
calling back in 50ms still cost the whole window; a target calling back at
`settle_s` plus a millisecond was reported as "no callback within Ns" -
which reads as a fact about the target and is a fact about the clock.

Polled instead, with the same ceiling, so a target that never calls back
costs exactly what it did before and nothing waits longer than it used to.
Measured: the two callback tests went from 3s of flat sleep each to 0.59s
and 0.51s.

AND THE TEST HAD MADE ITSELF TIGHTER THAN PRODUCTION. It passed
`settle_s: 3` against a product default of 4.0, so it was failing on a
window narrower than any real run uses. Widened to 8 as a ceiling, which
polling makes free. The two no-callback tests keep `settle_s: 1`: waiting
longer for something expected not to arrive proves nothing and costs
seconds.

I ALSO MISREAD MY OWN MEASUREMENT on the way. Run times moved 7.7s to
12.7s after the change and I attributed it to the wider window - then
`--durations` showed the two tests I touched at 0.59s and 0.51s, and the
5.03s belonging to `test_an_unroutable_target_is_refused_before_any_request`,
which has no settle window and is slow because a connect to an unroutable
address times out. The variation was never mine. A number that moved after
a change is not a number the change moved.

### Proven is one third of the verification, and no report said so

Measured on this repository's own sealed evidence, four sessions and 16
findings:

    graded by the matrix            16/16
    carrying a CWE                  16/16
    citing evidence ids             16/16
    read by a second model           0/16
    re-verified against the target   0/16
    severity critical               10/16

So both verification layers beyond the matrix - `argus judge`, which exists
and has 39 tests, and `argus replay`, written hours ago - had never touched
a single real finding. Nothing in any report said so, and a reader seeing
`proven` had no way to learn that `proven` was the whole of the
verification when it is one of three answers to three different questions:

    the matrix   did the target produce the quoted bytes?
    a judge      do those bytes demonstrate the class claimed?
    a replay     does the target still do it?

Every report now carries that table with the counts and the questions, and
when a layer is at zero it says which command would fill it. A verdict
carrying an `error` is not coverage and an `inconclusive` replay is not
coverage - the question was asked and did not arrive.

AND THE PER-FINDING REPLAY OUTCOME REACHED NO RENDERER AT ALL. `argus
replay` writes `replay`, `replays` and a one-way `replay_failed` into
findings.json; markdown, html and sarif mentioned none of them, and
hackerone's two mentions were about not synthesising a curl command. A
verification layer's outcome reached no reader, which is the same defect as
the silence about the judge - introduced in the hour after fixing that one.

### A floor expressed as a constant decays, and nothing goes red to say so

Reported by the session that owns the dashboard. The stylesheet grew from
791 to 953 lines with NO deletion involved, and a 521-line cut - the real
incident the floor exists for - then left 432 lines and 211 rules, above
both the 420-line and 200-rule floors. NEITHER FIRED.

A floor written as a constant has a sensitivity that decreases with every
addition to the thing it guards. The quantity it should compare against is
the file's own previous size, which is what HEAD holds. So the floor is now
0.65 of the committed size: content from the WORKING TREE, because a gate
checks what is about to be committed, and HEAD for SCALE only. Proved by
substituting a grown HEAD - the floors rise from 580 and 240 to 944 and
577, and the 521-line cut is still caught on both measures at the larger
size.

Not a bumped constant, which was the obvious fix and would have decayed
again on the next addition. The trade that WAS taken is recorded: scaling
from HEAD permits erosion, four deliberate commits each removing a third
taking 948 lines to 171 with nothing ever red, where the absolute backstop
stops it one step later. Erosion needs a sustained intentional act; decay
needed only ordinary growth and arrived unbidden.

THE SAME TWO CONSTANTS WERE IN A SECOND PLACE. A different test asserted
its planted cut "stays above every floor" against the literal 420 and 200,
so that assertion had also stopped meaning what it said. One concept, two
definitions - and the second definition is the one nobody is looking at.

AND THE FALLBACK I WROTE TO BE THE SAFE PATH WAS THE UNSAFE ONE.
`_committed_page` called `DASH.relative_to(ROOT)`, which raises ValueError
for a path outside the repo, while the handler caught OSError and
SubprocessError - so instead of falling back to the absolute floor the test
crashed. Found by a plant harness pointing the path at a temp file. A
fallback nobody has executed is a claim, not a behaviour.

### Two absences, one substring

Adding the per-finding replay line broke `test_markdown_states_the_absence_too`,
which asserted `"not performed" not in agreed` for a finding whose judge
agreed. It still passes its positive direction; what broke is that a SECOND
absence now uses the same words - a finding with a judge verdict and no
replay prints "Re-verification: not performed" - so the substring stopped
discriminating between two different claims.

Twenty-eighth instance this session of a check keyed on words rather than
on the form of the claim, and the first one written and broken by the same
hand inside an hour. Both assertions now name the claim
("Cross-verification: not performed"), and a new test holds that the two
absences are distinguishable in all four combinations, because they answer
different questions and a finding can have either, both or neither.

The pair structure is what surfaced it, for the second time today: the
positive direction goes on being true while the thing it is paired with
stops being true, and only the negative direction speaks.

### The findings table showed one finding out of ten

Found by the session that owns the console, and it is from this side of the
history: present in `a183382` at 13:29 and carried through every commit
since.

    /api/findings        10 findings
    #t-finds tbody        1 row

`var list = (S.findings || []).filter(matches)`, where `matches(f, filt)`
takes two parameters and opens `var F = filt || S.filt`. `filter` invokes
its callback with (element, index, array), so `filt` received the INDEX.
Element 0 got `0`, falsy, fell through to `S.filt` and rendered. Element 1
onward got a truthy number, `F.grade` was `undefined`, `undefined !== 'all'`
was true, and every remaining finding was discarded.

One row, always the first, whatever the data - and "one finding" reads as
DATA, not as a bug. On a console whose job is to show what was found, the
findings view understated the record by ninety percent and looked like an
answer.

WHY NOTHING CAUGHT IT. The unit tests call `matches(f)` with one argument,
so the function is correct and its tests are correct; the defect lives
entirely in the CALL SITE. And it only misbehaves with more than one
finding, so a single-finding fixture passes forever. This is the arity form
of the shape this repository keeps producing: the thing tested and the
thing used are not the same thing.

Asserted as the general rule rather than at the one site, because the rule
is general: a function with an optional second parameter must never be
passed bare to `filter`/`map`/`forEach`/`some`/`every`/`find`, because the
array method always supplies a second argument. `sort` and `reduce` are
deliberately exempt - their callbacks take more than one argument by
contract, so flagging a two-parameter function there would be a false
positive.

Plus the behaviour the reading predicts, driven under node: `matches(f)` and
`matches(f, 0)` both match, `matches(f, 1)` and `matches(f, 7)` do not.
That is why the symptom was one row and not zero.

AND THE CHECK FIRED ON A COMMENT ON ITS FIRST RUN. The only
`.filter(matches)` left in the file is inside the comment that QUOTES the
broken code in order to explain the fix, and a regex over the script
reported it as a live call site. Twenty-ninth instance of a mention read as
a claim this session, inside the check written to catch a different shape.

Fixed with a scanner rather than a wider regex: a naive `//`-to-end-of-line
strip would blank real code after every `https://` in the file, trading a
false positive for a false negative, which is the worse direction for a
check. Verified in both directions - a quoted call in a block comment and
in a line comment are ignored, a call after a `https://` string and a call
followed by a comment are both still found, and the line count is
unchanged so failure messages still point at the right place.

### A habit that fails five times is a mechanism that does not exist

The doc test count went stale FIVE TIMES in one session. Every time the
cause was identical: the number was taken by a separate `pytest
--collect-only` call, tests were added before the gate ran, and
`doc pytest count matches collection` failed. Each failure cost a full gate
run - six minutes - and each fix was the same two edits typed again.

Four times the number was fixed. The fifth time the mechanism was:
`scripts/refresh-counts.py` measures and writes in ONE step, with
`--check` to report staleness and exit 1 without writing. It does not get
to assert that it worked - `selftest.py` still checks the result
independently, which is the whole point of having the check at all.

Verified in all three directions rather than by running it once: on the
stale tree `--check` names both documents and exits 1, the write moves
them, and `--check` then exits 0.

AND DOCUMENTING IT TURNED THE GATE RED, which exposed a real hole rather
than a nuisance. `python scripts/refresh-counts.py --check` in AGENTS.md
had its flag attributed to argus, because flag ownership resolved
`python -m X` to X and this form has no `-m`: the first token is `python`,
which counts as argus's own invocation. Thirtieth instance this session of
a mention read as a claim.

The fix is the rule generalised, not an exemption added: an interpreter is
never the owner of a flag, so `python <path>.py` belongs to that script
exactly as `python -m X` belongs to X. Adding `--check` to an exemption
list would have gone green in ten seconds and left the hole for the next
script.

Plant-tested four ways, and DESCRIBED rather than quoted, because the
first version of this paragraph quoted all four planted strings and made
the gate red three times over - an invented subcommand, two invented flags,
and a count. An entry documenting a plant test must not contain the plants:
writing the literal into a gated document IS the claim the plant was.
Thirty-first through thirty-third instance this session, in one paragraph,
and the check was right every time.

The two passing plants invoke another script through the interpreter, once
with `python` and once with `python3`, each with a flag of its own. The two
failing plants invent a flag after an argus invocation, once through
`python -m` and once through the console script directly - so both argus
entry points are covered and neither is excused by the interpreter rule.

### A silent fallback is how a check loses its sensitivity

Every Windows CI job failed the derived floor's negative test:

    have={'stylesheet lines': 509, 'css rules': 247, ...}
    assert {}      # nothing caught

And the test was RIGHT. Locally the same cut is caught - HEAD and the
working tree both measure 1030 stylesheet lines, the floors are 669 and
269, and a 521-line cut leaves 509 and 247, under both. On Windows the
floors could only have been the absolute ones, which means the HEAD copy
was never read and the scale silently degraded.

Nothing in the failure said that. The message named the measurements and
the floors and gave no hint that an input was missing, so it read as a
defect in the floor rather than as a missing scale - and the cause is still
not determined from here, because the instrument did not record it.

Three changes, and the third is the one that matters:

- `_LAST_HEAD_ERROR` records WHY the read returned nothing: a non-zero exit
  with git's stderr, an empty blob, a timeout, a path outside the repo.
  The next failure will name its cause instead of being inferred from a
  `have=` dict.
- Two plausible causes fixed on the way, both platform defaults rather than
  logic: `text=True` decodes with the platform's preferred encoding, which
  is cp1252 on Windows while this file carries Vietnamese comments, so the
  encoding is now explicit; and the 30-second timeout became 90, because a
  cold Windows runner's first git invocation is slow and a timeout here
  degrades the floor instead of failing.

  AND ONE OF THOSE TWO IS ELIMINATED BY THE FAILURE MODE, from evidence
  already in hand rather than from a Windows box. The failing version
  caught `(OSError, subprocess.SubprocessError)`, and a cp1252 decode
  raises `UnicodeDecodeError`, which is a `ValueError` and neither of
  those - so it would have PROPAGATED and produced a test error. What was
  observed is an AssertionError, meaning the helper returned an empty
  string quietly. The encoding was never the cause.

  That leaves three ways to return "" - git absent, a non-zero exit, or a
  timeout - and only the timeout was changed. CI is now 11 of 11 green
  including every Windows job, so either the timeout was it or the cause
  was transient. The symptom could not distinguish those; the exception
  hierarchy could, and it ruled out the hypothesis the symptom had made
  look most plausible.
- The negative test now SKIPS WITH THE REASON when the scale is degraded,
  the same shape `require_node` already uses in this file: a run that drops
  a proof says which one. With the floor at its absolute values a 521-line
  cut genuinely does clear it, so the assertion was correct and measured
  nothing.

AND A SKIP IS ALSO HOW A CHECK DISAPPEARS. If every run degraded, the suite
would be green, the floor would catch nothing, and the only evidence would
be a skipped test nobody reads. So the opposite direction is asserted too:
in a checkout where git works - every development run and every Linux CI
job - the scale MUST come from HEAD, and the failure prints why it did not.

Verified by substituting a failing HEAD read: the negative test skips
naming the reason, the degradation guard fails naming the reason, and with
HEAD readable both pass.

### An expired finding, published as current

Two audit findings verified by hand, both on the finding axis, both real.

A FINDING THE TARGET NO LONGER DOES REACHED ONLY report.md. Counted per
renderer:

    markdown  17 mentions    html  0    hackerone  0    sarif  0

So after `argus replay` established that the target no longer produces the
quoted bytes, the artifact submitted to a bug-bounty triager published the
finding unchanged, under `PROOF: PROVEN`, with no sign of it. Not a
fabricated finding - an EXPIRED one presented as current, which is
assertion-beyond-the-evidence one field over. The gap was mine, made an
hour earlier by adding the per-finding replay line to markdown alone.

All four now carry it: a badge on the bug-bounty artifact, a line in the
html verification box, and `argus-re-verified` plus `argus-replay-reason`
in SARIF so a machine consumer can tell the two apart. `inconclusive`
reports as `not_re_verified` rather than as reproduced, because the
question never reached the target - the same rule the coverage table and a
judge's failed call already follow. A failure outranks a later success on
every artifact.

AND THE HTML BLOCK WAS WIRED UNDER THE EXIT RATHER THAN INTO IT. The replay
line sat fifteen lines below an early return that fires when no judge
verdict exists, so a finding with a replay outcome and no judge took the
return and never reached it. That function is no longer "the judge box" -
it carries the second and third readings - and its exit now says so.

### A judge's lowering was a one-way door the upgrade branch did not know

`judge.apply_verdict` documents three one-way doors and writes
`severity_claimed` ONLY when it lowers a severity, so that key is the
reliable marker that a model from another family found a claim overstated.

`session.add_finding`'s upgrade branch wrote the caller's severity
unconditionally whenever the grade improved. So the sequence `argus run` ->
`argus judge` (critical -> low) -> `argus run --resume`, where a worker
collects the missing checks for the same bug, restored the severity the
judge had reduced. The invariant was enforced in judge.py and violated in
session.py, and the violating place is the one nobody looks at.

The fix respects the marker and nothing more: better evidence may still
RAISE a severity no judge has touched, which is what an upgrade is for, and
may still lower one further - one-way means one direction, not frozen.
Plant-tested in both directions, including the OVER-correction: restoring
the unconditional write fails one test and freezing the severity entirely
fails two.

Building the fixture took four attempts and the fourth was measured rather
than guessed. Reaching `proven` for sqli needs all of: a CONTROL exchange
cited beside the injection, because "a request to the same endpoint WITHOUT
a table in it is what separates a read from the page's own furniture"; the
table named in the request; the DBMS fingerprint in the EXCHANGE; and the
excerpt quoting THE ROWS - an excerpt carrying the fingerprint matches
`DBMS_RE` and is rejected as "an error or a refusal, not data". Reading the
verifier was faster than the three guesses before it.

AND THE SUBSTRING DEFECT RECURRED IN A SIBLING TEST. Adding the replay
absence to the html box broke `test_html_states_that_no_second_model_read_
the_evidence`, which asserted `"not performed" not in` - exactly the
assertion fixed in the markdown test an hour earlier, with the fix already
known. Thirty-fifth instance. The lesson is not "name the claim once": it
is that adding ANY second absence to a block invalidates every
bare-substring assertion about the first.

### A declared secret, verbatim in the artifact submitted outside

The most serious thing the audit found, reported as medium and measured as
worse. A run started with `--secret <value>` has that value redacted from a
newly recorded finding's prose and written VERBATIM into an upgraded one:

    created finding   title: sqli, logged in as •••redacted•••
    upgraded finding  title: sqli upgraded, cookie SuperSecret123

All three free-prose fields - title, description, remediation - and from
findings.json that reaches report.md, report.html, report-h1.html and
report.sarif, including the artifact a bug-bounty triager receives.

A FIXED DEFECT RETURNING THROUGH A SECOND DOOR. This leak had already been
found once and closed in the creation path, and the comment beside that
code records the measurement that produced the fix: "notes.md, agent.log
and transcript.jsonl were clean while findings.json carried it verbatim -
and findings.json is what report.md and summary.json are rendered from,
which are the files that get emailed and filed."

The upgrade path was missed, and the mechanism is structural rather than
careless: the redaction helper was defined INSIDE the creation branch,
below the upgrade branch, so the upgrade branch could not have called it
and wrote `str(title or "").strip()` itself. One concept, two definitions,
and the second carried no redaction at all.

The helper now sits above both branches. Verified by construction before
and after: the same sequence that produced `cookie SuperSecret123` now
produces `cookie •••redacted•••`, the upgrade still reaches `proven`, and
`json.dumps(findings)` contains none of it.

Asserted on BOTH paths, because asserting one is what let it come back.
Plant-tested three ways - a raw title on the upgrade path, a raw title on
the creation path, and a raw description on the upgrade path - each fails.

### Three of the nine ways a record fails, in the command that writes

`argus judge` tested `chained`, `tail_truncated` and `bad_lines` - three of
the nine flags `verify_transcript` returns - and `artifact_mismatch` was
not among them. So a session whose report.md, meta.json, notes.md or
agent.log had been edited after sealing passed silently, had a
cross-verification verdict written into findings.json, and was RE-SEALED
over the edit. The tampering ended up covered by a fresh seal with nothing
saying so.

Measured by construction on a copy of `docs/sample-session` with one line
appended to report.md:

    artifact_mismatch   set
    chain_ok            False   (the shared definition refuses it)
    judge's condition   True    (it admitted it)

`chain_ok` is the single definition of a trustworthy record and already had
two callers. Five commands call `verify_transcript` and only two consulted
it - one concept with four definitions, and the one that admitted a
mismatch was the one that WRITES.

THE LINE IS WHETHER A COMMAND AMENDS OR RENDERS. `argus report` re-seals
too, and its handling was already honest: warn, proceed, and record
`reseal_over_mismatch` in the chain so the digests after that point are
known to cover edited bytes. `argus findings` only reads, so a warning is
enough. `argus judge` now does what report does rather than refusing,
because warning is this command's existing contract - `argus replay`
refuses because it had no contract to keep.

AND A PLANT SHOWED THE TESTS HELD THE LOGIC AND NOT THE WIRING. Two tests
assert the relation between the real lists and the construction of the
mismatch, and BOTH PASSED with the command's own condition reverted to the
narrow three. Nothing held that `argus judge` consults `chain_ok` at all.

The third test drives `cli.main(["judge", ...])` with no credential in the
environment - the warning is emitted 57 lines into the command and the key
is not needed until line 141 - and asserts both that it fires and that it
NAMES the flag. "Something is wrong" is not something an operator can act
on; a session edited after sealing is a different problem from a broken
chain. Re-planting the reverted condition now fails, where it passed
before.

### A CWE the finding will not carry

`_CWE` is keyed on the category name a model writes, and `add_finding`
canonicalises before looking it up - so a name that is an ALIAS of another
class inherits that class's identifier and its own entry is never read.

Measured: `rfi` mapped to CWE-98, PHP remote file inclusion, while
`proof.canonical("rfi")` is `lfi`, whose identifier is CWE-22, path
traversal. An RFI finding carried CWE-22 and the table said CWE-98.

Removed rather than corrected, because the entry was not a wrong value but
a statement about behaviour that does not happen - and a reader of the
table concludes a finding carries what it says. The taxonomy question,
whether `rfi` should be its own class with its own requirement, belongs to
whoever owns the matrix and is not answered here. What is removed is the
false claim about it.

Asserted as the relation rather than the case: no `_CWE` entry may state an
identifier that disagrees with the one its canonical class supplies. One
occupant today, and the next alias added with its own CWE will fail it.

WHAT IS DELIBERATELY NOT CHANGED, and the distinction matters.
`session-fixation`, `mfa-bypass` and `auth-bypass` are aliases of `jwt` and
therefore carry CWE-347, improper verification of a cryptographic
signature. A session-fixation finding is conventionally CWE-384 and an MFA
bypass CWE-287 or CWE-304. But the matrix treats six names as that one
class, with one requirement, on purpose - `jwt` has six aliases, `lfi` has
seven, `rce` has seven - so this is a question about the matrix's taxonomy
and not a mapping bug. Changing which weaknesses count as one class
changes what the gate proves, and that is not a decision to make from a
CWE table. Reported rather than altered.

### A dispute attributed to the model that agreed

`apply_verdict` keeps every verdict in `judges`, overwrites `judge` with
the newest, and sets `disputed` as a one-way flag. So judge #1 disputing
and judge #2 agreeing leaves `disputed` true and `judge` pointing at the
one that AGREED.

`report.html` read `judge` alone. Measured on that finding, against
markdown on the same one:

    html       DISPUTED by cross-verification (other-2)   no reason shown
    markdown   DISPUTED by cross-verification (other-1) - an error is not a row

So a reader of the html report would go to other-2 to ask about a dispute
it never raised. `apply_verdict`'s own comment records this hazard being
found and fixed - "a report read 'Cross-verification: agreed' over a
finding whose `disputed` flag was still set, telling the reader the
opposite of the record" - and it was fixed for markdown and missed here.
The third fixed defect today surviving in a sibling renderer.

html now reads the history and prefers the first dispute, and treats a
dispute in the history as a dispute even when the flag is absent, because
the history is the record and the flag is a convenience.

AND THE TEST OVER-ASSERTED THREE TIMES, each one broader than the claim.
First it required the agreeing model's name to be absent from the whole
document - but markdown deliberately prints a roll-call, "(2 judges read
this evidence: other-1 disputed, other-2 agreed)", precisely so a later
agreement cannot present itself as the whole story. Mentioning the
agreeing model is correct; attributing the dispute to it is not. Then the
filter caught every line containing "disput", which includes that
roll-call. Only the third filter names the attribution line itself.

The same error as the checks this session keeps fixing, in a test about
them: asserting the presence of a string rather than the form of the
claim.

### Two high-severity audit claims, refuted by the same property

Both said a finding's grade can rest on bytes the artifact does not keep,
so `argus verify` would report TAMPERED on a session nobody edited - once
through the 2000-character excerpt cap, once through `BODY_CAP`. Neither is
reachable, and the reason is one property neither verifier saw.

Measured against a real 210KB response with the proving token placed past
the cap:

    BODY_CAP             200,000
    send() returned       12,000 bytes   token absent
    transcript stored    200,000 bytes   token absent, truncated=True
    add_finding          REFUSED: not a verbatim substring

THE VERBATIM CHECK RUNS AGAINST THE STORED ENTRY, not against what the live
response contained. So an excerpt the record does not hold cannot be cited
in the first place: the same universal check that stops a fabricated
excerpt stops this. And the excerpt-cap claim fell the same way - across
all 29 classes with the token past the cap, two read different checks and
no class changes its grade, while the longest excerpt across 22 real
findings is 40 characters.

Asserted now rather than relied on, including the direction that keeps the
refusal meaningful: a quote from WITHIN the kept bytes is still accepted,
so the refusal is about the record and not about size.

Worth separating from the fixes, because the audit was useful and this is
what it could not do. Every structural claim its dimensions made was
correct - the grade is computed before the truncation, the cap does cut the
body, the entries do exist. What it could not establish is whether any of
that reaches a finding, because reaching a finding requires knowing what
the recorder keeps and what 22 real findings actually look like. Code tells
you the first; only evidence tells you the second.

### The Target line named the directory, not the target

The report's Target line - its claim about WHAT WAS TESTED, which in a
system whose premise is authorised testing is the authorisation boundary -
read `session.dir.name.split('-', 2)[-1]`. Measured across every sealed
session in this repository, 0 of 5 rendered correctly:

    directory          meta.json                   rendered
    sample-session     http://127.0.0.1:43673      "session"
    argus-lab          http://192.168.223.221:8777 "lab"
    argus-lab-team     http://192.168.223.221:8777 "team"
    dvwa               http://192.168.223.221:8081 "dvwa"
    bwapp              http://192.168.223.221:8080 "bwapp"

The two that look right drop the scheme and the port. It was correct only
by coincidence of the live naming convention, and a directory that is
renamed, copied or moved names something that was never tested.

AND THE LAST TWO ROWS MAKE IT STRUCTURAL, not cosmetic. `argus-lab` and
`argus-lab-team` are two runs against ONE target. The name-split renders
them as "lab" and "team", so the defect does not merely mangle a label - it
MANUFACTURES A DISTINCTION THE EVIDENCE DOES NOT CONTAIN, presenting one
target as two. The mapping is not one-to-one, so a directory name cannot be
the target even in principle. Asserted in that form: two sessions sharing a
recorded target must render one Target line.

Now read from `meta.json`, which holds it in all five, with the derivation
kept as a last resort and MARKED as derived - a reader must be able to tell
a recorded target from an inferred one, which is the same rule as every
other absence in these reports.

FOUND BY RE-RENDERING THE COMMITTED REFERENCE, not by reading the renderer,
and that is the whole lesson. The bug is invisible while the directory
still carries the host. It surfaced only because re-rendering a checked-in
example puts the session in a directory with a different name - and the
first attempt at that re-render was worse: rendering with a hand-built
Config replaced the recorded `scripted-demo` with the configured default,
`claude-sonnet-5-5`, a model that never ran. Three recorded facts
overwritten by defaults, in a reference artifact, by the step meant to fix
one of them. The renderer is only as honest as what is handed to it.

The committed example is therefore LEFT AS IT WAS. It is a sealed
historical artifact; re-rendering it would require reconstructing its
original config exactly, and getting that wrong writes a false model name
into the repository's own evidence. Every report rendered from here on shows
the event citation and the recorded target.

### A cited event rendered as an empty box

`docs/sample-session/report.html` showed, for the proven jwt finding's cited
event r62:

    Transcript r62:   ->
    <pre></pre>

The citation was built unconditionally from `request.method`, `request.url`,
`response.status` and `response.body`, and an event entry has none of those:
r62 is a `jwt_forge` event carrying `claims_set`, `payload_used`, `alg_in`
and a hashed token. So the operator-facing report rendered an empty box for
evidence its own narrative describes two lines below - "r62 set
['role','user'], echoed 'admin'".

`report-h1.html` already had the honest shape, printing "r62 is a jwt_forge
event, which carries no request - its output is evidence but it is not a
step". So this renderer was the one missing it: the fourth fixed-elsewhere
defect found in a sibling renderer in one session.

Extracted as `_citation` rather than fixed inline, because the inline
comprehension could only be tested by rendering a whole report. Bookkeeping
is excluded - `chain` is a digest and inviting a reader to treat it as part
of the proof is its own hazard - and an entry that really carries nothing
says so.

### A header quoted the way HTTP writes it could not be cited

The recorded header keys are lowercased, so a finding in one of the three
classes whose proof IS a header name - CRLF injection, security headers,
server disclosure - could only cite it if the quote happened to be
lowercased too. Measured, each in a fresh session:

    x-powered-by: PHP/5.6.40        accepted
    X-Powered-By: PHP/5.6.40        REFUSED
    Server: Apache/2.4.49           REFUSED
    PHP/5.6.40                      accepted
    uid=0(root) gid=0 (fabricated)  refused

The refused forms are how the header appears on the wire, in `curl -i`, and
in every browser's network panel. The refusal says the excerpt "is not a
verbatim substring of any cited response", which tells an agent that its
REAL evidence is fabricated - the direction of error this repository treats
as the one that matters. The comment on that code said both shapes were
included "so either quotation form matches", which was true of
JSON-versus-wire and not of the casing.

Fixed by ADDING parts, each still exact-matched, so a true finding may
quote more and a fabricated one gains nothing.

AND THE OVER-WIDE FIX PASSED THE TEST WRITTEN TO CATCH IT. Planting
`excerpt.lower() in part.lower()` left all 30 green: the fabricated list
held only strings differing in CONTENT, while the docstring named
`UID=0(ROOT)` as the hazard. The comment stated the invariant and the test
did not hold it - the same defect this session keeps fixing, in a test
written to guard against it. Three case-variants of recorded bytes added,
and the plant is red.

ALSO ASSERTED: THE TWO GATES AGREE. `add_finding` decides what may be
recorded, `findings_bad` decides what still verifies on re-read, and a
disagreement either way is a defect - accept-then-refuse makes `argus
verify` report a tampered finding on a session nobody edited, and
refuse-then-accept makes the gate narrower than the verifier. 7 forms,
identical before and after the fix, now held by the relation rather than by
whichever test covers one side.

AND THE MEASUREMENT TOOK FIVE WRONG HARNESSES. `Set-Cookie` was picked
first - a credential header, redacted by design - and its refusal read as
"headers cannot be cited at all". Then three wrong paths
(`findings.json`, `transcript.jsonl`, `findings_bad`'s arity), and finally
a hand-built finding dict with no `severity`, which `findings_bad` requires:
every row came back refused, including a quote verbatim in the body.

That impossible row is what saved the measurement. A result that cannot be
wrong and is wrong anyway is evidence against the instrument, not against
the subject - and reading only the header rows would have reported an
asymmetry between the two gates that does not exist, which would have
sounded more serious than the real finding.

### A confident negative from a clock, in two probes, now one function

`probe_ssrf_oob` and the stored-XSS collector both slept the whole settle
window and then checked for a callback ONCE. A callback arriving at the
window plus anything was missed, and the probe reported that the target did
not call back - so a real finding was not found.

The XSS site had a comment four lines above it naming that exact failure:
"the probe then reported 'reflected but did not execute' about a page it had
never actually visited, which is the worst shape of wrong: a confident
negative". It then produced the same confident negative from a clock instead
of from a wrong URL. SETTLE_SECONDS is 3.0, so a page whose payload fires on
a timer, an animation frame or a deferred script had one chance to be inside
it.

ONE DEFINITION NOW, `wait_for_callback`, because the fix existed in one
probe and not the other - the fifth time in this session that a defect was
already fixed on a sibling path. Three properties, each asserted:

    a hit inside the window is SEEN, whenever it arrives
    a hit arriving early is acted on early, not waited out
    the window is still a CEILING when nothing calls back

The third is the one a fix must not trade away, or this is a timeout
increase wearing a different name. And it is testable without a browser,
which the XSS path is not - so extracting it is what made the stored-XSS
behaviour coverable at all.

AND THE CEILING TEST HUNG INSTEAD OF FAILING. Planting an unbounded wait
left the call never returning, so the assertion that computed the elapsed
time was never reached: the test blocked rather than failed, which in CI
burns the job's whole timeout and names nothing. The check stated the bound
and did not enforce it - the same defect as the rest of this session, one
level up. A thread with a join timeout, stdlib only, turns it back into a
failure: 1 failed in five seconds instead of a hang.

### A gate run that was falsely RED, from the same mistake as the falsely green one

Gate 101 reported three failures in `test_proof.py` - the crlf control, the
upload canary, the race baseline - with assertion messages quoting source
lines from the wrong functions entirely:

    assert 'clean control' in '        "verdict": verdict,\n'
    assert '_marker("argusupl")' in '   "similarity_to_base": fsim,\n'

Those tests read a probe's source with `inspect.getsource`, which reads the
CURRENT file from disk using the line number recorded when the module was
imported. `probes.py` was edited while that pytest was running - 48 lines
inserted for `wait_for_callback` - so every function after the insertion
point reported source belonging to a different one. All three pass on the
settled tree.

THE SAME MISTAKE AS THE FALSELY GREEN RUN, and the lesson is sharper for it.
Earlier in this session a gate reported 164/164 about a tree state that
never existed, because pytest and selftest ran against different versions of
the files. The discipline taken from that was: never edit the tree while a
gate runs. This is that rule broken again, and this time it produced a red
run instead of a green one.

Red is the gentler outcome ONLY BY LUCK. The two runs are the same error,
and a falsely red gate costs a wasted investigation while a falsely green
one ships a defect - so the direction the coin lands is not a property of
the mistake. The rule is not "do not break a gate", it is "a gate run is a
statement about one tree state", and an edit mid-run makes it a statement
about none.

### Four more audit claims, refuted by reconstruction

A GRADE CORRECTION LEAVING THE PROOF BLOCK CONTRADICTORY. Planted: the
sample session's F03, graded `candidate` by the matrix, edited in
findings.json to claim `proven`. The re-render warns, corrects, and the
block is wholly consistent with the corrected grade:

    - **Category:** xss - **proof: candidate**
    - [x] payload reflected unencoded into HTML - '<>"' survived into r19
    - [ ] a real browser executed it - no callback carrying a probe nonce

It names the requirement, shows the unmet item unchecked, and gives the
reason. Both the metadata line and the proof grade carry the correction.

A WEBSOCKET PROBE WITH AN 8-SECOND DEADLINE. `probe_websocket` is 64 lines
and contains no `settimeout`, no `recv`, no `deadline` and no sleep; it
calls one helper, `_marker`. There is no raw socket anywhere in
`probes.py`, and the only remaining numeric sleeps in the file are 0.05
poll intervals.

A TE.CL PROBE RESTING ON A 3-SECOND READ. `probe_smuggle` has no timing
line at all, and it is BETTER than the claim assumed: it proves a desync by
CONTENT, not by a clock - `s2["status"] >= 400 and _SMUGGLE_G.search(body)`,
the target echoing back the stray `G` that poisoned the following request.
A witness, not a timeout. And three distinct `inconclusive` verdicts
separate "the connection did not survive", "the second request failed after
the ambiguous one - could be a desync or just a reset", and "no queued
response", so it refuses to call a desync on ambiguous evidence. Timing-
based smuggling detection is exactly what produces false positives on a
slow network, and this probe does not do it.

A HEADER-QUOTED EXCERPT REPORTED AS NOT FOUND IN THE RESPONSE.
`hackerone.py` says "shown from the start of the body: the quoted excerpt
was not found in it verbatim", where "it" is the body - which is accurate.
The claim misquoted the note as speaking about the response.

RUNNING TALLY ON THE AUDIT: nine real defects fixed, six claims refuted by
reconstruction, one taxonomy decision reported rather than taken. Every
structural statement its dimensions made was correct; what it could not
establish was whether any of it reaches a finding, which needs the recorder
and 22 real findings rather than the code.

### A branch of the gate that had never caught anything

The check that every `argus <subcommand>` named in the docs is real has two
branches: prose backticks, and fenced code blocks. Its own comment on the
second says "inside a fenced shell block the command often has no backticks
and no `python -m` prefix, which is where most examples live".

Measured: that branch found ZERO subcommands across every gated document.

Its fence pattern was ```(?:bash|sh|console)? which does not match `json`,
and an unmatched OPENING fence makes the next closing ``` read as an
opening - inverting every region after it, so real code becomes invisible
and the prose between blocks becomes "block content". README.md has 20
fences of which 2 are `json`; docs/USAGE.md 42 of which 2 are `json`.

So a fabricated subcommand inside a code block - THE FORM A READER COPIES
AND RUNS - passed the gate, while the same fabrication in prose backticks
was caught. The whole session has been fixing the opposite direction, a
checker reading a MENTION as a CLAIM; this is a checker missing a real
claim in the form that most looks like one.

Found by planting an invented subcommand name in a fenced block and
watching the gate pass. Not by reading the pattern - the pattern looks correct, and the
inversion only happens in the presence of a tag it does not list.

AND THE FIX EXPOSED A FALSE POSITIVE THE DEAD BRANCH HAD BEEN HIDING.
docs/USAGE.md prints "  argus called proven    : 2 (rce, sqli)" - a report
line meaning "argus called [these] proven". With `^\s*` that reads as a
claim that `called` is a subcommand. The discriminator, measured over the
real corpus rather than chosen: commands sit at column 0 or after a `$ `
prompt, output is indented. Indentation-allowed finds ['called',
'groundtruth']; column-0 finds ['groundtruth'], which is the real one, and
a planted fabrication at column 0 is still caught.

ASSERTED AS THE YIELD, not as the pattern. A branch whose scan returns
nothing is indistinguishable from one that works, and only the count says
which: `test_the_fenced_block_scan_actually_finds_something` fails when it
covers nothing. Both plants are caught by selftest itself as well - and
reverting the fence pattern makes the REVERSE check fail, because
`groundtruth` then appears in no gated document.

AND THE SEVENTH WRONG INSTRUMENT IN THIS SESSION produced a finding that
does not exist. The first plant matrix decided its verdict with
`grep -qE "^16[0-9]/16[0-9] passed"`, which matches `163/164` as well as
`164/164` - so a FAILING run was recorded as "missed". That table reported
two holes. Re-measured on the exit code, there is one: the flag check works
in both prose and fenced form, and those rows were the instrument, not the
subject. Same shape as `grep -c` versus `grep -cx` earlier - a pattern
matching more than intended - and this time it invented a defect rather
than hiding one.

### And the note explaining the fix broke the gate the fix had repaired

Gate 104 came back red on one line: the subcommand check naming an invented
command in a gated document. The document was this CHANGELOG, and the
invented command was in the paragraph above describing how the hole was
found - written inside backticks, where the prose branch of that same check
reads it as a claim.

FOURTH TIME IN THIS SESSION, and the durable fix was already written down
here: describe rather than quote. Three earlier CHANGELOG paragraphs did
this, each describing a planted shape by reproducing it, and the entry
recording that lesson is a few hundred lines above the one that repeated
it.

What makes this one different from the first three is the ordering. The
quote was written into the note explaining a fix to the OTHER branch of the
same check - so the prose branch, working correctly, failed the document
that had just restored the fenced branch. The gate was right both times and
the two halves disagreed about one string, which is as clear a statement as
this check can make: an example and an assertion are the same bytes, and
only the form around them says which one it is.

### A poll that read a file mid-write, red on Windows only

CI #590 went red on one of eleven jobs, windows-latest/3.10:

    tests/test_web.py:439: in a condition that parses the run's state
        file, read through pathlib with an explicit encoding
    E   PermissionError: [Errno 13] Permission denied: 'C:\\Users\\...'

The condition READS a file the worker thread is WRITING. On POSIX a reader
may open a file mid-write and a rename is atomic, so the poll sees either
the old content or the new one. On Windows the file is briefly unopenable -
during the write, and during the replace that puts the new content in
place - and the read raises.

DESCRIBED, NOT QUOTED, and this is the FIFTH instance in one session - the
second with this exact identifier. Quoting the failing line reproduced a
pathlib method name that the tool check reads as a claim about an argus
tool. The right fix was settled mid-session and written down: 31 argus
tools ARE named with parentheses in the docs, so narrowing the checker
would drop half the tool table's coverage, which means the prose is what
changes. Knowing which string is the landmine is evidently not the same as
not typing it.

"The file is momentarily unreadable" is not "the condition is false". It is
the same not-yet the loop exists to wait through, which makes this the same
shape as the callback polling fixed in `probes.py` an hour earlier: a check
treating an in-progress state as a verdict. Three instances of that shape
in one session, in three unrelated files.

An OSError is now swallowed while there is time left and RE-RAISED if the
deadline passes without one clean evaluation, because a persistent
permission problem must arrive as itself rather than as a confusing
assertion about None further up the test. Both directions are planted:
removing the tolerance fails, and swallowing the persistent error fails.

Reproduced without Windows, by planting the transient directly - two raises
then a value - which is the only honest way to test it from here. The fix
is verified on POSIX and its platform-specific half is verified by CI.

### A universal coverage claim, four lines from the count that refutes it

Raised against the console's hero line by the session that owns that file,
and flagged rather than edited because it is product copy. The same shape
turned out to be in the REPORT, which is this side's to fix.

Planted a row with no `grade` key in the sample session and re-rendered.
The report printed, four lines apart:

    | **ungraded** | 1 | recorded before grading existed |
    Every finding is graded against the proof requirement for its class

`ungraded` is a real bucket in `_GRADE_MEANING` - "recorded before grading
existed" - so a resumed session, or a findings.json written by an older
version, holds rows the matrix never graded. The sentence now carries the
count: "5 of 6 findings are graded ... and 1 carries no grade at all -
counted as `ungraded` above, never as a verdict about its evidence", and it
stays universal when every row is graded, because replacing a true claim
with a count makes it read as a qualified one.

A NUMBER CANNOT QUIETLY BECOME FALSE, which is the property this whole
system is built to have. That is the argument for stating one, and it is
also what makes the two NEIGHBOURING claims worth leaving alone. Both are
about CITATION, and both are enforced: `add_finding` refuses an excerpt
that is not a verbatim substring of a cited response, and `findings_bad`
re-validates every one on re-read. Grading is the one that can be absent,
so it is the only sentence that needed changing. Planted in that direction
too: weakening a citation claim to "some" fails.

The console's line remains the user's call, with the same recommendation -
state the number.

### The orphan sweep found no orphan, and two broken instruments

Swept the finding axis - the evidence store, the matrix, the judge, the
replay, the decision rules - for top-level functions nothing calls. Three
candidates, and all three are explained:

    decide.py  _reverified            defined once, called once
    replay.py  _entry_response_body   defined once, called once
    session.py looks_like_ci          NOT OURS

A clean negative on a dimension that produced three real orphans earlier in
this session, so the result is worth stating rather than quietly dropping.

THE THIRD CANDIDATE DOES NOT EXIST IN THIS PROJECT. The sweep filtered
candidate files by BASENAME, and three things in this checkout answer to
the basename of a package module without being it: a gitignored local build
tree measured 126 lines behind the real evidence store, the virtualenvs
under `challenges/` with their own vendored libraries, and a deliberate
shim for the bundled lab. The sweep parsed a vendored HTTP-session module
as if it were ours.

AND THE CHECK OF THAT REPORTED ZERO FOR A STRING THAT EXISTS. A recursive
text search for the same function name found nothing anywhere, which is
what nearly settled it as a hallucinated scan result. Reading the one file
directly found two occurrences. Two instruments disagreeing in opposite
directions on one question, and the subject was fine both times.

Ninth wrong instrument in this session. The pattern across all nine is the
same and it is the only durable lesson here: a surprising measurement is
evidence about the instrument first. Written into AGENTS.md as a rule for
the next sweep - measure the package by path, anchored under the package
directory, never by filename.

### The three layers, run end to end against a live target

`argus replay` had never been run against a running target - only against
unit fixtures and a loopback server inside the suite. Started the bundled
lab on loopback, ran the scripted engagement against it, and replayed the
findings it produced:

    F01..F05  reproduced     the target returned the quoted bytes again (HTTP 200)
    F06       inconclusive   the recorded request carried authorization and
                             the transcript stores the hash, not the value

    1 inconclusive, 5 reproduced

The inconclusive one is the designed behaviour, measured rather than
argued: F06 is the jwt finding whose request carried a credential header,
the transcript keeps only its digest, so the replay SAYS IT COULD NOT ASK
instead of reporting that the finding did not hold. That is the whole
reason `not_reproduced` and `inconclusive` are separate outcomes, and this
is the first time the distinction has been exercised outside a test.

AND THE DELIVERABLE STATES ITS OWN COVERAGE:

    | graded by the matrix           | 6/6 | did the target produce the quoted bytes |
    | read by a second model         | 0/6 | do those bytes demonstrate the class claimed |
    | re-verified against the target | 5/6 | does the target still do it |

with an explicit line that no finding here has been read by a model from
another family, naming the command that would do it. Three questions, three
answers, and the zero is printed rather than omitted.

`argus verify` is still clean afterwards - 73 chained entries anchored to
summary.json, 6 findings re-validated, artifacts sealed - which confirms on
a live session that replaying re-renders and re-seals rather than leaving
the artifact digests behind, the defect that made the first version of this
command break the seal of every session it touched.

AND A TENTH WRONG INSTRUMENT, immediately. A first pass searched the report
for the absence wording and found one line, which read as "the five
reproduced findings print nothing". They print the success wording, which is
a different string. A pattern narrower than the thing it looks for, for the
second time today.

### The documented remedy, exercised: a supplied credential closes the gap

The live end-to-end run left one finding `inconclusive` - its recorded
request carried a credential header and the transcript keeps only the
digest, so the replay could not ask. The reason text names the remedy: pass
the credential at replay time. That path had never been run against a live
target either.

Minted the same credential the engagement forged, confirmed the target
accepts it, and replayed that one finding with it supplied:

    without a credential   inconclusive   the question did not reach the target
    with one supplied      reproduced     the target returned the quoted bytes again

So the coverage table reads 6/6 re-verified, and the loop the module's
docstring describes is closed by measurement rather than by assertion.

THREE PROPERTIES HELD, each of which had only unit coverage before:

The history keeps BOTH attempts - inconclusive then reproduced - so a
reader can see that the first answer was "could not ask" and not "did not
hold". `replay_failed` stays false, because an inconclusive is not a
failure to clear.

`supplied_headers` reads what the client will actually put on the wire.
This is the shape the first version of that function got wrong: it read a
public attribute that does not exist, and therefore reported every supplied
credential as missing. A test holds the private name for exactly this
reason, and this run is the first time the correct reading has been
exercised against a target that checks the credential.

`argus verify` is clean after two replays of the same session - 76 chained
entries anchored to summary.json, 6 findings re-validated - so the
re-render-and-re-seal holds across repeated runs, not just the first.

### What the judge is and is not shown, measured on a live case file

The judge layer cannot be run end to end from here: the provider refuses to
send a credential to a non-TLS endpoint, so there is no way to point it at a
local stub without weakening a guard that exists for exactly the reason it
says. That refusal is correct and stays.

What CAN be exercised is everything up to the network call, and that is
where the design lives. Ran the dry run against the live session - 8892
bytes, 219 lines - and measured what reaches the second model:

    first model's title            SHOWN
    class, url, severity claimed   SHOWN
    grade from the proof matrix    SHOWN
    proof requirement for class    SHOWN
    raw request/response records   SHOWN
    first model's description       absent
    first model's remediation       absent
    the agent's run summary         absent

A HYPOTHESIS OF MINE, REFUTED BY READING THE PROMPT. Showing the grade
looked like anchoring: a second reader primed with "the matrix says proven"
is a weaker check than one asked blind. The prompt settles it, and each
disclosure is load-bearing:

- "You are NOT shown the first model's reasoning, and you should not try to
  reconstruct it" - which the measurement above confirms rather than
  assumes.
- "Answer this and nothing else: does the evidence, ON ITS OWN, establish
  the claim the finding makes?"
- The severity is shown because the judge is told to dispute it when "the
  severity is not defensible from the evidence". It is the claim under test,
  not a hint.
- The grade is shown because the judge "cannot promote a finding" and is
  told that if the evidence is STRONGER than the grade says, to say so in
  prose - so the grade defines the one-way door rather than the answer.

The residual is real but is a research question, not a defect: showing a
verdict creates some agreement prior, and the only way to size it is to run
both forms against real models and compare dispute rates. That needs an
endpoint, and it would measure models rather than this code.

Recorded because the measurement is the useful part, and now held by a
test rather than by a docstring: planting the description and the
remediation into the case file fails, and so does planting the agent's run
summary.

AND THE REQUIREMENT COMES FROM THE MATRIX, NOT FROM THE FINDING, which is
stronger than it looks and was found by the test failing. The first version
of this test passed its own requirement text in the finding and asserted it
appeared; it did not, because the case file looks the requirement up by
class. So a tampered findings.json cannot soften the bar it is judged
against - asserted now by planting "any 200 response will do" as a
finding's own requirement and requiring the real one to appear instead.

### The vacuous-truth trap in the grader, and the invariant that has no occupant

Asked the question the supervisor's MITRE point implies: does every class's
proof requirement demand evidence of the WEAKNESS, or only of a symptom -
which means, does each one require a control as well as an artifact?

THE FIRST INSTRUMENT WAS USELESS, and that is the finding about method.
A keyword search over the requirement prose reported 16 of 29 classes
missing a control, including sqli, rce, xss and idor, which plainly have
one. Controls are written in each class's own language: "the rows are not
what the page serves anyway", "another credential refused on the same
endpoint", "a nonce that was never sent". A word list cannot see them.
Thirteenth wrong instrument in this session, same shape as the rest - a
pattern narrower than the concept.

THE MEASURE THAT DOES NOT DEPEND ON VOCABULARY is the check count, since a
class with one required check cannot hold both an artifact and a control:

    four required checks   5 of them
    three                  7
    two                    16
    none                   1   <- dos, and it is the only REFUSED class

DESCRIBED, NOT TABULATED, and the first version of that table broke the
gate: the class-count check reads a number followed by the plural of the
word "class" as a claim about how many of them exist, so a distribution
tabulated in that form reads as several competing claims about the total.

Sixth time in this session that a write-up broke the gate it was
describing, and the first where the reproduced thing was a NUMBER rather
than a name. THEN THE PARAGRAPH EXPLAINING THAT broke it again, by
tabulating the offending form inside quotation marks to show what not to
write - in the same sentence that states the rule "anything a gate scans
for is unsafe to reproduce, whatever its type". Seventh instance, inside
the explanation of the sixth.

There is no clever version of this. The only form that survives is to
describe the shape in words and never to lay it out.

So 28 of 29 are structurally capable of an asymmetry, and the 29th cannot
be proven at all because policy says the proof is the damage.
`add_finding` refuses that class outright before grading is reached.

AND THE GRADER ALREADY GUARDS THE TRAP THAT ZERO CHECKS OPENS. `_grade`
reads `if required and all(name in passed for name in required)`. Without
the leading `required and`, the expression is `all(... for ... in ())`,
which is True - so a class with an empty requirement would grade EVERY
record `proven`, including a record holding nothing. Confirmed by removing
the guard: the test goes red.

TWO LISTS, ONE CONCEPT, asserted between them: "cannot be proven" and "is
refused" must name the same set. A checkless class that is not refused
would be offered to an agent as something to prove and could never reach
`proven`; a refused class with checks would imply it can be proven while
policy says otherwise. Planted both directions.

The invariant has no occupant today, which is the reason to assert it now
rather than later - the next class added with no checks is the one it is
for, and nobody sees a vacuous truth when it breaks.

### The de facto cap is disclosed, and the eighth hypothesis of mine refuted

Swept the last proof-matrix dimension reachable from here: classes that
cannot reach `proven`. No class carries a ceiling - which confirms the
earlier sweep that emptied that list - but one needs an external tool, and
that is a cap the ceiling field cannot see. On a machine without it, the
second required check for that class can never pass, so every finding of
that class stays a candidate.

The hypothesis was that a reader could not tell two very different
situations apart: the browser ran and nothing executed, which is evidence
AGAINST the finding, versus there was no browser, which is a missing
capability. Those are the same distinction as `not_reproduced` against
`inconclusive`, and getting them confused is how a real finding looks like
a refuted one.

Measured on the live session, the report already says all of it: that
execution is not shown because the engagement had no browser and the class
therefore stays a candidate; that reflection is visible in the bytes while
execution is not; that the tool is not on PATH; that it is an external tool
like the scanners; and how to install it or point at a local copy.

So the cap is fully disclosed, in the one place where a missing capability
could otherwise read as a negative result. Eighth refutation in this
session, and the fourth of a hypothesis of mine rather than an audit's.

Worth recording as a negative result for the same reason as the orphan
sweep: a dimension that comes back clean is information, and leaving it
unwritten makes the next sweep pay for it again.

### The three layers were absent from the document that exists to list them

`docs/VERIFICATION.md` tells a reader how to re-verify everything this
system claims. Measured: it mentioned the proof matrix, the cross-read and
the re-verification layer zero times each. The whole subject of this
session was missing from the one document a reviewer reads.

Added in the file's own shape - a property, where it is enforced, and the
test that proves it - for twelve properties across the three layers, plus
the end-to-end run against the bundled lab and the explicit note that the
cross-read column reads zero without a model endpoint and says so rather
than being omitted.

AND I INVENTED FOUR TEST NAMES, which is a different mistake from the seven
before it. The earlier seven reproduced a string a gate scans for; this one
asserted that four tests exist when they do not - in a document whose claim
is that it names only things that exist. Writing from memory of what the
tests "must" be called produced four plausible names, and the gate named
all four.

That is the error this system is built to prevent, made by its author in
its own documentation. The mechanism is identical to the one the proof
matrix exists for: a claim that sounds right, written by something that
believed it, with nothing behind it. The difference is only that a test
name has a gate behind it and a finding has a matrix - and both were
needed, by the same person, on the same day.

Eighth write-up failure, and the first that was a fabrication rather than a
quotation.

### Two refutations redone by reconstruction, and the worst near-miss of the session

Two timing claims were refuted earlier by READING the code - counting lines
and searching for socket calls - in a session whose whole lesson is that
reading is weaker than running. Redone against the live lab:

    the smuggling probe      0.02s total
    the websocket probe      0.00s and 0.03s

No deadline, no settle window, no timing dependence in either. The
smuggling probe returned `inconclusive` with the honest reason - the second
request failed after the ambiguous one, which could be a desync or just a
dropped connection - so it refuses to name a desync on ambiguous evidence,
which is the property that matters and which reading only suggested.

AND THE WEBSOCKET PROBE IS RIGOROUS IN THE WAY THIS SYSTEM IS SUPPOSED TO
BE. Its verdict rests on a round trip, not a status: it sends a foreign
Origin, gets the upgrade, sends a canary it minted, and requires the target
to ECHO THAT CANARY BACK. The recorded result carries the origin it sent,
the canary, and the reply containing it. It does not ask the socket whether
it opened.

THE NEAR-MISS, and it is the most dangerous mistake I made today. Running
that probe against the lab's socket endpoint, I read its verdict as a FALSE
POSITIVE on a path that does not exist - because a manual check of that
path had printed nothing. It printed nothing because the check lacked a
time limit and the surrounding timeout killed it while the upgraded
connection stayed open. The empty output was the instrument, not the
target. The endpoint exists, the lab's own route list documents it as
returning an upgrade, and a check with a time limit shows the upgrade
immediately.

So the sequence was: assert a false positive, in the system built to
prevent false positives, on the strength of an empty result from a tool
used wrongly. Fourteenth wrong instrument in this session and the first
that would have produced a retraction of a true finding - symmetrical to
the fabricated test names an hour earlier, and the same mechanism: a
confident claim with nothing under it.

What caught it was re-measuring with a bounded request and reading the
target's own documentation of its routes. Not scepticism in the abstract -
a second instrument.

### A reproduction that needed a credential now says so, correcting a claim of mine

Rendered the bug-bounty artifact from the live session - the first time that
renderer has been checked against real replay data rather than fixtures. Per
finding it states both halves honestly: re-verified against the target on
all six, and not cross-verified on all six, since no model has read any of
them.

But one finding reproduced only AFTER a credential was supplied, and
neither artifact said so. Its first replay was inconclusive - the recorded
request carried a credential and the transcript keeps only its digest - and
both the report and the badge row showed just "reproduced".

THAT CORRECTS SOMETHING I WROTE. A commit message earlier today said both
attempts stay in the history "so a reader can see that the first answer was
could not ask rather than did not hold". True of findings.json; false of
the report a reader actually gets. The distinction is material: for whoever
triages this, "it still works, with a valid session" is a different report
from "it still works", and the severity conversation differs.

Both artifacts now carry it - a line naming the earlier attempt and its
reason in the report, a neutral badge beside the success in the bug-bounty
page - and only when the history holds one, because qualifying a clean
result is its own form of misreporting. Three plants: removing the badge
fails, printing it on every finding fails, and removing the report line
fails.

A failure to reproduce still outranks everything, unchanged: an earlier
inconclusive does not soften a target that answered and did not produce the
bytes.

AND THE TEST READ `_badges` AS A LIST when it returns an assembled string,
so joining it inserted a space between every character. Fifteenth shape
assumption in this session, caught the same way as the other fourteen - by
running it.

### The whole finding pipeline, cold-started on the final tree

Around twenty edits landed today across the evidence store, the proof
matrix, the judge case file, the replay layer and four renderers. A passing
suite says each piece still works; it does not say the path through them
does. So: fresh lab on loopback, fresh engagement against it, every layer
and every artifact, from nothing.

    matrix          6 findings, 5 proven + 1 candidate, graded from bytes
    re-verification 5 reproduced, 1 inconclusive with its reason
    cross-read      dry run, 8892 bytes, no first-model reasoning in it
    artifacts       report.md, report.html, report-h1.html, report.sarif,
                    summary.json all rendered
    coverage        all three layers stated, including the zero
    verify          73 chained entries anchored to summary.json,
                    6 findings re-validated, artifacts sealed

The zero is the line worth keeping in view: the cross-read column reads
0 of 6 on evidence produced without a model endpoint, and the report says
so and names the command that would change it. Every defect fixed today
was a variant of that column being silently absent instead.

WHAT THIS DOES AND DOES NOT ESTABLISH. It establishes that the path holds
end to end after a day of edits, that the seal survives a replay, and that
the artifacts agree with each other. It does not establish that a second
model would dispute nothing - that needs an endpoint, and it would measure
models rather than this code. Nor does it settle the two decisions left for
a person: whether three authentication aliases should carry their own
weakness identifiers instead of their proof-shape class's, and one line of
product copy that is now a universal claim over a count that can contradict
it.

Both were reported rather than taken, because each one changes what the
system claims rather than whether it keeps its claims.

### The same bug on two subjects was two findings

The dedup key had already decided that a different subject VALUE on one
endpoint is one finding: it keeps query parameter NAMES and drops their
values, so two ids in a query string merge. The path was used verbatim, so
the same bug written as a REST path parameter got the opposite treatment.
Measured:

    /item?id=1   vs /item?id=9      merged
    /api/user/2  vs /api/user/3     SPLIT

AND IT IS REACHABLE, which is how it was found. Running the ledger against
a live session that already held an idor finding for one subject, it
recommended recording the next subject as a NEW finding - correctly, by its
own rules: the evidence is in the transcript and no finding cites it. So an
engagement against a REST API with N enumerable subjects produced N
findings for one bug, and the report counted N.

That is inflation at the source rather than at the presentation layer: not
a renderer double-counting, but the store genuinely holding N rows.

Numeric path segments now normalise, matching the decision already made for
query values. NARROW ON PURPOSE, because the note on that key is right that
over-merging hides a real finding and that is worse than the duplicate it
prevents. Only all-digit segments: a version segment keeps two APIs apart,
two collections with the same subject id stay apart, a longer path stays
its own endpoint, and a segment that merely begins with a digit - an
authentication factor count, for instance - is not an id. A uuid segment is
also an identifier, and merging those is a larger claim that can have its
own evidence and its own test.

Both directions planted: the verbatim path fails, and a looser rule that
merges anything beginning with a digit fails.

FOUND BY RUNNING THE LEDGER, which had never been run on a session that
needed a decision. The rule that blocks an engagement's exit while a proven
finding has no second-family reading was added earlier today and its output
had only been reasoned about, never read. The first thing it actually said
was about something else entirely.

### The fix created a loop, and the test for it took three attempts to fail

Merging two subjects into one finding closed the inflation at the store and
opened something worse at the ledger. Two definitions of "already
recorded": the store's dedup key, which now drops subject values, and the
ledger's scan, which used the raw path. So the ledger kept recommending a
record that `add_finding` then refused as a duplicate - recommend, refuse,
recommend. An agent following the ledger would not get out.

Found by running both sides together. Reading either alone looks correct,
and each is correct about its own question.

ONE DEFINITION NOW, in the module both planes already import, because the
ledger deliberately imports nothing from the evidence store - it reads
artifacts, the store writes them, and that separation is worth keeping. The
ledger still prints the concrete URL as the target, since an operator acts
on a real address rather than on a template; only the comparison is shaped.

Verified against the live and the sealed sessions: the recommendation is
gone and the ledger moves to the next genuine action, which is the proof
gap on the xss candidate with the missing check named.

AND THE TEST TOOK THREE ATTEMPTS, each failing in a way worth keeping.

The first compared the two key FUNCTIONS and agreed - but reverting the
ledger's call site left it green, because both functions still went through
the shared helper. It tested the definitions; the defect was at the call.

The second drove the ledger for real and guarded the assertion behind "if
the action is record_finding". The hand-built session produced a different
action, so the branch never ran and the test passed whatever the code did -
a VACUOUS test, hours after this session asserted an invariant against
exactly that shape in the grader. Reproducing the rule needs an exchange
that grades proven on its own, which means encoding a class requirement
into a fixture, and a fixture that drifts from the matrix starts passing
for the wrong reason.

The third asserts the call sites: both the recorded set and the comparison
against it must route through the shared key. Both plants are red now.

Seventeenth shape assumption on the way there - the action record's field
is not called what I typed - and the same remedy as the other sixteen:
print the real fields.

### Every artifact must report the same findings - the relation nothing asserted

Having argued that per-finding verification cannot see a defect in the
RELATION between findings, the next question is what else of that class is
unguarded. Measured on a live session: all five artifacts agree on the
count, and the summary's severity tally equals the findings' own. The
relation holds - and nothing asserted it.

Both failure modes of that relation have already happened in this project.
Two rows for one bug: a REST path subject keyed separately from a
query-string subject, fixed an hour ago. One row dropped: a console filter
that rendered one of ten findings, found by the session that owns that file.
Each passed every per-finding check.

Asserted now, in two tests: every artifact reports the same count and
carries every finding id, the summary's tally equals the findings'
severities, and the bug-bounty page - the one that leaves the building -
carries every title. Planted a renderer dropping its last result and
another dropping its first: both red.

FIVE WRONG SHAPES ON THE WAY, which is the part worth recording, because
the test was harder to write than the fix it guards:

The command entry point and a module were not in scope at the top of that
file. The demo writes into a timestamped SUBDIRECTORY, so every path was
one level off. The summary's `findings` key holds the LIST, not a count -
and the measurement I had run minutes earlier printed its length through an
isinstance branch that existed precisely because it is a list. The session
was reopened on the parent rather than the session directory, which
produced a page with no findings at all - and I diagnosed that as a wrong
target twice before reading the line numbers. And the last assertion
demanded a finding title appear RAW in an HTML page, which the renderer
escapes - correctly, since emitting a title unescaped would be an injection
hole in the deliverable. So the test, as first written, was asking for a
defect.

Nineteen shape assumptions in this session. The remedy has been the same
every time and it is cheap: print the real thing before asserting about it.

### A diff across hosts retracted six findings, and only stderr said why

Ran the retest diff, which had never been run. Between two runs of the same
application on different ports it correctly reports every finding as still
present - the port is normalised, which is right for a retest. Across
different HOSTS it reports every finding as fixed AND new, because the two
runs are different applications.

The code knew that and warned. On stderr. Stdout carried "6 fixed, 0 still
present, 6 new" with nothing saying why, and a diff is normally captured by
redirecting stdout - so whoever reads the file gets a retraction of six
findings and six discoveries presented as facts about the world. The JSON
carried both targets, from which a reader could INFER it; inference is not
a statement, and a machine consumer comparing hostnames is doing the tool's
work.

The caveat now reaches all three channels from one flag, and does not
appear on an ordinary retest, where it would teach a reader to ignore it.
Three plants: removing it from stdout fails, removing the flag from the
JSON fails, printing it on every diff fails.

AND MY OWN CHECK OF THIS LIED, in the exact pattern this session keeps
paying for. A first pass concluded stdout already said it, because a search
for host-related words found two matches - both the word "host" inside a
finding TITLE, "OS command injection in /ping host parameter". Twentieth
wrong instrument here, and the mirror of the worst one: that nearly
published a false positive, this nearly retracted a real finding. Same
cause both times - a pattern matching content where a claim was wanted -
and the same remedy: look at what the matches actually are before believing
the count.

### The last three unrun commands, and what the preflight actually says

Ran the remaining commands that had never been exercised. Three clean
results, written down because a dimension that comes back clean is
information:

The metrics comparison prints a row per measure across two sessions, and
the error row LEADS - with the reason in a comment: every row under it
describes a run that may not have happened, since zero findings, zero
requests and zero cost is also what a clean finding-free run looks like.
That is the "a dead run looks clean" hazard, already handled.

The verifier's JSON form is complete and agrees with its human output: the
chain state, the entry count, the findings re-checked, and the nine sealed
artifacts by name.

The credential preflight is the one worth quoting, because it corrects
something I have said repeatedly. With no key in the environment it reports
`ok: false`, `degraded: true`, the provider's own error text, and exits
non-zero. It does not claim success - which matters, because a preflight
that passed without a usable credential would let a run start and die, and
a dead run's artifacts look like a clean one's.

AND IT NAMES THE REAL BLOCKER. The credential EXISTS - the source is the
editor's own oauth - and the provider answers 400: third-party apps draw
from extra usage rather than plan limits, with the page to add it. So the
cross-read layer is not waiting on an API key, which is what I told the
user more than once. It is waiting on account balance. Measured twice, two
seconds apart, identical.

That distinction is not pedantic: "supply a key" asks for something the
machine already has, and acting on it would have produced another failed
run with the same 400.

### The console's aggregate agrees with the disk, and now something says so

The last unexamined audit claim in this half: that the dashboard's API sums
across session directories, so one bug counts twice. Refuted by running the
server, which had never been run here.

    the endpoint   16 findings, 14 proven + 2 candidate, 4 runs,
                   no repeated (run, id) pair
    a direct read  16 findings, 14 proven + 2 candidate

Exact agreement, and it independently reproduces the measurement the
session that owns the console reported hours earlier against the same
evidence - two sessions, two instruments, one number.

Tenth refutation here. But the relation was unasserted: a test covered ONE
session's findings, and the multi-session aggregate is precisely where
double counting would live, since the console reads this endpoint and an
aggregate that walks a directory twice misreports the engagement while
every individual finding stays correct.

Asserted now in both directions - the served (run, id) pairs must equal
what the files hold, with no repeats, and one planted session must be
served once. Plants: scanning each run twice fails, dropping each run's
first finding fails. The fifth invariant of this kind in this session.

AND THE FIRST PLANT TOOK THREE ATTEMPTS TO LAND, none of them the code's
fault. A pattern that occurs twice in the file, then a line filter that
caught both occurrences, then the exact index. Each failed attempt printed
"2 passed", which means nothing at all: a plant that does not apply is not
evidence that the test holds. That is the same trap as a vacuous assertion,
one level out - the check ran, the subject was never changed, and the green
result looked identical to a real one.

### The bug-bounty page denied an excerpt it was displaying

The one audit claim still refuted by READING rather than by running: that
the bug-bounty renderer tells a reader a header-quoted excerpt was not
found in the response. Reconstructed, and the reading was imprecise while
the effect was real.

The note says "shown from the start of the body: the quoted excerpt was not
found in it verbatim". Literally true - "it" is the body - and the headers
are rendered directly above the window, so the proof IS on the page. But a
triager scanning "the quoted excerpt was not found" concludes it is not in
the response, three lines under the header that carries it. The artifact
undercut its own finding.

AND THE PATH BECAME REACHABLE ONLY TODAY. Three classes have their proof in
a response header, and until the evidence store accepted header casing a
header-only excerpt could not be recorded at all - so this note could never
fire for one of them. The fix that made those findings citable is what
exposed this. Second time today a fix of mine opened a downstream defect:
the first was the dedup change that set the ledger recommending what the
store refuses.

It now says where the excerpt IS, and through the evidence store's own
definition of an entry's citable texts - the THIRD place that concept
lives, and the second had already drifted. Checking only the lines this
renderer prints missed the canonical header casing, which the store
accepts, so a quote written the way HTTP writes it still got the bare
denial. Reusing the store's function means a quote in any form it accepts
is recognised here as the same evidence.

Both directions planted: the bare note fails, and claiming HEADERS for a
fabricated quote fails - the second matters, because that sentence is what
a reader needs when a findings file has been edited by hand.

Twenty-first shape assumption on the way, a helper name typed from memory.

### The report did not say whether its own record verifies

Three commands treat an unverifiable record three ways, measured on one
tampered copy: the replay refuses and exits non-zero, because it writes new
evidence into the session; the judge warns, proceeds, and records that it
re-sealed over a mismatch; the render warns twice and writes the report.
Each is coherent for what that command writes, so the difference is
deliberate rather than an oversight - but nothing said so, and nothing said
it in the document.

AND THE EDIT REACHED THE DELIVERABLE AS FACT. Changing one finding from
medium to critical in findings.json renders as "Severity: Critical", raises
the critical count in the tally by one, and sits beside its unchanged
"proof: candidate". The seal catches the edit and the render warns on
stderr; neither reached the report. A report read away from the terminal
that produced it could not say whether its own record verifies, which is
exactly the diff-caveat shape from an hour ago.

`findings_bad` does not catch this and should not be asked to: it validates
EVIDENCE - the cited ids exist, the excerpt is verbatim - and an edited
severity leaves the evidence intact. Severity is partly a judgement, so
editing it is not necessarily tampering. Saying the file changed is not
optional.

The report now states its record's verification state in BOTH directions,
because a line that appears only on failure teaches a reader that its
absence means verified. The verified form carries the counts it checked, so
it reads as a measurement rather than a badge; the failing form names each
problem and says to read what follows as a claim about the file rather than
about the target.

Both planted: removing the line fails, and claiming verified over a
mismatch fails.

AND I MEASURED A STATE I HAD ALREADY CHANGED. The first reading of the
verification flags came back clean on the tampered copy, with the mismatch
key absent entirely - because my own earlier render of that copy had
re-sealed it. Twenty-second wrong instrument, and a new kind: not a bad
pattern but an observation taken after the observer had altered the thing.

### The documentation gap I named and then did not close

The previous entry observed that three commands treat an unverifiable
record three ways, that each is coherent for what it writes, and that
"nothing said so, and nothing said it in the document" - and then fixed
only the report line. The document half stayed open, named by its own
commit message.

Closed now, in the file's shape: a table of what each command does and the
reason, keyed to what each one WRITES, plus the four properties and the
tests that hold them. The re-verification refuses because it sends requests
and writes exchanges, so proceeding compounds the damage. The cross-read
proceeds because it cannot raise a grade and therefore cannot launder a
false finding upward - and the fact that it ran over a mismatch stays in
the artifact. The render proceeds because it only reads, and states the
record's verification state in its own text.

The edited-severity case is written out, because it is what makes two of
those properties distinct rather than one: evidence re-validation checks
that cited ids exist and the excerpt is verbatim, so an edited severity
passes it untouched and is counted in the tally, while the seal still
catches the edit. Those are different checks answering different questions,
and a reader who conflates them will expect the wrong one to protect them.

AND THE TEST NAMES WERE READ OFF THE FILES THIS TIME. The last section
added to this document cited four tests from memory and none existed - the
gate named all four. Reading them out of the test files first, the doc gate
passed on the first attempt.

### A test that raced a thread it could simply wait for

CI went red on two of five Windows jobs, same test both times, with the
sidecar state file still reading `running` where the assertion wanted
`failed`.

That test asserts a cross-party claim: the API row is derived from the
directory and turns terminal as soon as the runner returns, while the state
file is written by the WORKER THREAD. The first remedy for the race was a
ten-second poll, and the comment recording it said one Windows job had
failed while ten passed. Two jobs of one run then failed, which settles
that the window was never the problem - a longer timeout would have made
the flake rarer and no less wrong.

The registry already joins its worker threads, and that is what the test
should have done. After the join the flush has happened or the thread is
gone, so the assertion is exact instead of probable: the sidecar ends up
terminal, with no claim about when. Five consecutive local runs green.

WHY THE RACE EXISTS, since the fix is only honest with the mechanism named:
`_set_state` ends by logging the transition, and `log` is what mirrors the
record to the state file. So the write happens inside the worker thread at
the transition, after the directory has already become derivable - exactly
the gap the test was sitting in.

AND THE FIRST PLANT TESTED SOMETHING THE TEST DOES NOT CLAIM. Removing the
belt-and-braces flush in the worker's `finally` left the test green, which
looked like a hole until the mechanism above explained it: the transition
had already written the file. The plant that matters is the one this test
exists for - making a dead run report `done` - and that one is red.

### Two negative assertions with one second of margin

Generalising the fix above - if one timed wait was the wrong shape, where
are the others - found thirteen in the server tests and two elsewhere. The
thirteen are fine; the two are the opposite problem and worth the
arithmetic.

Both guard process cleanup: a tool times out, or an MCP server closes, and
the test asserts that a grandchild the subject spawned did NOT survive. For
a negative claim a timed wait is the right instrument - there is nothing to
join, since the process should not exist - but the risk inverts. A short
wait makes the test PASS WRONGLY, and these guard an invariant the tests'
own messages call out: an orphan "still has the target, the unlinked stdout
fd, and no place in the transcript".

Measured: the grandchild wrote its marker 2s in, the parent was killed at
0.5s, and the test looked 3s in. ONE SECOND OF MARGIN. A loaded runner can
close that, and the test would then report cleanup working while the orphan
was alive.

The write moved to 1s - it only has to outlive a kill at 0.5s - and the
look to 5s, so a delay of up to four seconds still produces a red test. Two
seconds added to the suite for four times the margin, and the arithmetic is
in the comment so the next person shaving it can see what they are
spending.

A poll would not help: concluding "it never appeared" means waiting out the
window either way.

Planted to confirm the widened test still catches the real thing: with the
process-group kill removed, the orphan survives and the test is red.

### A finding dropped for bad evidence, and nothing said it existed

Swept the generalisation of the diff-caveat fix: where else does the tool
know something and only stderr say it? Eighteen warnings qualify by
wording; the ones that matter are the exclusions that change a number.

The strongest is on the finding axis. The render drops findings whose cited
evidence no longer re-validates - correctly - and warns on stderr.
Measured: six findings recorded, five rendered, and the document mentioned
the sixth ZERO times. Not a finding that looked wrong; a finding that
DISAPPEARED, with a tally and a count that silently described five.

Both renderers now name it, through one function, and the omission notice
is absent on a clean render where it would teach a reader to skip it.

AND THE CROSS-ARTIFACT TEST I ADDED EARLIER ASSERTED THE WRONG INVARIANT.
It required every id in findings.json to appear in every artifact, which
would fail a render that was behaving correctly - the one session where the
test matters is the one where an exclusion is right. The correct invariant
is that an id is either SHOWN or NAMED AS OMITTED.

Holding that is what caught the html renderer still being silent after
markdown was fixed: the fifth time in this session a fix landed in one
renderer and missed its sibling, and the FIRST caught by an invariant added
earlier the same day rather than by a later audit. That is the first
evidence in this session that the invariants are doing work after the fact
and not only describing fixes already made.

Three plants: markdown silent fails, html silent fails, and claiming
verified over an omission fails.

AND THE GATE CAUGHT THE INTERACTION. A pre-existing test asserted the
dropped id appears NOWHERE in the report - `"F99" not in rep` - which the
omission notice violates by naming it. The old assertion was the coarse
form of a real concern: an id in the report could be mistaken for a
reported finding.

Naming is the more honest form in both cases that test covers. For a row
planted by a tamperer, naming it says someone added F99 and it was
rejected; for a real finding whose evidence broke, naming it says a
recorded claim was dropped. And the notice reads "recorded in findings.json
and NOT shown here", so the form cannot be read as a reported finding -
which is exactly what the old assertion was protecting.

So the assertion moved from presence to FORM: the id must not head a
finding block, and it must be named as omitted. Planted the defect that
test exists for - not excluding a tampered finding at all - and it is red,
so the stronger assertion did not cost the original coverage.

Third time today an assertion of the shape "this string is absent" had to
become "this claim is not made in this form", after the cross-verification
absence line and the dispute attribution.

### A median under a denominator that was not its own

Continuing the sweep for "the tool knows and only stderr says it": the
benchmark comparison printed each median beside the arm's ROW COUNT, while
`_values` skips a trial that has no value for that key.

Only eight of the fourteen metrics are all-or-nothing - they suppress the
median when a trial is missing. The other six are `proven`, `candidate`,
`unproven`, `findings`, `requests` and `coverage`: exactly the numbers a
reader uses to judge whether the system finds anything. Measured on an arm
of four trials where two died: the median was computed over two values and
printed under N=4, and the warning about the skew went to stderr while the
CSV went to stdout.

Both outputs now state the count the median was computed over, and say
nothing extra on a complete arm where it would teach a reader to skip it.
Three plants: the row count back in the CSV fails, the table omitting the
short count fails, and printing it on every arm fails.

THE RESIDUAL IS NAMED RATHER THAN FIXED, because it is a decision about the
experiment and not about this function. The skipped subset is
systematically the trials that COMPLETED, so an arm that crashes more often
still reports better finding counts - word for word the bias the sibling
test describes for time-to-first-finding, where "the arm that fails more
often reports the better time". Making these six all-or-nothing too would
suppress the median whenever one trial died, which throws away what the
surviving trials measured. This change makes the denominator truthful;
whether a partial arm should report at all is the user's call.

Reading the code's own partial solution first is what kept this honest: the
all-or-nothing list already existed, with a comment explaining the bias, so
the question was never "is this checked" but "which six are outside it".

### A diff that reported a finding it could not stand behind

Fourth and strongest instance of one shape in this sweep. The other three
qualified a whole run - a diff across hosts, a render that dropped a
finding, a median under the wrong denominator. This one qualifies ONE NAMED
FINDING.

The diff printed "[STILL ] F03 ... (medium)" inside "6 still present" - a
per-finding claim about the target - while F03's cited evidence no longer
re-validated against its transcript. The caveat naming F03 went to stderr;
the claim went to stdout. Whoever captures a diff, which is the normal way
to keep one, got the claim without the condition.

Marked on the row, not only in a header: a reader scanning for one finding
sees it beside that finding rather than carrying a list down from six lines
up. The ids also reach the JSON as a map per side, so a machine consumer
does not have to parse prose. Nothing is marked when both sessions are
sound.

Three plants: removing the row mark fails, removing the stdout header
fails, marking every row fails.

THE FOUR ARE ONE DESIGN CONVENTION MEETING ONE FACT. Warnings go to stderr,
and the deliverable gets read away from the terminal that produced it - in
a file, in a report next week, in a CSV handed to someone else. A warning
on stderr is not a disclosure; it is a message to whoever is watching. That
is the family every defect in this session belongs to: not an agent
inventing a finding, which the architecture blocks, but the artifact not
carrying what the system knows.

### The verified notice could not tell verified from never-checked

The last unverified candidate in the stderr sweep was "could not seal
artifacts - this render is not digest-anchored". Chasing it found a defect
in the record-state line added earlier today.

Measured on a live session before and after sealing: the notice read
"Record verified ... artifacts matching their digests" in BOTH cases, and
before sealing there are no digests at all - the seal is an entry in the
transcript and `sealed` is None without it. So a report from a run that
died before sealing, or whose seal failed, was indistinguishable from a
sealed one, and the sentence asserting digest agreement was false.

AND THE FIRST FIX FOR IT WAS WRONG, caught by the gate on three tests.
Flagging the absent seal as a problem made EVERY normal report say it did
not verify, because a first render always precedes the seal: sealing is the
last step and has to cover the files the render is writing. Measured, the
session on disk had nine sealed artifacts while its own report said it had
none - the render had read the transcript before the seal entry existed.

What is true at render time is that the seal FOLLOWS. So the sentence now
claims digest agreement only when there are digests, and otherwise says the
digests are written after this file. Both directions planted: the
unconditional claim fails, and saying "written after" over a sealed record
fails.

That is the second fix of mine today that the gate rejected before it could
ship, after the dedup change that set the ledger recommending what the
store refuses. Both were wrong in the same way - correct about the
condition, wrong about WHEN it can be evaluated.

FOURTH CORRECTION OF A CLAIM OF MINE in this session, and the same shape as
the other three: the sentence described what the code intended to check
rather than what it had checked. The verified line listed the conditions it
examined and omitted the one that makes the rest meaningful.

AND TWO WRONG DIRECTORIES ON THE WAY. The first attempt removed keys from
summary.json, where the digests are not - they are an `artifacts_digest`
entry in the transcript. The second called the verifier on the parent of
the session directory, since `Session(root, ...)` creates a timestamped
subdirectory, so it read a directory with no transcript and reported
`chained=False` for a session whose chain was intact. Twenty-fourth shape
assumption, and the remedy is the one that has worked every time: print the
real thing - here `session.dir` - before asserting about it.

### An IndexError where a diagnosis belonged

CI failed on one Windows job of eleven: a callback test raised
`IndexError: list index out of range` while indexing `callbacks[0]`. No
callback had arrived, and nothing said why.

The fixture is a target that fetches whatever URL lands in a query
parameter, and it swallowed every exception from that fetch. So a failure
in the TEST'S OWN target - a loopback urlopen that refused or exceeded its
three-second timeout on a loaded runner - surfaced as an index error in the
probe's result.

AND WAITING LONGER CANNOT HELP, which is the part worth keeping. That fetch
is synchronous inside the request handler, so by the time the probe's
request returns, the callback has already arrived or already failed. The
probe's eight-second settle window is waiting on something that has
finished. Widening it - which is what this test's history shows being tried
once already, from three seconds to eight - could never have worked.

The fixture now records why its fetch failed and the assertion names the
half that broke before indexing. Planted a fetch that always refuses: the
message reads "no callback arrived; the target's fetch reported ..." rather
than an index error.

SECOND TIME TODAY THE ANSWER WAS NOT A LONGER WAIT. The first was a test
racing a worker thread it could join. Here there is nothing to join and
nothing to wait for: the right repair was to make the silent failure
speak. A timed wait is the wrong instrument whenever the thing waited on
has already resolved - and swallowing the error is what hid that.

### Swept for swallowed observations; the package is clean and the scaffolding was not

The last fix found a test fixture swallowing the error from its own fetch,
so a failure in the test's target surfaced as an index error somewhere
else. Generalised: where else does an exception hide something that was
being measured?

The discriminator is what the exception MEANS. "This is not that shape" is
branch selection and `pass` is correct; "the thing you were measuring did
not happen" is an observation, and dropping it is the defect.

By that test the package is clean. The three silent handlers in the probe
module are all branch selection: a body that is not JSON falls through to
the urlencoded path, a cookie jar that will not convert moves to the next
jar, a blob that is not base64 moves to the next candidate. None of them
loses a measurement.

The collector's body-read fallback looked like the dangerous kind - an
unreadable body becomes empty - and it cannot lose a callback. The nonce is
matched against the path AND the body, and every callback URL is built by
one function that puts the nonce in the PATH, which comes from the request
line rather than the body. Both call sites use it.

So the one real instance of this class was in the test scaffolding, not in
the package, which is worth stating plainly: the probes are careful about
not discarding what they saw, and the fixture that stood in for a target
was not. A swallowed error in a fixture is as capable of hiding a defect as
one in the product - it just hides it from the test rather than from the
operator.

### Verification & packaging
Each count is stated ONCE. The merge of the two lines of work brought two
copies of this section, each with its own figure, which is exactly the drift
the documentation gate exists to catch - and it caught it.

- `python -m pytest tests/ -q`: 1198 tests (unit + live-lab + loop + team +
  MCP client + MCP server + proof matrix + provider adapters + the decision
  controller + the cross-family judge + probe/matrix agreement + CLI +
  external-tool subprocess path + hardening regressions + the web console +
  the orchestrator + prompt assembly + skill-card grants). Every hardened
  fix carries a regression test: UA-redaction, malformed JWT/manifest/MCP
  entries, atomic-write litter, non-JSON tool results, worker-crash
  isolation.
- `python selftest.py`: 164 offline checks, including a documentation
  consistency pass — every tool, subcommand, proof class and **stated count**
  in the docs is verified against the code, and a count the docs stop stating
  fails rather than passing on nothing. It caught a stale tool-schema count
  in `docs/USAGE.md` on its first run, left behind by an earlier version.
- `docs/VERIFICATION.md`: property → enforcement → test matrix — every
  safety claim names the code that enforces it and the test that proves
  it, with a reading order for a first-pass review.
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
  CI (Ubuntu+Windows × Py3.10-3.14) runs pytest + selftest + a
  wheel-contents check.
