# The falsifiers — route-closing observations — map

Companion to `the-falsifiers.md`.

| Observation | Route closed |
|---|---|
| no IP control | the whole class — go upstream |
| NX off / RWX present | inject instead |
| no pop rdi, no ret2csu | arg setting closed |
| no syscall + static binary | the syscall route |
| full RELRO + lazy binding | GOT writes |
| no leak + PIE | binary addressing |
| chain > read limit, no pivot | this chain — stage it |
| every route's ending closed | the class itself |
