---
name: crypto-rsa
description: >
  Action-oriented depth skill for RSA key or plaintext recovery. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: crypto-ecc-dlog.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [crypto, crypto-rsa, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# RSA key or plaintext recovery

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

answer the six discriminators in order with python3 tools/crypto_attack.py list, then run the ONE attack they select: how many moduli, is e small, is d small, are the primes close, is part of a factor known, is phi shared

**Falsifier** — the observation that closes this class: the attack's own stated applicability bound is exceeded -- for example d above the 0.292 bound for boneh-durfee, or a known-bits window above n**0.25 for coppersmith -- and no lattice parameter moves it
## Recognise

The handout gives numbers, not a service: one or more moduli `n`, a public
exponent `e`, and one or more ciphertexts. Write the parameter sheet before
choosing anything — modulus bit length, `e`, how many moduli, how many
messages, and whether any value repeats across them.

## The discriminator table

Answer in order; the first yes picks the attack id for `tools/crypto_attack.py`.

| Observation | Attack id |
|---|---|
| several moduli from the same generator, none factorable alone | `batch-gcd` |
| the same message encrypted to several recipients under small `e` | `hastad` |
| one modulus reused with two exponents | `common-modulus` |
| primes `p`, `q` generated close together (`next_prime` after `p`) | `fermat` |
| `d` small, `e` full-size | `wiener`, then `boneh-durfee` below its bound |
| part of a factor or of the message known | `coppersmith-high-bits` / `coppersmith-core` |
| `e` = 3 and the message short enough that `m**e < n` | `eth-root` / `small-e-root` |
| `p - 1` smooth | `pollard-pm1` |

If only a private operation is missing — you hold `d`, `phi`, or the factors —
`factor-from-d` or `rsa-decrypt` finishes directly.

## Confirm

A recovered plaintext or factor is confirmed when it passes a check the handout
verifies by itself: `pow(m, e, n)` reproduces the ciphertext, or the product of
the recovered factors reproduces `n` exactly. A plausible-looking plaintext that
fails that check is a candidate, not a recovery.

## Traps

- Bounds are the attack. `boneh-durfee` fails silently above its `d` bound and
  `coppersmith` above its known-bits window; check the applicability line each
  attack prints before waiting on the lattice.
- A shared-prime batch needs at least two moduli; a single `n` never reaches
  `batch-gcd`.
- `e = 3` alone means nothing — the shortcut applies only when `m**e < n`, so
  padded messages route back to `hastad` or `coppersmith`.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # every attack id and its applicability
python3 tools/crypto_attack.py <attack-id> --help
```

Feed the parameter sheet, not guesses: a wrong bit length routes to the wrong
lattice bound.

## Routing

Shares signals with: `../crypto-ecc-dlog/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/crypto-triage/references/rsa-attacks.md`
- `skills/ctf-crypto/triage-rsa.md`
- `skills/ctf-crypto/rsa-attacks.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
