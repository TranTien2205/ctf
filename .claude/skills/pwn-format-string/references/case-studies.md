# Case studies — the canonical shapes

1. The printf(name) leak: %p run leaks canary+PIE, then a smash.
2. The blind write: no output, but %n to GOT redirects a later call.
3. The GOT-overwrite classic: printf(buf), partial RELRO, puts→system.
4. The ret-addr write: stack addr leaked, %n writes a gadget's address.
5. The __free_hook (old glibc): write system to free_hook, free "/bin/sh".
6. The multi-write: overwrite GOT + ret-addr in one fmtstr.
7. The two-primitive binary: fmtstr leaks, smash exploits.
