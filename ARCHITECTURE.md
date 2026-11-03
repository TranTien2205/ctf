# Architecture

Four planes. Each one has a single job, a single way in, and something it can be
measured on. The reason for the separation is not tidiness: it is that an
LLM-driven penetration tester fails in four distinct ways, and each plane exists
to make one of those failures structurally impossible rather than unlikely.

| Failure | Plane that prevents it | How |
|---|---|---|
| touching something it was not allowed to touch | broker | scope and risk tier are checked before the command is built, fail-closed |
| reporting a vulnerability it never demonstrated | ledger | per-class proof requirements, enforced on the write path |
| spending an afternoon on payload variants | ledger | per-class probe and time budgets, then a forced change of strategy |
| losing the thread across a long engagement | orchestrator | the plan, the decisions and the evidence live on disk, not in a context window |

## 1. The pipeline, concretely

```
operator
  │  a prompt, a skill, or a workflow template
  ▼
LLM ───────────────────────────────────────────────────────────────┐
  │  what it is shown each step:                                   │
  │    · the session contract (four rules, restated on a cadence    │
  │      the model's profile chooses)                              │
  │    · the ledger digest: targets, surface, open hypotheses,      │
  │      probes by class, findings, budgets, strategies spent       │
  │    · the controller's next action, computed from evidence       │
  │    · the last few tool results verbatim, older ones collapsed   │
  ▼                                                                │
MCP tools/call  (57 tools, 10 servers)                               │
  ▼                                                                │
broker                                                             │
  │  pre_probe:  scope ─ tier ─ hypothesis exists ─ class matches   │
  │              ─ budget not spent                                 │
  │  exec:       argv only, own process group, timeout, output cap  │
  │  post_probe: evidence recorded, redacted, bounded               │
  ▼                                                                │
nmap · httpx · ffuf · nuclei · nikto · sqlmap · curl-equivalent     │
playwright · per-CVE scripts under scripts/exploits/                │
  ▼                                                                │
observation ───────────────────────────────────────────────────────┘
  │
  ▼
ledger: evidence graded by the proof matrix
  │
  ▼
report: confirmed · candidate with the missing check · not demonstrated
```

The loop closes at `observation`: the model's next decision is made from the
ledger, not from its own summary of what happened. That is the difference
between a session that can be interrupted and resumed by a different model and
one that cannot.

## 2. The ledger — the control plane

`argus/ledger/`

| Module | Job |
|---|---|
| `scope.py` | default-deny allowlist. Deny wins. An empty scope allows nothing. Optional resolution checking. |
| `state.py` | the engagement: targets, surface, hypotheses, probes, an evidence index, findings, budgets. Atomic writes; evidence bodies in their own files so the state stays small enough to show a model. |
| `proof.py` | the proof matrix: 21 classes, each with a requirement, the checks that make it a proof, and a verifier that reads evidence records. |
| `hooks.py` | the only write path. Six named refusals. Every verb takes an advisory lock, so parallel agents do not lose each other's writes. |
| `decide.py` | the decision controller: ten ordered rules, fail-closed, each naming the observation that triggered it. |
| `report.py` | three sections that never merge, plus coverage stated as a limit. |
| `lock.py` | one writer at a time per engagement, held across a JSON rewrite and never across a tool call. |

### The proof matrix is the centre of the system

A class is not a label; it is a requirement. `rce` requires the output of
`id; echo <nonce>` with the nonce matching the probe and nothing destructive in
the request. `sqli` requires the DBMS fingerprint plus a named table with at
least one row. `idor` requires two identities, a cross-read that names both the
actor and the subject, **and** the control that establishes what the answer
should have been. `xss` requires a browser that executed the payload —
reflection stays `supported` forever, which is correct.

Three grades: `proven`, `supported` (a real signal with a named missing check),
`unproven`. A fourth, `refused`, exists for classes this system will not prove at
all: `dos` is registered precisely so that asking for it returns a reason rather
than a scan.

`supported` is the grade that makes the system useful rather than merely strict.
It records what is real, names the one check that is missing, and hands the next
session a two-minute task instead of a paragraph of speculation.

### The controller externalises the one judgement models get wrong

Given a ledger, a strong model usually picks a reasonable next move. A weak one,
a tired one, or one whose context has drifted instead re-runs the last command
with a new payload, or writes a confident paragraph about something it has not
shown. From the outside those two cases are indistinguishable — unless the next
action is computed from recorded evidence, which is what `decide.py` does. The
model chooses the content of the move; the controller chooses its shape, and a
departure has to be stated.

When a class's budget is spent, the controller does not stop. It climbs a ladder:
reuse a known chain, reclassify the surface, research the stack, widen the
surface, fan out a fleet, hand off to a human. `stop_report` fires only when
every rung has actually been spent.

## 3. The broker — the tool plane

`argus/broker/`, 57 tools over 10 servers, each one declared once and reachable
two ways: over MCP stdio by any client, and in-process by our own harness. The
gate is in the framework, not in the tools, so a tool author writes the
measurement and gets scope, tier, hypothesis, budget, evidence and redaction
applied around it.

| Server | Tools |
|---|---|
| `http` | one request; a baseline/variant differential with a self-similarity check |
| `recon` | ports, service fingerprint, parameter discovery, javascript mining, passive subdomains |
| `fuzz` | content and parameter discovery, calibrated, wall-clock capped |
| `scan` | nuclei, nikto — candidates only, and every result says so |
| `exploit` | sqlmap in three bounded modes; the per-CVE script registry |
| `proof` | the class-specific proof tools, each carrying a nonce |
| `web` | the classes a single request cannot settle: race (both orderings in one call), cache poisoning (proven by the clean fetch), open redirect, CORS, GraphQL, upload |
| `session` | identities, login, token refresh, requests issued as a named identity, and the authorization differential with both its controls |
| `ledger` | the ledger as tools, including `add_evidence` for observations made elsewhere |
| `knowledge` | probe ladders, the proof matrix, skills, two chain-card corpora ranked separately, local CVE lookup |

Two properties worth naming:

- **Risk tiers.** `passive` reads indirect sources, `active` touches the target,
  `intrusive` changes state or executes code. An engagement enables a set; the
  broker refuses the rest. `proof.exec_marker` is intrusive, so proving code
  execution is a decision the engagement had to make in advance.

  A tier is a property of the **tool**, not of the payload, and the distinction
  matters: `http.differential` is `active`, and a variant of `host=127.0.0.1;
  sleep 2` reaches a shell on a vulnerable target and executes something. The
  intrusive gate governs whether this system will *prove* execution, not whether
  a request can cause it. An earlier version of this document said `active`
  "touches the target read-only"; that was a claim the code does not keep, and in
  a system whose gate checks that documentation names only things that exist, a
  doc describing behaviour the code lacks is the same class of defect.
- **`ledger.add_evidence`.** Evidence from outside the broker — a Burp request, a
  playwright session, a source read, a callback seen elsewhere — is graded by the
  same matrix on the same terms. This is what keeps the proof requirement from
  being a cage: it constrains what may be *claimed*, not which tools may be used.

## 4. The runtime — the harness plane

`argus/runtime/`

A general harness runs every model the same way and pays twice: the strong model
is held back by caps it does not need, and the weak one drifts because nothing
restates the rules often enough. So the loop is one piece of code and the
differences live in a profile:

| Field | Why it differs per model |
|---|---|
| `max_steps` | a model that holds a thread for forty steps and one that loses it at twelve |
| `observation_cap` | how much tool output it can read before the beginning falls out |
| `history_chars` | when compaction starts |
| `restate_contract_every` | weaker instruction-following needs the rules more often |
| `one_tool_per_step` | some models mis-sequence parallel calls; some do not |
| `tool_dialect` | native function calling, or a text protocol for a CLI backend |
| `cost_per_mtok` | what the router trades off |

Compaction is the interesting part: old tool results collapse to one line each
(tool, summary, evidence id) because the full record is on disk and can be
re-read with `ledger.read_evidence`. The ledger is the memory; the transcript is
a short working set.

Providers: Anthropic, OpenAI-shaped (OpenAI, DeepSeek, OpenRouter), Google, plus
two CLI agents used as stateless text models, plus a scripted mock so the loop
can be tested with no key and no network.

## 5. The orchestrator — the coordination plane

`argus/orchestrator/`

```
objective
  ▼
planner      one strong model, once. Reads the ledger, writes tasks, stops.
  │          Validated before it runs: out-of-scope targets dropped, classes
  │          checked against the matrix, refused classes removed, cycles rejected.
  │          `--deterministic` writes the same shape with no model, which is the
  │          baseline the model plan has to beat.
  ▼
router       task kind → role → candidates → (runner, model, mode).
  │          Two rules: review is cross-family, and breadth goes to the cheapest
  │          capable model while judgement does not.
  ▼
scheduler    a ready queue and fixed slots. A free slot is filled the moment it
  │          opens, rather than draining a wave. After each completion the plan
  │          expands from whatever the ledger now holds — one task per open
  │          hypothesis — so a plan written before recon can still be right.
  ▼
runner       three ways to execute one task, one brief for all three:
             · our harness, in-process, tightest control
             · claude code, its own loop, our MCP server as its only tools
             · opencode, the same arrangement, different credentials
  ▼
verify       a model from another family reads the evidence — never the first
             model's reasoning — and disagreement demotes the finding.
```

### What prevents context drift

Nothing understands the whole engagement. Three artifacts stand in for that:

- `decisions.json` — the small set of things later agents must not silently
  contradict, each with an author and a rationale, with history. Disagreement
  then happens *with the reason in front of it*.
- `tasks/<id>/brief.md` and `report.md` — the handoff. A task that cannot be
  described in a brief is not a task yet.
- the ledger — every probe, every evidence record, every refusal.

A new agent reads a digest of those three. That is why a run can be interrupted,
resumed, or handed to a different model.

## 6. What this system is for, as a research artifact

Five claims, each with the measurement that would support or refute it, and the
baseline it is measured against. The instrumentation for all five already exists:
`log/cost.jsonl`, `log/commands.jsonl`, `log/bus.jsonl`, the evidence directory
and the proof grades.

| Claim | Measurement | Baseline |
|---|---|---|
| An admission gate reduces unsupported findings | share of recorded findings that a blind human review rejects | the same models, same targets, no proof requirement |
| An external controller reduces wasted probes | probes per confirmed finding; repeat-payload rate within a class | the same models with the tools and no controller |
| A capability-scoped broker eliminates out-of-scope action | count of commands issued outside the declared scope | an agent with a shell |
| Routing by strength and cost beats one strong model everywhere | cost per confirmed finding, and findings missed | the strongest model for every task |
| Cross-family verification catches what same-family review does not | demotion rate, cross-family versus same-family | same-family second pass |

`argus metrics <engagement>` reads the instrumentation back: probes per confirmed
finding, the repeat-payload ratio per class, refusals by kind — including how many
times an agent tried to act outside the declared scope — cost per model and cost
per confirmed finding. It is a readout, not a score: every line of it is
meaningless without the baseline run in the last column.

The honest part of this table is the last column. Each row needs the baseline
run, not just the instrumented one, and `--deterministic`, `--policy` and
`--model` exist so that both halves are one command apart.

### Evaluation targets, cheapest first

1. `test/fixtures/vulnapp.py` — seven planted weaknesses, one per class, on
   loopback. Ground truth is exact, so precision and recall are computable. It is
   a fixture, not a benchmark: it cannot show whether the system generalises.
2. A local lab estate — the `acme-lab` style range: a chain across hosts, with a
   scoring script, where partial credit localises the gap.
3. Public deliberately-vulnerable applications, offline, in Docker.
4. An authorised engagement, which is the only setting that tests the parts a lab
   cannot: scope that matters, a client who reads the report, and a target nobody
   planted anything in.

## 7. What is deliberately absent

- **No autonomous flag submission, no autonomous reporting.** A human reads the
  report.
- **No persistence, no lateral movement tooling, no credential dumping.** The
  proof of code execution is `id`. Everything past that is an engagement decision
  a human makes.
- **No denial of service.** Refused by construction.
- **No "confidence score" on findings.** A grade is derived from checks that are
  listed; a number would hide them.
