---
name: orchestration
description: Run several models as one tester — what the planner does, how tasks are routed by strength and cost, how the shared context prevents drift, and when a fleet is the wrong answer. Use when deciding which model does what, when a plan needs writing, or when an engagement is big enough to parallelise.
---

# Orchestrating a fleet

```
argus plan acme-dmz                     # the strongest reachable model writes the plan
argus run acme-dmz --policy balanced --parallelism 3
argus verify acme-dmz                   # a different family reads the evidence
```

## The decomposition that makes a fleet worth it

Any engagement splits into two parts.

**The spine** is the chain that actually reaches the finding. Each step depends
on the answer to the one before, so nothing compresses it — and it is almost
always short.

**The mass** is everything else: proving that fifteen other inputs are *not* it,
reading a bundle, researching a version, writing a tool. None of it depends on
the rest, and this is where the hours go.

A fleet speeds up the mass and does nothing for the spine. So the ratio decides
the gain: an engagement that is mostly spine barely moves; one that is mostly
mass — which is what a hard one looks like — moves by roughly the number of
agents you keep busy.

**The test for whether you are orchestrating or just delegating: at any moment,
is anything running that you are not doing yourself?**

## What each layer is for

| layer | job | why it is separate |
|---|---|---|
| planner | objective → tasks on disk | the most expensive tokens, spent once, on the decision that shapes everything after it |
| router | task → runner, model, mode | cost is decided here, and it is the only place that knows what is reachable |
| scheduler | dependencies, slots, expansion | fills a free slot the moment it opens, rather than draining a wave |
| ledger | the memory | an agent that joins at task nine reads it instead of being told |

## Routing, and the two rules that are not negotiable

- **Review is cross-family.** Two models that agree because they share a prior
  are not a check. The router excludes the family that produced the finding.
- **Breadth goes to the cheapest capable model; judgement does not.** Under the
  balanced policy, `breadth`, `triage` and `long_context` roles take the cheapest
  reachable candidate, and `planner`, `reviewer` and `report` keep the declared
  order. A plan written by the cheapest model is a false economy: it is the one
  artifact the whole engagement is shaped by.

`argus fleet` prints what is reachable here and what each task kind would route
to. The strengths in `argus/runtime/profiles/models.json` are **routing
hypotheses**, not measurements — correcting one is a JSON edit.

## The planner's one job

Read the ledger, write tasks, stop. A planner that starts probing produces a
diffuse plan and spends the most expensive tokens in the engagement on the
cheapest work. The plan is validated before it runs: out-of-scope targets
dropped, classes checked against the proof matrix, refused classes removed,
dependency cycles rejected. `argus plan --deterministic` writes the baseline plan
with no model at all, which is also the control condition for asking whether the
planner earned its cost.

## Preventing drift without a bigger context window

Nothing understands the whole engagement. What exists instead:

- `decisions.json` — the small set of things later agents must not silently
  contradict, each with an author and a rationale, so disagreement happens *with
  the reason in front of it*.
- `tasks/<id>/brief.md` and `report.md` — the handoff. A task that cannot be
  described in a brief is not a task yet.
- the ledger — every probe, every evidence record, every refusal.

A new agent reads a digest of those three, not a transcript. That is why a run
can be interrupted, handed to a different model, or resumed tomorrow.

## Keeping the pipe full

- Launch the breadth wave **before** driving the spine yourself, not after.
- Ask every independent question at once, not in the order they occurred to you.
- Speculate ahead of the spine: put agents on the layers you will need *if the
  current step dies*, because most steps die.
- The moment a task lands, start the next one — skim for anything that breaks a
  falsifier, launch, then read properly.
- One agent costs minutes whatever the task. Never hand one something you could
  finish in less.

## When a fleet is the wrong answer

- The engagement is one target with three parameters. Run one agent.
- The spine is the whole problem — a single chain where every step needs the
  previous answer. Parallelism buys nothing and the coordination costs real
  tokens.
- A known chain matches. `knowledge.chain_match` first: a known answer beats any
  number of parallel guesses.
