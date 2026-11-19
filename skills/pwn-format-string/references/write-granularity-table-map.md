# Write granularity — n vs hn vs hhn — map

Companion to `write-granularity-table.md`.

| Specifier | Width | Use |
|---|---|---|
| `%n` | full word (8 bytes x64) | whole-value write |
| `%hn` | 2 bytes | same-page/64KB redirects |
| `%hhn` | 1 byte | byte-wise address build |
| `%ln` | long (8 bytes x64) | same as %n on x64 |
