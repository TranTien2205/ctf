---
name: crypto-symmetric-oracle
description: >
  Action-oriented depth skill for Block, stream or MAC oracle. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: crypto-prng, misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [crypto, crypto-symmetric-oracle, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Block, stream or MAC oracle

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

detect ECB in ONE request wherever you control plaintext -- identical plaintext blocks give identical ciphertext blocks -- then separate an invalid-pad answer from an invalid-MAC answer before writing any oracle loop

**Falsifier** — the observation that closes this class: the mode is authenticated (GCM or an HMAC checked before decryption), so a tampered ciphertext is rejected identically whatever the padding, and no oracle exists to query
## Recognise

You control plaintext and read ciphertext (or the reverse through a service):
an ECB/CBC/CTR token, a MAC tag, a decrypt endpoint. The first question is
always which oracle you actually hold — encrypt, decrypt, padding-check, or
verify.

## Confirm

Detect ECB in **one** request: submit 32+ identical bytes and look for
identical ciphertext blocks. Then separate the oracle answers — an
invalid-padding response that differs from an invalid-MAC response is the whole
padding-oracle precondition.

| Oracle or reuse | Route |
|---|---|
| ECB with attacker-controlled plaintext | block cut-and-paste / chosen-plaintext dictionary |
| CBC with a distinguishable padding error | padding oracle decryption |
| a reused IV or nonce under CTR/stream | keystream reuse, `crib-drag` |
| `MD5`/`SHA1` used as `hash(secret || message)` | `length-extension` |
| two messages under one keystream | XOR them; the keystream cancels |

## Traps

- Authenticated modes close the class: GCM, or any HMAC checked **before**
  decryption, rejects a tampered ciphertext identically and no oracle exists.
- ECB needs a controlled block boundary — a fixed server prefix shifts your
  alignment by its length mod 16.
- A generic 500 is not a padding oracle. Only a response that distinguishes
  padding-bad from MAC-bad carries the signal.

## Operational probe

```bash
python3 tools/crypto_attack.py list        # xor / hash / helper families
python3 tools/crypto_attack.py crib-drag --help
python3 tools/crypto_attack.py length-extension --help
```

## Routing

Shares signals with: `../crypto-prng/`, `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/crypto-triage/references/block-cipher.md`
- `skills/crypto-triage/references/hash-attacks.md`
- `skills/ctf-crypto/modern-ciphers.md`

| Any block/stream/MAC-oracle question | `references/oracle-shapes.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
