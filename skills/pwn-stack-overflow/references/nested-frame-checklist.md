# Nested frames — the overflow inside a called function — checklist

The vulnerable read often sits inside a helper function called by main: the smash controls the HELPER's return first, then main's — a chain across frames.

## Checklist

- [ ] The smash controls the innermost frame's return first.
- [ ] After the helper's return, execution is in main — main's own return is next on the stack.
- [ ] You can chain: helper returns to a gadget, main's return is the next controlled address.
- [ ] The offsets compound — measure both.

## Abort conditions

- Each frame's return is independently overwritable in one smash.
- The helper's return goes first; plan the sequence.

## Falsifier

Falsifier — only the helper's return is reachable and the useful redirect needs main's frame: the second return is unreachable.
