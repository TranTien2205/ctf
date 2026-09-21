# CTF Solver Training Protocol

This document defines how to train and evaluate the CTF solver system across
many authorized challenges. It is challenge-agnostic: a challenge may be
white-box or black-box, web or binary, easy or difficult, but every run follows
the same evidence and learning rules.

The objective is not to collect writeups. The objective is to reduce the time
to the first useful signal, choose better first probes, avoid unsupported
claims, and make weaker models follow the same reliable process as stronger
models.

## 1. Scope and safety

- Use only authorized jeopardy CTF, attack-defense, and lab targets.
- This protocol is for challenge solving, not machine-box, Active Directory, or
  unrelated red-team operations.
- A target URL, source tree, binary, capture, or artifact must be supplied by
  the challenge or operator.
- Do not commit credentials, access tokens, real flags, or sensitive target
  state. Redact them in notes and chain cards.
- Stop if the next action would affect an unauthorized target, destroy shared
  state, or exceed the challenge scope.

## 2. Training modes

Every run declares one mode before the first probe. Do not mix metrics from
different modes.

| Mode | Purpose | Writeup before flag | Source policy |
|---|---|---:|---|
| `blind` | Measure independent solving | No | Read only if officially supplied |
| `source-assisted` | Measure white-box reasoning | No | Read supplied source before probing |
| `guided` | Train a weaker model with controlled help | No full writeup | Use the hint ladder only |
| `retrospective` | Extract reusable knowledge from a known solve | Yes, after an attempt | Source and writeup may be compared |
| `writeup-assisted` | Fast coverage when independent measurement is not needed | Yes | Mark as non-independent |

The default benchmark mode is `blind`. A writeup-assisted run must never be
used as evidence that blind-solving ability improved.

## 3. Challenge run contract

Before starting a challenge, create a run record with these fields:

```json
{
  "challenge": "stable-name",
  "category": "web|pwn|rev|crypto|forensics|osint|misc|ai",
  "target": "authorized-target-or-artifact-path",
  "mode": "blind",
  "source_officially_supplied": false,
  "writeup_used_before_flag": false,
  "model": "model-name",
  "started_at": "ISO-8601",
  "time_budget_minutes": 30,
  "hint_level": 0
}
```

The initial observation must be captured exactly as it was available before the
solve. Do not rewrite it using knowledge learned later.

## 4. Required solver sequence

All modes use the same control loop. Only the information available to the
solver changes.

```text
bootstrap
  -> classify
  -> dispatch
  -> chain_match
  -> create or open state
  -> decide
  -> pre-probe
  -> execute exactly once
  -> post-probe
  -> decide again
  -> confirm or falsify through hooks
  -> verify the flag through hooks
  -> record the solve or stop honestly
```

Start with:

```bash
python3 selfcheck.py
python3 tools/classify.py "<initial observation>"
python3 tools/skill_select.py "<initial observation>"
python3 tools/chain_match.py "<initial observation>"
python3 tools/state.py <challenge> --category <category> --target <target>
python3 tools/decide.py <challenge>
```

For an official source artifact, use the white-box path:

```bash
python3 tools/classify.py --source <source-dir>
python3 tools/skill_select.py --source <source-dir>
python3 tools/chain_match.py --source <source-dir>
```

After every recorded probe or flag event, run `tools/decide.py` again. The
controller's action, rationale, and commands are authoritative for the next
step. Do not invent a replacement command when the controller provides one.

## 5. White-box training

When source is officially supplied, the solver should read it. Hiding supplied
source would measure the wrong skill and would turn a white-box challenge into a
different black-box challenge.

Read source in this order:

1. Entrypoints, routes, handlers, and input boundaries.
2. Authentication and authorization checks.
3. Datastore queries, parser calls, subprocess calls, template rendering, and
   outbound requests.
4. Flag path or solved condition, if present in the artifact.
5. Relevant frontend JavaScript or configuration.

The solver must record file and line evidence before selecting a payload. It
must distinguish:

- Candidate sink versus reachable sink.
- Suspicious code versus a confirmed vulnerability.
- Flag-shaped content in source versus a flag read from the supplied artifact.

Do not open the entire depth corpus after reading source. Classify, run the
cheapest confirming probe, then open one depth skill and one named reference.

## 6. Blind training

In blind mode, the solver may use only:

- The challenge statement.
- The supplied target and permitted artifacts.
- Responses, headers, frontend assets, and errors observed during the run.
- Existing verified chain cards whose preconditions match.
- The selected skill and its permitted references.

Do not search for or read the challenge writeup before the flag. Do not retrieve
private source that the challenge did not provide. A source disclosure found
through an observed, authorized vulnerability is a valid in-run step and must
be recorded as evidence.

## 7. Guided training and hint ladder

Guided mode is for improving weak-model reliability without giving away the
solution. Give at most one hint, then let the solver execute the next control
loop iteration.

| Hint level | Allowed assistance |
|---:|---|
| 0 | No hint; normal autonomous attempt |
| 1 | Ask the solver to reread observed evidence and frontend/source |
| 2 | Point out a competing class or mechanism layer, without a payload |
| 3 | Identify the relevant first probe from the selected skill |
| 4 | Identify an observed source file, route, parameter, or response field |
| 5 | Provide a payload shape or chain step after the solver has logged the blocker |
| 6 | Provide the relevant writeup section; do not claim independent success |

The hint level must be recorded. If the solver cannot progress at level 5, stop
the run and use it as a training failure instead of dumping the full writeup.

## 8. Writeup policy

Writeups are valuable for retrospective learning but harmful when mixed into a
blind benchmark.

After a blind or source-assisted attempt reaches `record_solve`, `stop_report`,
or its time budget, compare the trace with the writeup:

1. Identify the first point where the solver diverged from the successful path.
2. Identify which pre-solve signal was available but ignored.
3. Identify whether the first probe or falsifier was wrong.
4. Identify whether the failure was classification, dispatch, execution,
   evidence handling, or time management.
5. Convert only the generalizable lesson into a skill, taxonomy signal, chain
   card, or test case.

Never copy a final payload into a skill without recording the first probe that
opened the chain. Never treat a writeup claim as evidence for the current
target.

## 9. Probe and evidence discipline

For every probe:

```bash
python3 tools/hooks.py pre-probe <challenge> --request '<exact request>'
# execute the probe once
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> \
  --class <taxonomy-class> \
  --request '<exact request>' \
  --verdict confirms|falsifies|inconclusive \
  --evidence-kind surface|class|impact|transport \
  --evidence '<verbatim response excerpt>'
python3 tools/decide.py <challenge>
```

Rules:

- A timeout, reset, empty response, or HTTP 000 is `inconclusive`.
- Every probe must identify one open hypothesis and matching taxonomy class.
- `confirms` requires a verbatim response excerpt and
  `--evidence-kind class|impact`; a `surface` response such as a login redirect,
  registration success, or form render is not class evidence.
- A flag enters state only through `hooks.py pre-flag`.
- A write-shaped probe requires blast-radius review and `--write-ack`.
- Test first on an object or account created by the solver.
- Do not run a sixth probe in one exhausted mechanism class.
- Clean up temporary objects, listeners, files, and processes after the run.

## 10. Run trace and postmortem

Each run should preserve a redacted trace containing:

```json
{
  "initial_observation": "exact pre-solve text",
  "classification": ["candidate classes and evidence"],
  "chain_matches": ["candidate cards and confirmed preconditions"],
  "probes": [
    {
      "class": "web-ssrf",
      "request": "redacted exact request",
      "verdict": "inconclusive",
      "transport": "timeout",
      "evidence": "redacted response excerpt",
      "hint_level": 0
    }
  ],
  "controller_actions": ["new_hypothesis", "run_probe", "stop_report"],
  "flag_verified": false,
  "writeup_used_after_attempt": true
}
```

The postmortem must answer:

- What was the first useful signal?
- Was the first probe discriminating?
- Which class was first selected and was it correct?
- Which hypothesis was parked and why?
- What was the highest hint level required?
- Did the solver make any unsupported confirmation or flag claim?
- What should change in the system, if anything?

## 11. Metrics

Track these metrics separately for each mode and model:

```text
routing_accuracy
classification_top1_accuracy
classification_top3_recall
negative_case_precision
first_probe_accuracy
first_decisive_probe_rate
median_time_to_first_signal
median_probes_to_confirmation
wrong_class_rate
unsupported_confirmation_rate
false_flag_rate
chain_match_precision
chain_probe_reuse_rate
writeup_dependency_rate
average_hint_level
classify_miss_backlog
field_note_review_latency
```

The most important practical metrics are:

- `first_decisive_probe_rate`: whether the first action produces a useful
  distinguishing signal.
- `writeup_dependency_rate`: how often the solver needs a writeup before the
  flag in blind/source-assisted runs.
- `average_hint_level`: how much intervention weaker models require.
- `unsupported_confirmation_rate` and `false_flag_rate`: safety and evidence
  discipline.

## 12. Dataset split

Maintain four separate datasets:

| Dataset | Writeup before run | Purpose |
|---|---:|---|
| `training` | Allowed | Improve skills, prompts, and references |
| `validation` | No | Tune against known shapes without direct answers |
| `holdout` | No | Detect overfitting and measure generalization |
| `regression` | No | Protect behavior that already worked |

Every solved challenge should add its pre-solve observation to the relevant
golden cases. Never delete an old case merely to make a classifier pass.

## 13. Learning-loop promotion rules

After a flag is verified:

```bash
python3 tools/validate_card.py knowledge/chains/<id>.json
python3 tools/classify_solve.py --chain <id>
python3 tools/learning_report.py
python3 tools/classify_solve.py --review
bash test/run_all.sh
```

A field note remains `proposed` until its chain card and exact evidence have been
reviewed. A catalogue class may become `verified` only when:

1. The chain card is valid and flag-free.
2. The flag passed `hooks.py pre-flag` from a live response or artifact.
3. The first probe that opened the chain is identified.
4. The field note is human-confirmed.
5. A pre-solve golden case is added.
6. Legacy regression and system evaluation pass.

Do not promote a class because a final exploit payload happened to work.

## 14. Update and regression protocol

Every system update follows this order:

1. Run the current gate and save its output as the pre-change baseline.
2. Make one coherent change.
3. Run `python3 -m py_compile` on changed Python files.
4. Run `git diff --check`.
5. Run `bash test/run_all.sh`.
6. Inspect the capability report, system evaluation, audit, and learning report.
7. Confirm that `CLAUDE.md`, `AGENTS.md`, and `.claude/skills` still expose the
   same system to all supported agents.
8. Save a tagged version only after every required gate passes.

The legacy baseline is never raised manually to hide a regression. New metrics
must be added as tests first, then improved through real training runs.

## 15. Recommended curriculum

Start with a calibration set of 10–15 authorized challenges:

- A mix of white-box and black-box challenges.
- Several categories, not only web.
- Some challenges with verified local chain cards.
- Some challenges with no matching chain.
- At least one negative or ambiguous classification case.

Use approximately:

```text
50% blind
30% source-assisted
20% guided or retrospective
```

After calibration, move toward:

```text
70% blind
20% source-assisted
10% guided or retrospective
```

The system is improving when the same challenge shape requires fewer probes,
less help, and fewer unsupported claims—not merely when the skill directory has
more files.

## 16. AI operating modes and tool trust

The solver must label the role it is using for each action:

| Role | Allowed behavior | Trust level |
|---|---|---|
| `reader` | Extract routes, constants, strings, functions, sinks, and exact output | Highest, when quoted from an artifact or tool output |
| `writer` | Create a probe, script, harness, query, or solver | Medium, verified by executing it and capturing raw output |
| `hypothesizer` | Propose classes, chains, or explanations | Lowest, never evidence by itself |

The rule is: **the agent proposes; the machine verifies**. A model summary is
not a substitute for the raw tool output. A generated script is not correct until
it runs against a known input or a controlled target response.

For web challenges, the same separation applies:

- `reader`: extract routes, parameters, headers, templates, queries, and sinks.
- `writer`: create a bounded request, parser test, replay script, or response
  comparator.
- `hypothesizer`: propose SSRF, XSS, SSTI, IDOR, cache deception, or another
  class, but never promote it without a distinguishing response.

## 17. Tool layers and permissions

Treat available tools as three layers:

1. **Static read** — source, disassembly, decompilation, strings, xrefs,
   configuration, and local artifacts.
2. **Dynamic measurement** — HTTP requests, debugger/emulator runs, browser-bot
   visits, process traces, and response capture.
3. **Write/execute** — state changes, patches, payload submissions, filesystem
   writes, database mutations, and shell commands.

Start with static read. Use dynamic measurement only for a stated hypothesis.
Use write/execute only after scope and blast radius are recorded. Every dynamic
measurement must preserve raw output; every write must be reversible or limited
to an object created for the run.

Before using an unfamiliar MCP or external tool, ask it to list its available
capabilities grouped by read, dynamic, write, and execution permissions. Do not
enable a debugger, shell, patch, or write surface merely because it is available.

## 18. Stop conditions and anti-drift summaries

Each autonomous run has a one-sentence verifiable goal. After four tool calls,
write a one-line checkpoint containing:

- The current belief and the exact evidence supporting it.
- The hypotheses ruled out and the observation that ruled each one out.
- The single next controller action.

Stop and call `tools/decide.py` again when:

- Four consecutive calls ruled out nothing.
- The next value would have to be guessed instead of read.
- The raw tool output is missing.
- The current class budget is exhausted.
- The action would become a write without blast-radius acknowledgement.

This prevents context drift, repeated syntax variations, invented constants,
and model summaries that silently replace measurements.

## 19. Constants, offsets, and observed values

When recording a value from source or a tool:

- Preserve it verbatim.
- Do not round it or change its number base.
- State whether it came from source, a live response, a local execution, or a
  model hypothesis.
- If uncertain, write `UNKNOWN` and explain what observation is missing.

This applies equally to a binary offset, a crypto modulus, an HTTP status, a
cookie value, a route parameter, a database identifier, or a response length.

## 20. Harness and replay validation

When a model creates a solver, emulator, payload generator, or replay script:

1. Run it on a known input with a known output, when available.
2. Compare the raw output against the source or live response.
3. Change one input and verify that the output changes for the expected reason.
4. Save the command, input, output, and exit code in the run trace.
5. Only then use it for the challenge path.

For web work, a harness should first replay a harmless baseline request before
adding a marker or state-changing field. For reverse engineering, a harness
should first reproduce one observed basic block or function result before lifting
the full algorithm.
