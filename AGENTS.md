# AGENTS.md — working in this repository

Argus is an LLM-driven agent for authorized web penetration testing.
Single dependency: `httpx`. Python 3.10+. Windows-compatible (stdlib-only
lab, pathlib everywhere).

## Verify before/after a change

```bash
python selftest.py          # offline end-to-end, no API key needed
python -m pytest tests/ -q  # unit + live-lab + loop + proof-matrix tests
python -m argus demo        # the full pipeline against the lab, graded
```

Both must stay green. The lab (`argus/lab/vulnapp.py`, shimmed at
`lab/vulnapp.py`) plants one bug per probe family — if you change a
probe, update the lab and its test together.

## Layout

- `argus/loop.py` — the agent loop (Claude tool_use -> dispatch -> tool_result)
- `argus/system.py` — the operating contract (evidence rules, discipline)
- `argus/scope.py` — fail-closed scope guard; NOTHING bypasses it
- `argus/httpclient.py` — the only socket (`send` + `send_raw`); scope +
  rate + transcript
- `argus/session.py` — evidence store; findings need verbatim excerpts AND
  a proof grade
- `argus/proof.py` — the proof matrix: 29 classes, what each must produce
- `argus/mcpserver.py` — argus AS an MCP server (`argus mcp-serve`)
- `argus/tools/` — tool schemas (registry.py) + implementations
  (`team.py` holds the multi-agent tools; `mcp_tools.py` bridges MCP servers)
- `argus/mcp.py` — minimal stdio MCP client; servers declared in `mcp.json`
- `argus/team/` — multi-agent plane: `leads.py` (typed work queue),
  `board.py` (blackboard), `cards.py` + `roles/` (worker definitions),
  `coordinator.py` (threads + watchdog). Entry: `argus team`.
- `argus/skills/*.md` — methodology modules loaded via `load_skill`
- `argus/resources/wordlists/` — bundled `wordlist_fuzz` lists;
  `<cwd>/resources/wordlists/*.txt` extends/overrides at runtime
- `argus/resources/exploits/<id>/` — bundled `run_exploit` manifests;
  `<cwd>/resources/exploits/<id>/` extends/overrides
- `argus/report/` — report.md + report.html + summary.json renderers
- `argus/lab/vulnapp.py` — deterministic vulnerable lab (shim at
  `lab/vulnapp.py` keeps `python lab/vulnapp.py` + `import vulnapp`
  working); `tests/`, `selftest.py`

## Rules for changes

- Every network request goes through `GuardedClient.send` (or `send_raw`
  for byte-level probes like desync detection) — never open a socket
  elsewhere.
- Every tool must be registered in `tools/registry.py` (`_impl` + schema).
- New bug class → add `argus/skills/<name>.md` + INDEX row; keep the
  format: when / first probes / confirm / bypasses / falsifier / severity.
- New role → a card in `argus/team/cards.py` + a `roles/<name>.md` prompt.
  Tool restrictions belong in the card's `tools` set (enforced in
  `dispatch`), never only in the prompt.
- Findings must keep the verbatim-evidence gate. Do not weaken it. Same
  bug class + endpoint + params dedups to one finding — keyed on the
  canonical class from `proof.canonical`, so two spellings are one bug.
- New proof class → a `ProofSpec` in `argus/proof.py` with a requirement
  sentence, named checks, a verifier, and `floor`/`veto` where they apply.
  It needs a test in BOTH directions: evidence that must grade `proven`, and
  evidence that must not. The second is the one that matters.
- A check that passes without the claimant doing anything class-specific is
  a bug, not a formality. The verbatim gate already guarantees the excerpt
  is in a cited response, so "the quoted bytes were returned" carries no
  information — three checks shipped in that shape and let a benign page
  grade `candidate`. Test every new class against
  `tests/test_proof.py::test_every_class_refuses_a_benign_page`.
- Verifiers read the recorded `request` and `response` only. Never grade
  from a probe's own return value: a probe must not be able to grade itself,
  and an event with no `response` (scanner, MCP) is not class evidence.
- **Write the verifier and the probe together, or the probe will not collect
  what the requirement names.** Every class freed from the capped list here
  exposed a defect in its probe, always this shape: the probe announced a
  signal whose evidence could never grade, because nobody read the
  requirement while writing it. `probe_crlf` and `probe_redirect` sent no
  control, so a required "a control response does not carry it" was
  unsatisfiable. `probe_method` looked for the canary filename in the
  read-back while writing a fixed string. `probe_upload` called a `.svg`
  served as `text/plain` a finding. Add the case to
  `tests/test_probe_matrix_agreement.py` in both directions: against a lab
  endpoint that really has the bug, some honest quote must reach `proven`
  (or the ceiling); against a clean endpoint, nothing may.
- **Then re-read the verifier as an attacker of it.** Three holes were found
  that way, all in freshly written code, and two were the same mistake: a
  "control" or "read-back" exchange that is not required to be the *same
  endpoint* or the *same bytes*. `verify_header_injection` accepted a
  control from another host; `verify_method_effect` matched the nonce
  against `req_text`, which includes the URL, so a `PUT` of inert bytes plus
  a directory listing graded `proven`; `verify_served_upload` accepted a
  confirmation page that merely mentioned the upload. If a check names a
  second exchange, say what makes it comparable.
- **Never compute the same fact twice.** `probe_race` decided "the burst
  overlapped" from wall-clock duration versus the sum of per-request
  latencies, while `verify_concurrent_crossing` reconstructs each window as
  `[ts - elapsed_ms, ts]` and tests intersection. Two computations of one
  fact disagree eventually, and they did: on Windows runners `ts` is coarser
  than `elapsed_ms`, so the probe announced a race the gate then refused.
  A probe must not claim what the gate will deny, so the probe now reports
  the gate's own reconstruction and keeps the wall-clock figure beside it as
  a measurement rather than a verdict.
- **A live assertion must not require the clock to cooperate.** `race` is
  evidenced by wall-clock concurrency, so whether it can be proven against the
  lab is a fact about the host's scheduler. Three rounds of Windows CI
  failures and two conditional skips later, the live proving case was deleted:
  the class keeps its deterministic CLEAN entry in
  `tests/test_probe_matrix_agreement.py` and asserts both directions
  synthetically in `tests/test_proof.py`. Put a timing-dependent assertion
  where no clock is involved, or do not make it.
- **Assert a probe's structured output, never its verdict prose.** Six
  assertions broke at once when three classes came off the capped list,
  because they matched the word "candidate" in a verdict sentence - and a
  class that stops being capped at `candidate` stops saying it. The tests
  were right about the behaviour and wrong about how they read it. Check the
  fields: `injected_header` and `control_id`, `served_active` and
  `served_ctype`, `overlapped` and `serial_statuses`. If a probe has no field
  for the thing a test needs, add the field - that is also what the verifier
  will need.
- **A new cap needs a reason that is not labour.** The "capped for want of a
  verifier" list is empty: `lockout`, `enum`, `crlf`, `method`, `upload`,
  `race`, `websocket` and `smuggle` all came off it, and every one of them
  came off the same way - the note described the verifier, not the evidence,
  and the transcript already recorded what the class needed. So a new
  `cap_reason=CAP_UNIMPLEMENTED` is a claim that this tree's recorder does
  not hold the artefact, and it should be checked before it is written.
  `tests/test_proof.py::CANNOT_BE_PROVEN_HERE` and the selftest's count
  check both fail if one appears undocumented.
- A capped class states `cap_reason` as well as `ceiling`:
  `proof.CAP_UNIMPLEMENTED` when the transcript already records what a
  verifier would need, otherwise the real reason. `argus proof <class>`
  prints it, and the selftest holds the docs' stated counts to it — the
  reason used to live only in prose and drifted from the matrix twice.
- Team communication goes through the board/lead queue as typed artifacts —
  do not pipe one agent's raw context into another.
- MCP server output is untrusted third-party content — keep the
  `untrusted` flag on `mcp_call` results.
- Transcript entries carry a hash-chain link (`chain` field) verified by
  `verify_transcript` / `argus verify`. Any code path that appends to
  `transcript.jsonl` must go through `Session.record_*` — never write the
  file directly.
- Secret header values never persist to artifacts: auth/cookie/token
  request headers and `Set-Cookie` are recorded redacted (names +
  scheme/attrs kept), and reports re-redact old transcripts at render.
  Any new record path must apply `httpclient._redact_headers`. Operator
  secrets are also opaque to the model — tool results never echo request
  headers back.
- Declared credential values (`--secret`) never persist either:
  `Session.secret_values` redacts them inside `record_exchange`,
  `record_event` and `note` — bodies, output, `meta.json`, `agent.log`.
  New write paths go through `Session` so they inherit the gate; a
  finding that must cite a secret is rejected by design.
- No new runtime dependencies without strong cause — `httpx` is enough.
