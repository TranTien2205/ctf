# Protections — canary, PIE, NX, RELRO, ASLR

tools/pwn_triage.py reports each protection WITH the evidence that decided it. The sheet determines the whole chain — read it before touching a payload.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| CANARY present | smashing write trips __stack_chk_fail | leak it or write around it |
| PIE enabled | no absolute addresses | leak a code pointer first |
| NX on | no shellcode | code reuse — pwn-code-reuse |
| full RELRO | GOT is read-only | no GOT overwrite |
| ASLR on (default) | libc/stack addresses unknown | need a leak |

## Steps

1. python3 tools/pwn_triage.py ./chal — protections + dangerous imports + gadgets + routes left, with the evidence for each.
2. python3 tools/pwn_triage.py ./chal --gadgets — the full matched gadget list.
3. python3 tools/pwn_triage.py ./chal --challenge <name> — prints the ledger-record command.
4. Cross-check with readelf -h (PIE), readelf -s (imports), check the %fs:0x28 load in disasm for a real canary.

## Falsifier

Falsifier — the protections report contradicts your read of the binary: the report carries the evidence; trust the evidence, not the label.

## Traps

- A STATIC binary carries __stack_chk_fail even when built -fno-stack-protector — confirm the canary from the %fs:0x28 load, not the import.
- PIE + no leak = you need a partial-address write or an info-leak primitive first.
- 'NX' on Linux stack-NX; data/bss writable but not executable regardless.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
python3 tools/pwn_triage.py ./chal --gadgets
readelf -h ./chal | grep Type
```

## Cross-references

`tools-pwn-triage.md` · `canary-bypass.md` · `pie-leak.md`
