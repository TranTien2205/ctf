# Code-reuse falsifiers — the route-closing observations


| Observation | Route closed |
|---|---|
| no IP control | the whole class — go upstream |
| NX off / RWX present | ROP unnecessary — inject |
| no syscall gadget + static | syscall execve closed |
| no pop rdi and no ret2csu | argument setting closed |
| full RELRO + no lazy binding | GOT/ret2dlresolve closed |
| no libc leak + no shipped libc | every libc call closed |
| no writable page + no string in binary | /bin/sh planting closed |
| one-shot + chain too long | multi-stage closed |
| every gadget tail has fatal side effects | the chain can't compose |

A falsifier kills a route, not the class — the matrix has alternatives.
