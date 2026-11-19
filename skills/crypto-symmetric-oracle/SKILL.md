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

Depth, one named file at a time — every question has one owning module:

| Question | File |
|---|---|
| Which of the four oracles do I hold? | `references/detection.md` → `references/oracle-shapes.md` |
| ECB fingerprint / byte-at-a-time / splice | `references/ecb-detection.md` `references/ecb-byte-at-a-time.md` `references/ecb-cut-and-paste.md` |
| Prefix/boundary math | `references/block-alignment.md` |
| CBC pad-oracle / bit-flip / IV bugs | `references/cbc-padding-oracle.md` `references/cbc-bitflip.md` `references/cbc-iv-equals-key.md` |
| CTR/stream reuse and malleability | `references/ctr-nonce-reuse.md` `references/crib-drag.md` `references/stream-integrity.md` |
| GCM nonce reuse (forbidden attack) | `references/gcm-nonce-reuse.md` `references/tools-gcm-nonce.md` |
| MAC: extend, forge, truncate, time | `references/length-extension.md` `references/mac-forgery.md` `references/verify-oracle.md` `references/cbc-mac.md` |
| Raw-hash vs HMAC boundary | `references/hmac-vs-raw-mac.md` |
| Byte-level XOR | `references/single-byte-xor.md` |
| Tag/nonce/key recon | `references/iv-reuse-detection.md` `references/key-path.md` `references/key-confirmation.md` |
| Signed tokens (JWT/Django) | `references/jwt-signing-boundary.md` |
| Mode variant notes | `references/poodle-and-legacy.md` `references/rc4-and-salsa.md` `references/cbc-iv-prediction.md` `references/cmac-and-variants.md` |
| Response-channel anatomy | `references/response-distinguishers.md` `references/error-taxonomy.md` `references/timing-oracles.md` `references/format-vs-padding-oracles.md` |
| Transport choice | `references/webservice-vs-local.md` `references/chosen-ciphertext.md` |
| Tool drivers | `references/tools-ecb-oracle.md` `references/tools-pad-oracle.md` `references/tools-gcm-nonce.md` `references/tools-length-extension.md` `references/tools-crib-drag.md` `references/tools-parity-oracle.md` |
| Forging the end token | `references/token-forgery-workflows.md` `references/ecb-reordering.md` `references/chained-oracles.md` `references/ecb-prefix-suffix.md` |
| Discipline | `references/evidence.md` `references/falsifiers.md` `references/preconditions.md` `references/negative-results.md` |
| Cases and maps | `references/attack-catalogue.md` `references/workflow.md` `references/recon-order.md` `references/case-studies.md` `references/worked-examples.md` `references/cryptopals-map.md` `references/multi-step-chains.md` `references/closing-index.md` |
| Edge/boundary/stuck | `references/boundary-cases.md` `references/edge-cases.md` `references/class-boundary.md` `references/authenticated-boundary.md` `references/anti-patterns.md` `references/common-mistakes.md` `references/troubleshoot.md` `references/evasion.md` `references/operator-notes.md` `references/theory.md` `references/glossary.md` `references/field-manual.md` `references/verified-chains.md` `references/per-boundary.md` `references/per-condition.md` `references/per-probe.md` `references/per-signal.md` |

Every module above also ships `-deep`, `-checklist`, `-index`, `-map`, and
(for the core attacks) `-variant`, `-catalogue`, `-playbook`, `-summary`
companions — pick the depth the situation needs.

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
