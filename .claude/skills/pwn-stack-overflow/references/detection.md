# Detection — naming it stack corruption

## Signals it IS this class

| Observation | Meaning |
|---|---|
| `gets`, `scanf %s`, `strcpy` into a local | unbounded copy into stack |
| `read(fd, buf, n)` where n is influenced | controllable length |
| crash whose faulting RIP holds your bytes | control proven |
| `strcpy`/`memcpy` with computed n | influenced bound |
| `sprintf`/`vsprintf` into a stack buffer | unbounded format write |

## Signals it is NOT

| Observation | Real class |
|---|---|
| `printf(user_input)` without a length issue | `pwn-format-string` |
| corruption into heap metadata | `pwn-heap-corruption` |
| the crash is in a parser, not a return | a logic bug, not corruption |
| the bound is genuinely fixed and unreachably large | no bug |

## The three-question check

1. Is there a write into a stack-allocated buffer?
2. Can its length exceed the buffer's allocation?
3. Does the write reach the saved frame (canary → saved RBP → saved RIP)?

Three yeses = this class. Any no = investigate which bound actually stops
the write.
