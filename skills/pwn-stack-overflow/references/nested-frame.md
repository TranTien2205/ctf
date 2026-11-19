# Nested frames — the overflow inside a called function

The vulnerable read often sits inside a helper function called by main: the smash controls the HELPER's return first, then main's — a chain across frames.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the read is in a helper called by main | two returns available | chain them |
| helper returns then main returns | nested control | chain across frames |
| one smash, two return addresses | double redirect | the layout |

## Steps

1. The smash controls the innermost frame's return first.
2. After the helper's return, execution is in main — main's own return is next on the stack.
3. You can chain: helper returns to a gadget, main's return is the next controlled address.
4. The offsets compound — measure both.

## Falsifier

Falsifier — only the helper's return is reachable and the useful redirect needs main's frame: the second return is unreachable.

## Traps

- Each frame's return is independently overwritable in one smash.
- The helper's return goes first; plan the sequence.

## Commands

```bash
r2 -A ./chal && pdf @ <helper>
```

## Cross-references

`saved-regs.md` · `offset-measurement.md`
