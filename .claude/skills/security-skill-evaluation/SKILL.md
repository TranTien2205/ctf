---
name: security-skill-evaluation
description: >
  How to tell whether a skill in this library is actually getting better. Use
  when adding a skill, promoting a field note, raising a class from catalogue to
  verified, or deciding that a skill has stopped earning its place.
tags: [meta, evaluation, skill-quality, ctf]
environment: [ctf, lab]
evidence_level: catalogue
---

# Skill evaluation

A growing skill library is not automatically a better one. Without a measure, a
library grows toward whatever is easiest to write, and the cost — context spent
opening it, and hypotheses anchored by it — grows with it.

This skill is the measure. `test/run_all.sh` enforces the mechanical half;
everything below is the judgement half.

## What the gate already checks

Do not re-check these by hand:

- every skill on disk is in `skills/registry.json`, and every registry path exists
- `skills/INDEX.md` names no file that is missing
- no documentation references a tool that does not exist
- the control plane stays English
- chain cards are well formed and carry no flags
- counts never fall below `test/baseline.json`

## The four questions the gate cannot answer

**1. Can an agent tell when to open it, from the description alone?**
If the description needs the body to disambiguate, the router will mis-select it.
Check against `do_not_use_when` in the registry: a skill with no honest
"do not use when" is usually too vague to route to.

**2. Does it shorten the path to a probe?**
A skill earns its place by producing a decisive action sooner. If it mostly
restates what the router already said, it is a reference file, not a skill.

**3. Is its evidence level honest?**
`verified` requires a chain card in `knowledge/chains/` that names the class.
`catalogue` must say plainly that nothing here has solved one. A catalogue skill
presented as experience is the fabrication this whole system is built against.

**4. Does it cost what it claims?**
`skill_tokens` in the registry is bytes divided by four. A router that has grown
past roughly 1,200 tokens has stopped being a router.

## Measuring the library over time

The honest metrics are in `test/capability_report.py` and, for classes, in
`knowledge/bug-classes.json`:

| Metric | What it tells you |
|---|---|
| classes at `verified` vs `catalogue` | how much of the taxonomy is backed by a real solve |
| chain cards | how much is reusable next time |
| `confirmed` vs `proposed` field notes | whether the learning loop is being reviewed or just accumulating |
| lines in `knowledge/classify-misses.log` | shapes the taxonomy cannot name yet — the backlog |
| routing golden cases passing | whether a change to signals broke a shape already met |

A library improving looks like: catalogue classes converting to verified, the
miss log shrinking as classes are added, field notes moving from proposed to
confirmed. A library rotting looks like: more skills, same verified count, a
growing pile of unreviewed proposals.

## Evaluating against a task

Take a challenge already in `solved/` and check whether the current library would
have routed to the right class from the evidence available **before** the solve,
not after. `test/cases/classify.json` holds exactly that set. Adding a case after
each solve is what keeps this measurement honest; the templates are in
`references/eval-task-templates.md`.

## When to delete a skill

Delete when a skill has been in the library through several relevant challenges
and was never opened, or was opened and did not change the next action. Record
why in the commit message — a deletion without a reason will be re-added by
someone six months later.

Never delete a test case to make a change pass. That is the one move the gate
cannot catch.

## References

- `references/skill-quality-rubric.md` — per-skill structural rubric
- `references/eval-task-templates.md` — known-answer task shapes for evaluation

## Routing

Learning loop and review flow: `../../LEARNING_LOOP.md`. Registry and load policy:
`../INDEX.md`.
