# radare2 — the dynamic story here — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| r2 -d ./chal | debug session | breakpoints, stepping |
| r2 -A ./chal | full analysis | functions, xrefs, gadgets |
| pdf @ main | disassemble main | the function body |
| /R pop rdi | find gadgets | the ROP search |

## Falsifier

Falsifier — radare2 can't analyze the binary (packed/obfuscated): the static analysis story is thin; readelf/objdump/strings fallback.
