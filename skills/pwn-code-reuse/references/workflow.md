# The code-reuse workflow — the whole run in order


1. Confirm IP control — the upstream primitive is proven (cyclic offset
   verified or a write lands on a call slot).
2. Triage — python3 tools/pwn_triage.py ./chal: protections, the gadget
   report, the routes each protection leaves.
3. Decide leak-needed: PIE/ASLR → yes; non-PIE static → maybe not.
4. Leak if needed — the GOT-print recipe or a UAF read.
5. Choose the ending — system/execve/win/syscall — by what the binary
   and the leak allow.
6. Build the chain — pops, args, call, ending.
7. Verify stage by stage — r2 -d, gadget by gadget.
8. Fire — and the flag passes through hooks.py pre-flag.

## The runbook kernel

    control → protections → leak → chain → verify → fire
