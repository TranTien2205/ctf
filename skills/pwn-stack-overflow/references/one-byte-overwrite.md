# Off-by-one and single-byte overwrites

A single controlled byte past the buffer can still matter: zero the canary's low byte, shift the saved RBP's LSB, or corrupt a length field.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| write reaches exactly one byte past the buffer | off-by-one | LSB corruption |
| canary's low byte is 0 (usually) | canary's LSB is fixed | a byte-overwrite keeps it valid |
| saved RBP low byte corruptible | frame shift | frame-pointer control |

## Steps

1. Identify which byte is overwritten (the first byte past the buffer).
2. If it hits the saved RBP's LSB: a controlled RBP-shift enables the leave;ret pivot.
3. If it hits the canary's LSB: a 0 byte keeps it valid (canaries end in 00).
4. A one-byte overwrite of a length field can enable a larger second overflow.

## Falsifier

Falsifier — the overwritten byte reaches nothing security-relevant: no exploitable effect.

## Traps

- The canary's low byte is always 0x00 — overwriting it with 0 keeps it valid.
- Saved-RBP LSB shifts the parent's frame — a pivot primitive.

## Cross-references

`saved-regs.md` · `canary-bypass.md`
