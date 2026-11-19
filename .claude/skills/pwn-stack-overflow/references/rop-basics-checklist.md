# ROP basics — code reuse when NX is on — checklist

Return-oriented programming: chain existing code fragments ending in 'ret' to do work without injecting code. pwn-code-reuse is the owning class; this file is the bridge.

## Checklist

- [ ] pwn_triage --gadgets lists the matched gadgets (the essential set: pop rdi/rsi/rdx, syscall, ret).
- [ ] Each chain entry = address + its consumed stack args; a 'pop r; ret' gadget pops the next qword into r.
- [ ] Chain layout: [pad][pop rdi;ret][arg1][pop rsi;ret][arg2][syscall;ret].
- [ ] The class file is ../pwn-code-reuse/ — this file is the recognition.

## Abort conditions

- Small static binaries have few gadgets — check if __libc_csu_init exists for the universal gadgets.
- A missing 'pop rdx' gadget is the usual hole — find it via the mov rdx gadgets or a different call.
- Every gadget in the chain must be reachable at runtime (PIE → need base leak).

## Falsifier

Falsifier — the gadgets needed don't exist in the binary (or a needed constant can't be loaded): ROP fails; need a leak or a different primitive.
