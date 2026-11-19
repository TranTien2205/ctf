# The verify table — the stage checks


| Stage | Verify |
|---|---|
| overwrite | rip = your gadget |
| pop | the register holds the value |
| leak | a pointer-range value |
| write | the target's bytes changed |
| call | the function ran (observable) |
| ending | the flag/shell/read occurred |

A stage failing its check is the bug's address — bisect there.
