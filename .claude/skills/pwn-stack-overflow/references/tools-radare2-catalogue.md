# radare2 — the dynamic story here — case catalogue

No gdb in this environment — radare2 is the debugger/disassembler: r2 -d debugs, r2 -A analyzes, pdf @ main disassembles, /R finds gadgets.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | r2 -d ./chal | debug session | breakpoints, stepping |
| 2 | r2 -A ./chal | full analysis | functions, xrefs, gadgets |
| 3 | pdf @ main | disassemble main | the function body |
| 4 | /R pop rdi | find gadgets | the ROP search |

## Falsifier

Falsifier — radare2 can't analyze the binary (packed/obfuscated): the static analysis story is thin; readelf/objdump/strings fallback.
