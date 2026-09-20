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

Say which of the three evidence kinds supports each claim. When something is a
guess, label it a guess. When a probe failed to run, say it failed to run. An
honest "not verified" is worth more than a confident claim that does not survive
the next session.
