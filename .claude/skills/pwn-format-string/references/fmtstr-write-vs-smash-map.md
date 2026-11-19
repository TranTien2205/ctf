# Fmtstr-write vs stack-smash — two writes, two classes — map

Companion to `fmtstr-write-vs-smash.md`.

| Write | Class |
|---|---|
| a %n | format-string |
| a copy past a buffer | stack-smash |
| both primitives in one binary | leak + smash |
## Falsifier
