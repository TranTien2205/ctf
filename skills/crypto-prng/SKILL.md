---
name: crypto-prng
description: >
  Action-oriented depth skill for Predictable pseudorandom generator. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: crypto-symmetric-oracle.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, crypto-prng, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Predictable pseudorandom generator

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

name the generator from source, count how many consecutive outputs you hold, then run the matching attack id (lcg-recover, lcg-unknown-modulus, lcg-truncated, berlekamp-massey, lfsr-recover, lfsr-predict, mt19937-clone)

**Falsifier** — the observation that closes this class: predict one held-back output and compare: a generator whose next value you cannot produce exactly is not recovered, and mt19937-clone genuinely needs 624 consecutive 32-bit outputs
## Recognise

The generator is the target, not the cipher. Source names it (`LCG`, `LFSR`,
`mt19937`, `random.getrandbits`) or the shape does: outputs that look uniform
but repeat the generator across tickets, nonces or keys.

## Confirm

Record consecutive outputs — the attack tables index on them. Then name the
matching attack id from `tools/crypto_attack.py list`:

| Generator and what you hold | Attack id |
|---|---|
| LCG with modulus `m`, multiplier `a`, increment `c` | `lcg-recover` |
| LCG with modulus unknown but outputs untruncated | `lcg-unknown-modulus` |
| LCG leaking only high bits | `lcg-truncated` |
| LFSR keystream bits | `berlekamp-massey`, then `lfsr-predict` |
| LFSR where the taps are unknown | `lfsr-recover` |
| MT19937 with 624 consecutive 32-bit outputs | `mt19937-clone` |

Confirmation is a predicted held-back output reproduced exactly — never a
statistical argument. If the next value cannot be produced bit-for-bit, the
generator is not recovered.

## Traps

- Outputs must be **consecutive and raw**. A `mod`, a hex encoding, or a float
  division between the state and your observation changes the required count or
  breaks the clone entirely.
- MT19937 needs the full 624-word state window; 623 outputs leave you one word
  short, not one output short.
- A time-seeded generator is a seed search, not a state recovery — bound the
  seed window from the challenge's stated epoch before brute-forcing.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # id, family, applicability
python3 tools/crypto_attack.py <attack-id> --help
```

Count outputs before running anything: the applicability line on each attack
says exactly how many it needs.

## Routing

Shares signals with: `../crypto-symmetric-oracle/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-crypto/triage-prng.md`
- `skills/ctf-crypto/prng-attacks.md`
- `skills/ctf-crypto/prng.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
