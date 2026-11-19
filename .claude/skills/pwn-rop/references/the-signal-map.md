# The signal map — what each output means


| Output | Meaning |
|---|---|
| nx:true pie:false | non-PIE chain, libc leak still needed |
| relro:full | no GOT writes |
| canary:true | the canary's slot needs its leaked value |
| no system in imports | libc or syscall ending |
| /bin/sh in strings | the arg's fixed (non-PIE) |
| no syscall gadget | the libc route |
