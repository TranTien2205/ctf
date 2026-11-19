# The code-reuse checklist — the run in order — checklist

Companion to `the-checklist.md`.

## Checklist

- [ ] [ ] IP control proven — offset measured
- [ ] [ ] Protections read — NX/PIE/RELRO/canary
- [ ] [ ] Leak needed? — PIE/dynamic decide
- [ ] [ ] Leak obtained — the base(s) computed
- [ ] [ ] Ending chosen — system/execve/win/syscall
- [ ] [ ] Gadgets found — the pops + the call
- [ ] [ ] /bin/sh source — found, planted, or libc
- [ ] [ ] The chain assembled — the script, the arithmetic
- [ ] [ ] The alignment ret — before the call
- [ ] [ ] Stage-verified — r2 -d walk
- [ ] [ ] The ending lands — observable effect
- [ ] [ ] The flag — through hooks.py pre-flag
