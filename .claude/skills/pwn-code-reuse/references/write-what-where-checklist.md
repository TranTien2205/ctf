# Write-what-where — the arbitrary write chain — checklist

Companion to `write-what-where.md`.

## Checklist

- [ ] `mov [rdi], rsi; ret` — write rsi at [rdi].
- [ ] `mov [rax], rdx; ret` — variants by register.
- [ ] `pop rdi ; ptr` + `pop rsi ; val` + `mov [rdi], rsi ; ret`.
