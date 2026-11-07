---
name: crypto-ecc-dlog
description: >
  Action-oriented depth skill for Curve, nonce or discrete-log recovery. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: crypto-rsa.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [crypto, crypto-ecc-dlog, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Curve, nonce or discrete-log recovery

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

decide the discriminator first: a nonce REUSED across two signatures recovers the key in closed form with ecdsa-nonce-reuse and needs no lattice, a merely BIASED nonce is hnp or hnp-ecdsa, and a plain discrete log needs the smoothness check before bsgs or pohlig-hellman

**Falsifier** — the observation that closes this class: re-derive the public point from the recovered private scalar and compare: a scalar that does not reproduce the supplied public key is not the key, and bsgs is out of reach above a group order of roughly 2**44
## Recognise

The handout carries curve parameters, ECDSA signature pairs `(r, s)`, or a
discrete-log statement (`y = g**x mod p`). Name the group first — curve name,
order, generator — because the discriminator below reads differently on each.

## The discriminator

| Observation | Route |
|---|---|
| the same `r` across two signatures | `ecdsa-nonce-reuse` — closed form, no lattice |
| a nonce that is biased, short, or partially known across several signatures | `hnp` / `hnp-ecdsa` — a lattice problem |
| a group order that factors smoothly | `pohlig-hellman` |
| a small order or bounded exponent | `bsgs` — out of reach above ~2**44 |

The reused-nonce case is the most common CTF shape and the cheapest to check:
two signatures, same `r`, gives `k` in one division and the private key in one
more.

## Confirm

Re-derive the public point from the recovered scalar and compare it with the
supplied public key. A scalar that does not reproduce the public key is not the
key, whatever the algebra looked like.

## Traps

- Nonce **reuse** means identical `r`, not similar nonces. Similarity is the
  biased case and needs the lattice route with several signatures — one
  signature never feeds `hnp-ecdsa`.
- `pohlig-hellman` runs per-factor of the order; check smoothness first with
  `smoothness` before committing.
- On Weierstrass curves, validate that supplied points lie on the curve —
  invalid-curve attacks exist only when the server skips that check.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # ecdsa / dlog / lattice families
python3 tools/crypto_attack.py smoothness --help
```

## Routing

Shares signals with: `../crypto-rsa/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/crypto-triage/references/ecc-attacks.md`
- `skills/ctf-crypto/ecc-attacks.md`
- `skills/ctf-crypto/lattice-and-lwe.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
