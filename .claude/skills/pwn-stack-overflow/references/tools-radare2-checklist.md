# radare2 — the dynamic story here — checklist

No gdb in this environment — radare2 is the debugger/disassembler: r2 -d debugs, r2 -A analyzes, pdf @ main disassembles, /R finds gadgets.

## Checklist

- [ ] r2 -A ./chal — analyze once, then use the function list (afl).
- [ ] r2 -d ./chal — run with input to see the crash and the register state.
- [ ] pdf @ <func> — read the deciding check and the vulnerable read.
- [ ] /R <mnemonic> — find gadgets (the pwn_triage set is the essential one).

## Abort conditions

- r2 -d works where gdb doesn't — it's the only debugger here.
- iz/izz lists strings with addresses; is lists symbols.
- On a remote target, you can't run r2 -d — the offset comes from the remote fault instead.

## Falsifier

Falsifier — radare2 can't analyze the binary (packed/obfuscated): the static analysis story is thin; readelf/objdump/strings fallback.
