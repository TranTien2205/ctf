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

### Verification & packaging
Each count is stated ONCE. The merge of the two lines of work brought two
copies of this section, each with its own figure, which is exactly the drift
the documentation gate exists to catch - and it caught it.

- `python -m pytest tests/ -q`: 616 tests (unit + live-lab + loop + team +
  MCP client + MCP server + proof matrix + provider adapters + the decision
  controller + the cross-family judge + probe/matrix agreement + CLI +
  external-tool subprocess path + hardening regressions). Every hardened fix
  carries a regression test: UA-redaction, malformed JWT/manifest/MCP
  entries, atomic-write litter, non-JSON tool results, worker-crash
  isolation.
- `python selftest.py`: 157 offline checks, including a documentation
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
