# Protections — canary, PIE, NX, RELRO, ASLR — checklist

tools/pwn_triage.py reports each protection WITH the evidence that decided it. The sheet determines the whole chain — read it before touching a payload.

## Checklist

- [ ] python3 tools/pwn_triage.py ./chal — protections + dangerous imports + gadgets + routes left, with the evidence for each.
- [ ] python3 tools/pwn_triage.py ./chal --gadgets — the full matched gadget list.
- [ ] python3 tools/pwn_triage.py ./chal --challenge <name> — prints the ledger-record command.
- [ ] Cross-check with readelf -h (PIE), readelf -s (imports), check the %fs:0x28 load in disasm for a real canary.

## Abort conditions

- A STATIC binary carries __stack_chk_fail even when built -fno-stack-protector — confirm the canary from the %fs:0x28 load, not the import.
- PIE + no leak = you need a partial-address write or an info-leak primitive first.
- 'NX' on Linux stack-NX; data/bss writable but not executable regardless.

## Falsifier

Falsifier — the protections report contradicts your read of the binary: the report carries the evidence; trust the evidence, not the label.
