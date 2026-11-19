# radare2 — the dynamic story here — deep

No gdb in this environment — radare2 is the debugger/disassembler: r2 -d debugs, r2 -A analyzes, pdf @ main disassembles, /R finds gadgets.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — radare2 can't analyze the binary (packed/obfuscated): the static analysis story is thin; readelf/objdump/strings fallback.

## Highest-cost traps

- r2 -d works where gdb doesn't — it's the only debugger here.
- iz/izz lists strings with addresses; is lists symbols.
- On a remote target, you can't run r2 -d — the offset comes from the remote fault instead.

## Commands

```bash
r2 -A ./chal && afl
r2 -A ./chal && pdf @ main
r2 -A ./chal && /R pop rdi
r2 -d ./chal
```

## Cross-references

`tools-pwn-triage.md` · `rop-basics.md`
