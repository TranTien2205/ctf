# Glossary — the vocabulary

| Term | Meaning |
|---|---|
| saved RIP | the return address — the overwrite's prize |
| canary | random word checked before return |
| NX | stack/data not executable |
| PIE | base randomized; addresses are base+offset |
| RELRO | partial: GOT writable; full: GOT readonly |
| gadget | code fragment ending in ret |
| chain | qwords of gadget addresses + their args |
| ret2win | jump to a function in the binary |
| ret2plt | call an imported function's PLT stub |
| ret2libc | call a libc function via a leak |
| ret2csu | the __libc_csu_init universal gadgets |
| SROP | sigreturn-oriented — one syscall restores all regs |
| cyclic | de Bruijn pattern → the offset |
| fork-brute | per-connection canary recovery |
