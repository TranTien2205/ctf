# Finding /bin/sh — the string source


system() needs a "/bin/sh" pointer — three sources:

1. The binary's own .rodata — `strings ./chal | grep /bin/sh` or
   r2 -A; / /bin/sh.
2. libc's copy — base + the string's offset (version-specific).
3. Your planted bytes — write "/bin/sh" into .data/.bss first, then
   pass that address.

## The computation

    binsh_addr = libc_base + binsh_offset
    # offset via: strings -t x libc.so.6 | grep '/bin/sh'

## Falsifier

No source reachable: no string in binary, no known libc, no writable
page to plant — execve with a planted path on the stack instead.
