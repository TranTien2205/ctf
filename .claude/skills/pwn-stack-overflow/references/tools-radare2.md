# radare2 — the dynamic story here

No gdb in this environment — radare2 is the debugger/disassembler: r2 -d debugs, r2 -A analyzes, pdf @ main disassembles, /R finds gadgets.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| r2 -d ./chal | debug session | breakpoints, stepping |
| r2 -A ./chal | full analysis | functions, xrefs, gadgets |
| pdf @ main | disassemble main | the function body |
| /R pop rdi | find gadgets | the ROP search |

## Steps

1. r2 -A ./chal — analyze once, then use the function list (afl).
2. r2 -d ./chal — run with input to see the crash and the register state.
3. pdf @ <func> — read the deciding check and the vulnerable read.
4. /R <mnemonic> — find gadgets (the pwn_triage set is the essential one).

## Falsifier

Falsifier — radare2 can't analyze the binary (packed/obfuscated): the static analysis story is thin; readelf/objdump/strings fallback.

## Traps

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
