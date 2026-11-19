# Where the chain begins — the write's landing point — checklist

Companion to `the-ret-chain-entry.md`.

## Checklist

- [ ] → `pop rdi; ret` + args → ROP continues.
- [ ] → `system` / `execve-stub` → direct.
- [ ] → a function that prints the flag → done.
