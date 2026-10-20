# `.claude/workflows/` — the fan-out, automated

What these files are for, in one sentence: `tools/subagent_fanout.py` only
**prints** briefs, and everything between "briefs printed" and "ledger written"
was manual. These close that gap.

## The measurement that justifies them

Walked end to end, the path from a web challenge to a flag was **13 steps, of
which 3 were automatic** — the fan-out print, `--validate`, and `--merge`. The
other ten were done by hand:

- every brief was read and pasted into an `Agent` call, one per family, and the
  concurrency existed only if a human remembered to put them in **one** message;
- every returned report was pasted into a file, because the agents answer in
  chat while `--validate` and `--merge` read paths off disk;
- every emitted `hooks.py post-probe` line was hand-edited to add
  `--hypothesis-id`, then run one at a time.

Against a **7 to 10 minute** spawn-to-report floor per agent, that hand-work is
the dominant cost in a wave.

## The two workflows

| Workflow | Use it for | Fleet shape |
|---|---|---|
| `web-sweep.js` | one authorized web challenge | **measure-only**: the `ctf-web-*` families hand back measurements, the main thread chains them |
| `solver-fleet.js` | crypto, pwn, rev, osint, misc | **solver**: the chain lives inside one family, so the agent may carry it to a flag |

```
Workflow({ name: 'web-sweep',
           args: { challenge: 'acme', handout: 'challenges/acme/src',
                   target: 'http://10.0.0.5:3000/' } })

Workflow({ name: 'solver-fleet',
           args: { challenge: 'nameless', category: 'crypto',
                   handout: 'challenges/nameless' } })
```

DFIR still fans out through `tools/subagent_fanout.py --dfir` by hand; the eight
`ctf-dfir-*` agents and `skills/dfir-parallel-sweep/SKILL.md` are unchanged.

## What they do that a human reading briefs did not

- **Short-circuit on a strong chain card.** `subagent_fanout` already computes
  `strong_chain_match`. When it is set, `web-sweep.js` returns that card's own
  probe and spawns **nothing** — a known answer beats ten parallel guesses, and
  the guesses cost 7-10 minutes each.
- **Check the handout is on disk first.** Twelve minutes were once lost
  reconstructing a 236-line source file over HTTP while it sat in the handout
  directory. That `ls` is now step one of the Brief phase.
- **Spawn by evidence, not appetite.** A family whose `source_signals_that_fired`
  is empty is parked, not run. With no source present nothing can fire, so a
  black-box target sweeps wide instead.
- **Kill the report-staging gap.** Passing the fan-out contract as a `schema`
  makes each agent return a validated object instead of chat text, so nothing
  has to be pasted into a file by hand.
- **Prove a flag against its own bytes.** `solver-fleet.js` checks, in plain
  JavaScript with no agent in the loop, that the claimed flag string literally
  appears inside the claimed evidence. A candidate that fails is downgraded
  before a human sees it. This is narrower than proving the bytes came from the
  target — nothing offline can do that — but it catches the failure that
  actually happens, a flag reconstructed from memory.

## What they deliberately do not do

**They never write `challenges/<name>/state.json` and never run
`tools/hooks.py`.** Both return `commands_for_the_main_thread`.

The reason is concrete, not ceremonial: `tools/decide.py` enforces 25 probes per
challenge, and ten agents recording probes in parallel would spend that in one
round and force a class switch on classes nobody worked. Agents measure; the
main thread records. A flag is a **candidate** until `pre-flag` accepts it with
its verbatim excerpt.

Two regression tests hold this in place:

- `test_every_workflow_script_spawns_an_agent_that_exists` — `agentType`
  resolves against `.claude/agents/`, and a typo fails the spawn mid-wave after
  the earlier agents have already cost their minutes. The fleet lists are
  duplicated in the scripts because the workflow sandbox has no filesystem, so
  the duplication is proven rather than trusted.
- `test_no_workflow_script_delegates_the_ledger` — a script that handed the gate
  to a subagent would look like a speed-up and would silently disable the
  controller.

## Sandbox constraints these scripts are written around

- **No filesystem and no Node API.** A script cannot run
  `subagent_fanout.py` itself; a cheap agent does it in the first phase.
- **`Date.now()`, `new Date()` and `Math.random()` all throw.** Nothing here is
  timed or randomised.
- **`meta` must be a pure literal** — no variables, no interpolation.
- **Concurrency is capped at `min(16, cpus - 2)`.** Past that agents queue, and
  a queued agent is serial time wearing a parallel costume. This is why
  `tools/contest/dispatch.py` plans 2 to 3 challenges at a time rather than ten.

## Scope

Authorized CTF and lab work only, and only the host and port the challenge
supplied. These workflows orchestrate; they decide no bug class and attack
nothing on their own initiative.
