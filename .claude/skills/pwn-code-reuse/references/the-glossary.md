# Code-reuse glossary


| Term | Meaning |
|---|---|
| gadget | a ret-terminated instruction tail |
| the chain | a stack of gadget addresses + args |
| pop gadget | pop rX; ret — sets a register |
| ret | the chain's instruction-pointer step |
| pivot | moving rsp to a controlled region |
| PLT | the call stubs — the call surface |
| GOT | the resolved pointers — the leak/write surface |
| ret2libc | calling into libc via ret |
| ret2csu | the __libc_csu_init universal call |
| SROP | sigreturn frame — all regs at once |
| ret2dlresolve | the resolver-forge call |
| one-gadget | the libc execve constraint point |
| the alignment ret | the bare ret fixing movaps crashes |
| the two-stage | leak + re-enter + real chain |
