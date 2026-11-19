# Off-by-one and single-byte overwrites — checklist

A single controlled byte past the buffer can still matter: zero the canary's low byte, shift the saved RBP's LSB, or corrupt a length field.

## Checklist

- [ ] Identify which byte is overwritten (the first byte past the buffer).
- [ ] If it hits the saved RBP's LSB: a controlled RBP-shift enables the leave;ret pivot.
- [ ] If it hits the canary's LSB: a 0 byte keeps it valid (canaries end in 00).
- [ ] A one-byte overwrite of a length field can enable a larger second overflow.

## Abort conditions

- The canary's low byte is always 0x00 — overwriting it with 0 keeps it valid.
- Saved-RBP LSB shifts the parent's frame — a pivot primitive.

## Falsifier

Falsifier — the overwritten byte reaches nothing security-relevant: no exploitable effect.
