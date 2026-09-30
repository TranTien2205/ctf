---
name: ad-patch-without-breaking-sla
description: >
  Close a bug in a live service without losing the availability score. Use in an
  attack-defense contest before the first patch and before every one after it.
  Covers where to patch — in front of the service or in its source — the
  before/after bracket that makes a regression impossible to miss, the rollback,
  and the four patches that are guaranteed to cost more than the exploit they stop.
tags: [process, method, attack-defense, defense, availability, patch, rollback, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "no green baseline was saved before the patch, so no comparison is possible"
    - "the comparison reports a regression: revert first, think second"
    - "the patch would remove a feature the organiser's checker exercises"
evidence_level: catalogue
---
# Patching without losing the SLA — Process Skill

**Catalogue method. Nothing in this repository has solved an attack-defense
contest.** One thing here IS measured, in this session, and it is the reason the
bracket below is written as two commands rather than one: a version of
`tools/ad/sla_check.py`'s `compare()` that walked only the *after* run returned
`safe to keep` when a check that used to pass had been **deleted or renamed** —
blessing precisely the failure the tool exists to stop. That is fixed, and there
are three selftest cases holding it fixed. Trust the bracket; do not trust a
memory of it.

## The asymmetry, and why it is deliberate

`--compare` blocks on one thing only: a check that **passed before and does not
pass now**, including a check that has vanished from the spec. It does not block on
a check that was already red, because that was not caused by your patch and
blocking on it would stop you patching at all.

Exit codes, which is what a script should branch on:

| Code | Means | Do |
|---|---|---|
| 0 | all green, no regression | keep the patch |
| 1 | a regression against `--compare` | **revert now**, diagnose after |
| 2 | something is failing but was already failing | your call |
| 3 | the spec itself is unusable — missing, unparseable, no checks | fix the spec |

## First action

Not the patch. The baseline:

```bash
python3 tools/ad/sla_check.py <spec>.json --save before.json
```

**Falsifier:** the baseline is not green. Then you are not patching a working
service — you are debugging a broken one, and a comparison against a red baseline
proves nothing. Fix availability first.

## The bracket

```bash
python3 tools/ad/sla_check.py <spec>.json --save before.json     # must be green
#   ... apply exactly ONE change ...
python3 tools/ad/sla_check.py <spec>.json --save after.json --compare before.json
echo $?
```

One change per bracket. Two changes in one bracket and a regression tells you
something broke without telling you which edit did it, and under pressure the
answer is to revert both — including the one that worked.

## Where to patch

Two places, and the choice is about how fast you can undo it, not about elegance.

**In front of the service** — a reverse proxy rule, a request filter, a firewall
rule with `nft` or `iptables`:

- Reverting is one line and needs no restart, which is its whole advantage.
- It cannot see anything the request does not carry. A bug reachable from an
  authenticated path, or triggered by state, is not stoppable from in front.
- It is where a blocked byte gets encoded around. A filter on `../` does not stop
  `%2e%2e%2f`, and a filter on both does not stop the decoder's own escape syntax.
  Assume any single-form filter buys you minutes, not the contest.

**In the source** — the actual check the author left out:

- It is the only kind of patch that ends the bug rather than delaying it.
- It requires a restart, and a restart is a window where the checker may find the
  service down. Know the restart command and its duration *before* you need it.
- It is where "patch by deleting the feature" happens, so it is where the bracket
  matters most.

Start in front when you are being farmed right now and need the bleeding to stop;
move into the source once the bracket is green and the clock is yours again.

## The four patches that cost more than the exploit

1. **Deleting the endpoint.** The checker exercises the feature. Removing
   `/api/note` stops the exploit and the score.
2. **Deleting or renaming the check that went red.** This is the one the tool now
   catches, and the reason the message names the legal move: if the removal really
   is deliberate, re-save the baseline with `--save`. Switching `--compare` off is
   not the legal move.
3. **Rotating a credential the service itself needed.** Every default in the image
   is public and must rotate, but a config file or a service account that reads it
   has to be updated in the same bracket. Rotate, then re-run the bracket, one
   secret at a time.
4. **Blocking egress the service needs.** Locking outbound traffic is sound
   defence and it also breaks the organiser's checker if the checker is called
   back, and your own farm if it runs from the same host. Allow-list before you
   deny.

## Rollback, written down before it is needed

For every patch, write the undo command *next to* the patch command before applying
it. A patch you cannot undo in one command is not ready. Keep the original file:

```bash
cp <file> <file>.orig.$(date +%H%M%S)      # before
cp <file>.orig.<stamp> <file> && <restart> # the undo, written in advance
```

## What ends a patch cycle

`echo $?` printed 0 or 2, the comparison's `regressions` list is empty, the undo
command is written down, and the service is green on the organiser's own scoreboard
— not only on yours. Anything else and you are still mid-patch.
