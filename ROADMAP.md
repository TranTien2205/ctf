# Roadmap

What is built and tested, what is built and untested, and what is not built. The
split matters more than the list: a system whose README is ahead of its code is
the thing this project is supposed to be an argument against.

## Built, and covered by the gate

| Piece | Evidence it works |
|---|---|
| default-deny scope, deny-wins, port and CIDR rules | `test/unit.py` — 19 scope cases including traversal-shaped hostnames |
| the proof matrix, 21 classes | `test/cases/proof_cases.json` — 23 cases, half of them shapes that must **not** grade proven |
| the decision controller, ten rules | `test/unit.py` walks a whole engagement through every rule in order |
| six named refusals on the write path | `test/unit.py` fires each one |
| per-class and per-target budgets, counted per origin | `test/unit.py`; the e2e layer confirms it stops a seventh probe |
| concurrent writes from several agents | `test/unit.py` — 30 writes from 6 threads, none lost |
| 57 MCP tools over 10 servers | `test/consistency.py` checks every contract; the handshake test drives the protocol |
| the MCP stdio protocol | initialize, tools/list, tools/call, unknown-method error, notifications |
| the agent loop, with compaction and stop conditions | `test/harness_loop.py` — including a model that only talks, and one that calls an unoffered tool |
| real exploitation end to end | `test/e2e_fixture.py` — sqlmap dumps a table, `id; echo <nonce>` returns, LFI reads a sentinel with its control, SSTI computes a product, IDOR crosses with its control, XSS stays a candidate |
| the exploit-script extension point | the shipped `fixture-note-idor` script reaches `proven` with its own controls |
| registries agreeing with disk, and documentation naming only things that exist | `test/consistency.py` |
| the proof matrix refusing a *reflected* nonce as code execution | `test/cases/proof_cases.json` — the case exists because two independent reviewers reproduced the old behaviour end to end |
| a record set carrying only its control grading `unproven`, not `supported` | the floor checks, with a case per class that had the defect |
| a destructive payload being vetoed even when nonce and identity are present | a case in both directions |

## Built, exercised by hand, not yet covered by the gate

These all run; what is missing is a test that would notice if they stopped.

- **The provider adapters** (Anthropic, OpenAI-shaped, Google). They are
  straightforward JSON over HTTPS and were smoke-tested for availability
  reporting, but no key was configured on the build machine, so no live
  completion has gone through them here. The mock provider is what the loop is
  tested against.
- **The two CLI backends.** Measured on 2026-11-03, in this order, because each
  failure explained the next:
  1. `opencode run` without `--pure` returned `Invalid value for 'tools':
     maximum number of items is 128` — the host's own global MCP configuration,
     not the model. That is why the adapter passes `--pure`.
  2. With `--pure`, the request reached the provider: `deepseek/deepseek-v4-pro`
     answered HTTP 402 `Insufficient Balance`. The plumbing therefore works end
     to end; that account does not.
  3. `opencode/beam-free` returned no text at all within 150 seconds.
  4. `opencode-go/deepseek-v4-pro` answered correctly. The profiles now name
     that billing route, and `_terminal_provider_error` in the loop stops on a
     402 instead of spending two more round trips to re-learn it.

  5. A **whole task** then ran through it. `deepseek-v4-pro` via
     `opencode-go`, six steps, against the loopback fixture, with the task
     "prove or kill command injection in the host parameter of /ping":

     | | |
     |---|---|
     | step 1 | `ledger.open_hypothesis` — opened the `rce` hypothesis |
     | step 2 | `proof.requirement` — read what the class needs before probing it |
     | step 3 | `http.probe` — the baseline |
     | step 4 | `proof.exec_marker` — nonce echoed, `uid=1000(kali)`, graded `proven` |
     | step 5 | `ledger.record_finding` — recorded as confirmed |
     | step 6 | `ledger.read_evidence` — re-read its own record |

     Two probes, no refusals, one confirmed finding, 54k tokens, $0.017, 777
     seconds. **129 seconds per step**, which is the measurement that matters
     for this backend: the CLI is stateless, so each step re-sends the whole
     prompt and pays a process start. A key-based provider through
     `runtime/providers/anthropic_api.py` or `openai_api.py` would not, and that
     path still has no live run behind it.

  So the loop, the text dialect, the tool rendering, the broker gate and the
  ledger all hold up with a real model on the other end. What is still untested:
  a delegated task through `claude -p` or `opencode run --auto` with our MCP
  server as the agent's own tools (`orchestrator/runner.py`), and any live run
  through the HTTP provider adapters.
- **The planner against a real model.** The validator is tested with a
  deliberately bad plan; the prompt has not been given to a live planner.
- **Cross-family verification against a real model.** The prompt and the
  evidence rendering are exercised with `--show-prompt`; the model call is not.
- **`proof.browser_exec`.** Correct only if playwright is installed in the same
  interpreter; otherwise it refuses with instructions. The refusal path is
  exercised, the execution path is not.
- **`proof.oob_start` / `oob_check`.** The collector starts and records; no
  target has called back to it in this repository yet.
- **`recon.subdomains`, `scan.nikto`, `fuzz.params`.** Wrappers over tools that
  are installed but were not run against a live target during the build.

## Not built

- **A second transport for MCP.** stdio only. Streamable HTTP would let a remote
  client drive the broker, and is the right next step for a team.
- **Depth skills for 7 classes.** `skills/INDEX.md` lists them by name:
  `graphql-exposure`, `cache-poisoning`, `csrf`, `prototype-pollution`,
  `open-redirect`, `file-upload-rce`, `log4shell`. Each has a proof requirement
  and a probe ladder whose last rung names the tool that satisfies it; what is
  missing is the written-down method.
- **A measured case that a second run is cheaper.** Cards of its own now exist:
  `knowledge.chain_write` harvests one per confirmed finding, validation refuses
  a card carrying a hostname, an address, a credential or proof output, and
  `knowledge.chain_match` ranks the two corpora separately. What has **not**
  happened is a run that reused a card on a second target, so "the second run
  against a stack is cheaper than the first" is a design claim with no
  measurement behind it — the same column as the five research baselines.
- **The measurement half of the research claims.** `ARCHITECTURE.md` section 6
  lists five claims with their baselines. `test/baselines.py` now runs the
  offline half, and it is worth being exact about how much that is:

  - **Claim 1, the admission gate**, has a real A/B: the same scripted action
    sequence with only the write path switched. That is one variable.
  - **Claim 2, the external controller**, does not. It compares three
    hand-written drivers that differ in more than whether they consult the
    controller, and the script says so in its own closing block.
  - **Claims 3, 4 and 5** — the scope-gate count, routing versus one strong
    model, and cross-family review — need live models and have not been run.

  And the whole harness measures what the *gate* does to a given sequence of
  actions, not what a model would do: the subject under test is a scripted
  driver. That framing is in the file's docstring and in its output, because a
  number that overclaims is worse than no number.
- **A learning loop.** Nothing updates the routing hypotheses in
  `models.json` from measured outcomes. Today they are edited by hand.
- **Attack-defense and post-incident planes.** The evidence policy's defensive
  grades (`evicted-verified`, `absent-within-coverage`) are not implemented;
  this system only makes offensive claims.
- **The authenticated flows a session store does not reach.** The store, the
  login replay, the refresh and the two-identity differential exist
  (`argus/ledger/identities.py`, the `session` server). What is still missing is
  everything stateful *around* a credential: re-reading a CSRF token per
  request, an OAuth or SAML round trip, a per-request nonce, and a login that
  needs a second factor. Those are the flows that make a real engagement's
  authenticated half slow, and none of them is covered.

## The order I would build next

1. **Run the three live baselines.** Deterministic plan versus model plan, one
   strong model versus a routed fleet, same-family versus cross-family review —
   on the fixture and one lab estate. The two offline ones are done; these three
   are what turn the argument for the design into a measurement.
2. **One live delegated task** through each CLI backend, so the two cheapest
   paths to a subscription are tested rather than plausible.
3. **The stateful authenticated flows** — a CSRF token re-read per request, an
   OAuth round trip, a second factor. The session store made the simple cases
   work; these are the ones a real engagement actually hits.
4. **Reuse a chain card on a second target**, which is the measurement the
   corpus does not have yet.
5. **Depth skills for the remaining seven classes**, `cache-poisoning` and
   `csrf` first: both have tools and ladders and no written method.
