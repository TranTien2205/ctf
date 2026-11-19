# Field manual — the condensed runbook

1. `pwn_triage` — protections + gadgets + routes.
2. Find the sink: unbounded copy into a stack buffer.
3. `pwn_cyclic <N>` → send → fault → `--find` → offset.
4. Protection routes: canary → leak/fork; PIE → leak; NX off → shellcode;
   NX on → ret2win/ret2plt/ret2libc/ret2csu/SROP.
5. Build the chain qword-by-qword; check bad bytes against the read's filter.
6. Watch alignment — a ret gadget before the libc call.
7. Land it; post-probe the class, pre-flag the bytes.

Each step's falsifier is the cheap check: run it before building.
