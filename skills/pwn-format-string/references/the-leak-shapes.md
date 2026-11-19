# The leak shapes — recognizing what's in the %p dump

| Shape | Likely |
|---|---|
| 0x7f... | a libc/mmap/stack address |
| 0x55... / 0x56... | a PIE code/binary pointer |
| a word ending in 00 | the stack canary |
| 0x6c6c6568... | ASCII bytes (your input) |
| a small number | a counter/index |
| a repeated pattern | a pattern/cyclic |

Read the dump's shapes — each tells you what leaked.
