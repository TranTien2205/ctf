# Class boundary — what stack-corruption is NOT

## The neighbors

| Shape | Real class |
|---|---|
| `printf(user_input)` — read/write via format spec | `pwn-format-string` |
| corruption into heap chunk metadata (fd/bk, size fields) | `pwn-heap-corruption` |
| NX on — the exploit is code reuse | `pwn-code-reuse` (the chain class) |
| a parsing crash with no write-to-saved-state | a logic/DoS bug |

## The deciding question

'Does the write reach the saved stack frame (canary → saved RBP → saved
RIP)?' Yes → this class. Reaches heap metadata → heap class. A read/write
that never reaches stack state → format-string or logic.

## Shared surfaces

- `pwn-code-reuse`: the chain built on top of THIS corruption. The classes
  split at 'the bug is a stack smash' (here) vs 'the payload is ROP' (there).
- `pwn-format-string`: a `printf(input)` is a read+write primitive, not a
  smash — different mechanism, different payload shape.

## The honest edge

A stack smash under full RELRO + canary + no leak may be unexploitable as
return-control — the class owns the bug, but the route out may be heap or
a different primitive. Record honestly when the protection set closes the
intended chain.
