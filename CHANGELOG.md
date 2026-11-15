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
  single-agent mode, where all 56 tools are granted and nothing is
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
- **An empty tool grant permitted all 56 tools.** `AgentLoop.__init__`
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

Not triaged, recorded with their shapes: the sweep's remaining claims
against `probe_xxe` (an SSRF-via-XXE payload asking for a URL rather than a
file), `probe_idor` (an object id shifted in a POST body rather than the
URL), `probe_lockout` (the credential-field pattern and the series floor),
`probe_smuggle` (the TE.CL veto), `probe_disclosure` (`/.git/HEAD` and
`/debug` against a floor that wants a credential-shaped secret) and
`probe_ppoll`/`probe_cache` (the unkeyed-input floor).

### Verification & packaging
Each count is stated ONCE. The merge of the two lines of work brought two
copies of this section, each with its own figure, which is exactly the drift
the documentation gate exists to catch - and it caught it.

- `python -m pytest tests/ -q`: 731 tests (unit + live-lab + loop + team +
  MCP client + MCP server + proof matrix + provider adapters + the decision
  controller + the cross-family judge + probe/matrix agreement + CLI +
  external-tool subprocess path + hardening regressions). Every hardened fix
  carries a regression test: UA-redaction, malformed JWT/manifest/MCP
  entries, atomic-write litter, non-JSON tool results, worker-crash
  isolation.
- `python selftest.py`: 160 offline checks, including a documentation
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
