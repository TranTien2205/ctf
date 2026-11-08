---
name: misc-encoding-carrier
description: >
  Action-oriented depth skill for Encoding or carrier puzzle. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: misc-interpreter-escape, crypto-symmetric-oracle.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [misc, misc-encoding-carrier, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Encoding or carrier puzzle

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

IDENTIFY THE CARRIER before decoding: the alphabet, the distinct-character count and the length modulus separate base64 from base32 from base85 from hex from a custom alphabet in one command, and the index of coincidence separates a substitution from a transposition from a Vigenere

**Falsifier** — the observation that closes this class: the alphabet and length match no standard carrier and the index of coincidence is outside the natural-language range, so it is neither a standard encoding nor a classical cipher and the structure of the container is the real hiding place
## Recognise

A blob with no obvious attack surface: identify the carrier **before** decoding.
Alphabet, distinct-character count, and length modulus separate base64 from
base32 from base85 from hex from base58 at a glance; the index of coincidence
separates an encoding from a classical cipher.

## Confirm

Run the standard decoders first — a blob that decodes cleanly under one of them
was an encoding, not a cipher, and the class closes. Only when every standard
carrier fails, compute IC: near the natural-language range it is a substitution
problem (`../ctf-crypto/classic-ciphers.md`); far below it suggests
polyalphabetic or layered.

| Carrier | Tell |
|---|---|
| hex | even length, alphabet `[0-9a-f]` |
| base64 | alphabet size 64, `=` padding, length ≡ 0 mod 4 |
| base32 | `[A-Z2-7]`, `=` padding in groups of 8 |
| base85 / z85 | no padding, wider symbol set |
| rot-N / Caesar | IC of natural text, shifted letter frequencies |

## Traps

- Decode **twice**: `base64(hex(...))` and friends are the standard trick.
- `+`/`/` versus `-`/`_` distinguishes standard base64 from URL-safe; wrong
  alphabet fails silently.
- An odd-length "hex" string is usually base64 *of* hex, or a nibble-aligned
  custom table — check distinct-character count, not vibes.

## Operational probe

```bash
python3 -c "import base64,binascii; d=open('blob.txt','rb').read().strip(); [print(n, getattr(base64,n)(d)[:60]) for n in ('b64decode','b32decode','b85decode','a85decode')  if __import__('contextlib').suppress(Exception) or False]"
strings blob.txt | grep -i "flag{"
```

## Routing

Shares signals with: `../misc-interpreter-escape/`, `../crypto-symmetric-oracle/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-misc/encoding-and-cipher.md`
- `skills/ctf-misc/encodings.md`
- `skills/ctf-crypto/classic-ciphers.md`

| Any encoding/carrier question | `references/layer-identification.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
