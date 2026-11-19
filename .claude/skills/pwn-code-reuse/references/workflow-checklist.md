# The code-reuse workflow — the whole run in order — checklist

Companion to `workflow.md`.

## Checklist

- [ ] 1. Confirm IP control — the upstream primitive is proven (cyclic offset
- [ ] 2. Triage — python3 tools/pwn_triage.py ./chal: protections, the gadget
- [ ] 3. Decide leak-needed: PIE/ASLR → yes; non-PIE static → maybe not.
- [ ] 4. Leak if needed — the GOT-print recipe or a UAF read.
- [ ] 5. Choose the ending — system/execve/win/syscall — by what the binary
- [ ] 6. Build the chain — pops, args, call, ending.
- [ ] 7. Verify stage by stage — r2 -d, gadget by gadget.
- [ ] 8. Fire — and the flag passes through hooks.py pre-flag.
