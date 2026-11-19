# one-gadget — the libc shortcut


A libc offset where execve("/bin/sh") fires if constraints hold —
one ret, the whole exploit.

## The find (no one_gadget tool here)

    r2 -A libc.so.6
    Look for the execve call sites with feasible register constraints.

## The constraints

Each candidate needs its register/stack preconditions met at the call
— verify against the firing context.
