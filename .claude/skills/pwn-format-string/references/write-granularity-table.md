# Write granularity — n vs hn vs hhn

| Specifier | Width | Use |
|---|---|---|
| `%n` | full word (8 bytes x64) | whole-value write |
| `%hn` | 2 bytes | same-page/64KB redirects |
| `%hhn` | 1 byte | byte-wise address build |
| `%ln` | long (8 bytes x64) | same as %n on x64 |

An address like 0x7f... needs %hhn×8 or %hn×4 — a single %n can't reach
it because the count can't be negative.
