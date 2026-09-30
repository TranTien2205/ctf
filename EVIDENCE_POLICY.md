# Evidence Policy

Every exploit claim carries two separate fields: what is claimed, and what
supports it. A claim with no evidence field is not a finding.

## What counts as evidence

- **Source evidence** names the exact file, line, route, input and sink.
- **Probe evidence** records the exact command or request, the timestamp, the
  status, the headers, the final URL, and a bounded span of the output or the
  observed callback.
- **Verification evidence** is the flag-bearing response or the supplied artifact
  read during this session.

## What does not count

A writeup's claim. A flag-shaped string in source, in a cache, or in a card. A
guessed value. A timeout. A tool's own label or confidence score. A chain card
match. Your own reasoning about what probably happened.

A timeout is evidence about availability or processing time, and nothing else.

## Defensive claims (attack-defense and post-incident)

The three kinds above all describe something present in a response. Half of an
attack-defense contest produces claims with no response behind them at all: "we
evicted the persistence", "nothing was exfiltrated", "the service is clean",
"that team has patched". No command proves an absence. So a defensive claim is
evidenced by the method that looked, plus the blind spot that method had.

Five fields, all of them:

- **command** is the exact command that ran, not a description of it.
- **output** is verbatim and bounded.
- **coverage** is what that command could NOT have seen. This field *is* the
  claim. Without it there is a search and no result.
- **recheck** is the observation that would fail if the claim were false.
- **grade** is one of three:
  - `evicted-verified`: the mechanism was re-triggered and did not fire.
  - `evicted-unverified`: the artifact was removed, and nothing re-triggered it.
  - `absent-within-coverage`: a search ran, found nothing, and `coverage` names
    what it was blind to.

An absolute absence is refused unless the grade is `absent-within-coverage` and
`coverage` is filled in. "Nothing was exfiltrated" is a claim about every byte
that ever left the host, and a single packet outside the window falsifies it.
State the absence with its window instead: "no outbound transfer larger than
1 MB appears in the captured window; the window begins at 01:40 and the
intrusion predates it." That is still an absence, it is still graded
`absent-within-coverage`, and the coverage clause is what makes it true. The
difference between those two sentences is worth more in a write-up than either
claim is.

"Probably exfiltrated" is not a defensive claim at all. It is a hypothesis, it
carries no grade, and it is labelled a hypothesis wherever it appears.

This needs no `tools/hooks.py` verb, and should not get one. Every hook loads a
challenge state file before it reads any argument: run `post-probe` against a
service name and it answers `no state file: create it with tools/state.py
first` and exits 2, measured on 2026-09-29. Past that gate, `post-probe`
requires a `--hypothesis-id` naming one existing hypothesis and a `--class`
matching that hypothesis's bug class. A defensive claim has neither. Pushing
one through the hook would mean inventing a challenge, a hypothesis id and a
bug class to carry a sentence about a host, which is three fabricated fields in
exchange for one honest one. That is why `tools/ad/` is a deliberate sibling
plane: it does not write `challenges/<name>/state.json` and it does not call
the hooks. The format above is the whole rule, the service's own ledger under
`tools/ad/` is where the claim is recorded, and the write-up is where it is
read.

## Cards

Writeup cards use `quality.verified_live: false` unless verification evidence
from this session is present. Unknown metadata stays `null` or `unknown`;
validators and critics reject unsupported additions.

Chain cards in `knowledge/chains/` follow `knowledge/chain-schema.json`:

- `verification.status` is `verified_live` only when the flag was read from a
  live response or a supplied artifact during a session here. Otherwise it is
  `writeup-claimed` or `unverified`.
- `flag` is always null. A card is for matching preconditions, not for carrying
  answers. `test/regression.py` fails on any flag-shaped string inside a card.
- `preconditions` are plain language for a human to confirm. No tool checks them,
  and `tools/chain_match.py` never reports a match as proof.
- `blast_radius` records what the chain can damage on a shared instance, so the
  cost of a write is known before the write.

## Direction changes

A hypothesis is closed only by an observation that falsifies it, and the reason
records that observation. An operator redirect, a tight schedule, or a better
idea are reasons to **park** a hypothesis at priority 0, not to close it. See
`HYPOTHESIS_PROTOCOL.md`.

## Reporting

Say which of the three evidence kinds supports each claim, or, for a claim
about an absence, which of the three defensive grades, with its coverage
boundary. When something is a guess, label it a guess. When a probe failed to
run, say it failed to run. An honest "not verified" is worth more than a
confident claim that does not survive the next session.
