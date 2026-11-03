# argus

An evidence-gated, multi-model penetration-testing agent system.

A model decides what to try. A broker decides what may run. A ledger decides
what may be called a finding. Those are three separate programs on purpose, and
the separation is the whole design: it is what makes an LLM-driven tester safe to
automate and its output worth reading.

```
operator  ──prompt, skill or workflow──▶  LLM
                                          │  reads: the ledger digest + the controller's next action
                                          ▼
                                    MCP tools/call
                                          │
                                 ┌────────▼─────────┐
                                 │   broker         │  scope · risk tier · hypothesis · budget
                                 └────────┬─────────┘  every gate fail-closed
                                          │  argv only — there is no shell
                        ┌─────────────────▼──────────────────┐
                        │ nmap ffuf nuclei nikto sqlmap curl │
                        │ playwright · per-CVE scripts       │
                        └─────────────────┬──────────────────┘
                                          │  observation, bounded and redacted
                                 ┌────────▼─────────┐
                                 │   ledger         │  evidence · hypotheses · budgets
                                 └────────┬─────────┘  graded by the proof matrix
                                          ▼
                     report: confirmed · candidate · not demonstrated
```

Above that, when one model is not enough:

```
objective ─▶ planner (the strongest model, once) ─▶ plan.json + tasks/
                                                        │
                     router ──by strength and cost──────┤
                                                        ▼
            harness (our loop)  ·  claude code  ·  opencode     ← all three on the same MCP tools
                     └──────────── one ledger, one decisions store ─────────────┘
```

## What it refuses to do

This is the part worth reading first, because it is what the rest is built
around.

- **It cannot reach a target the scope does not name.** An empty scope allows
  nothing. A deny rule beats any allow rule. The check is at the broker, so a
  hallucinated hostname produces a refusal, not a request.
- **It has no shell.** Every tool is an argv list. A model that writes
  `; rm -rf /` into a parameter produces a tool argument.
- **It cannot record a finding it did not demonstrate.** Each class has a proof
  requirement, and the ledger refuses anything that does not meet it. Code
  execution is proven by `id; echo <nonce>` — never a reverse shell, never a
  write. A SQL injection is proven by the DBMS fingerprint plus one named table
  and at least one row; five rows is a proof and a full dump is an incident.
- **It cannot spend an afternoon on payload variants.** Six probes per class,
  then the controller forces a change of strategy rather than a change of payload.
- **It does not test denial of service.** That class is refused by construction:
  the proof would be the damage.

## Quickstart

No dependencies beyond the Python standard library and whichever pentest tools
you already have.

```bash
# 1. the engagement, with its scope and its authorisation on the record
./bin/argus open acme-dmz \
    --objective "web foothold on the DMZ portal" \
    --in-scope 172.31.66.0/24 --out-of-scope 172.31.66.1 \
    --ports 80 443 8080 --tiers passive active intrusive \
    --authorisation "signed SoW 2026-11-01, window 09:00-18:00, contact ops@acme"
./bin/argus target acme-dmz http://172.31.66.10/

# 2. what happens next is computed from the ledger, not from a conversation
./bin/argus next acme-dmz

# 3. one model, one loop
./bin/argus agent acme-dmz --model claude-sonnet-5-5

#    or a fleet: plan with the strongest model, route the rest by strength and cost
./bin/argus plan acme-dmz
./bin/argus run  acme-dmz --policy balanced --parallelism 3

# 4. have a different model family read the evidence, then write the report
./bin/argus verify acme-dmz
./bin/argus report acme-dmz --write

# 5. what it cost and what it bought
./bin/argus metrics acme-dmz
```

To drive the tools from any MCP client instead — Claude Code, opencode, an IDE:

```bash
./bin/argus mcp all --engagement acme-dmz     # 57 tools over stdio
claude mcp add argus -- python3 -m argus.broker.serve all --engagement acme-dmz
```

## Try it with no target and no API key

The repository ships a deliberately vulnerable fixture, bound to loopback, with
one planted weakness per class:

```bash
bash test/run_all.sh
```

The end-to-end layer opens an engagement against the fixture and proves SQL
injection, command injection, arbitrary file read, expression injection and IDOR
with real tools — `sqlmap` really does dump the table — then checks that a
reflected XSS payload is recorded as a **candidate** rather than a finding,
because no browser confirmed execution.

## Layout

| Path | What lives there |
|---|---|
| `argus/ledger/` | scope, state, the proof matrix, the decision controller, the only write path |
| `argus/broker/` | the MCP server framework and eight tool servers |
| `argus/runtime/` | the agent loop, one profile per model, one adapter per provider |
| `argus/orchestrator/` | planner, router, scheduler, runners, the shared context bus, verification |
| `argus/knowledge/` | probe ladders, per class, as data |
| `skills/` | the written-down method, one file per class or activity |
| `workflows/` | reusable plan templates |
| `scripts/exploits/` | the per-CVE script registry, with a template |
| `test/` | the gate, the fixture, the proof-matrix cases |
| `engagements/` | one directory per engagement: ledger, evidence, transcripts, logs, report |

Read `ARCHITECTURE.md` for how the planes fit together and what each one is
measured on, and `EVIDENCE_POLICY.md` for what may be claimed.

## The models

`argus fleet` prints what is reachable on this machine and what each kind of task
would route to. Nothing is hard-coded: `argus/runtime/profiles/models.json`
holds one profile per model — step budget, observation cap, how often the
contract is restated, whether several tool calls in one turn are safe, the cost —
and the `strengths` lists are **routing hypotheses to be measured**, not
measurements. Correcting one is a JSON edit.

Under the default `balanced` policy: the planner and the reviewer keep full
capability, and breadth, triage and long-context reads go to the cheapest
reachable model. A plan written by the cheapest model is a false economy, because
it is the one artifact the whole engagement is shaped by.

## Authorisation

Authorised testing only: your own systems, a lab, a CTF, or an engagement with
written permission whose scope you have entered above. The intrusive tier refuses
to open without an authorisation note naming who authorised it and over what
window — not because a note makes testing legal, but because an engagement that
cannot produce one should not be running.

## Honest limits

- **Routing is heuristic.** Keyword and role matching is not proof that a model
  is better at a task. The numbers in `models.json` are a starting point.
- **A proof requirement is a floor, not a ceiling.** It stops the common false
  positives. It cannot stop a well-constructed wrong conclusion, which is what
  cross-family verification is for, and that too is a check rather than a
  guarantee.
- **The collector is local.** Blind classes are provable in a lab or on an
  internal engagement, and need an external collector the client approves for an
  internet target.
- **`argus/broker/exec.py` is not a sandbox.** It is argv-only with timeouts and
  output caps; a tool it runs can still reach the filesystem and the network.
- **The scope is checked as written.** `resolve: true` additionally checks
  resolved addresses, and an engagement that cares about DNS rebinding must
  enable it.
- **Nothing here understands the whole engagement.** The plan, the decisions
  store and the ledger are on disk precisely because no model does.
