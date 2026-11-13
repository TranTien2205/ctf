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

### Probe coverage (26 matched-pair probes)
- Injection: sqli (quoted/numeric/OR-pair/xpath/UNION), nosqli, ssti,
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

### Verification & packaging
- `python selftest.py`: 121 offline checks.
- `python -m pytest tests/ -q`: 187 tests (unit + live-lab + loop +
  team + MCP + CLI + external-tool subprocess path + hardening
  regressions) — every hardened fix now carries a regression test
  (UA-redaction, malformed JWT/manifest/MCP entries, atomic-write
  litter, non-JSON tool results, worker-crash isolation).
- `docs/VERIFICATION.md`: property → enforcement → test matrix — every
  safety claim names the code that enforces it and the test that proves
  it, with a reading order for a first-pass review.
- Fault-tolerance pass: every forensic reader (`verify`, `findings`,
  `diff`, `sessions`, `_reopen`, renderers) degrades malformed session
  artifacts to flags/warnings instead of tracebacks — fuzzed across
  dir-swaps, non-dict JSON, null fields and truncated files; locked in
  by `test_readers_survive_mutated_session_dir`. `dispatch` itself is
  total (every tool × wrong-JSON-type args returns a serializable
  dict) under `test_dispatch_total_on_malformed_args`.
- `python -m argus demo` / `demo --team`: scripted end-to-end on the lab,
  no API key (5 evidence-gated findings each).
- Wheel ships skills + role prompts + wordlists + exploit manifests;
  CI (Ubuntu+Windows × Py3.10/3.11/3.12) runs pytest + selftest + a
  wheel-contents check.
