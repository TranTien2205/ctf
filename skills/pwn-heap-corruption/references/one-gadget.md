# The one-gadget — the execve constraint gadget


A libc address where execve("/bin/sh") fires if register/stack
constraints hold — the shortcut a hook write aims at.

## Reality here

one_gadget the tool is ABSENT — find candidates by hand:
    r2 -A libc.so.6
    / execve        # search refs to the execve symbol
Constraints must be checked in the disassembly around each candidate.

## The check

Each candidate's constraints (e.g. [rsp+0x30]==0) must hold at the
call moment — verify against the call site's register/stack state.

## Falsifier

No candidate's constraints are satisfiable from the firing context:
the shortcut doesn't exist — use system()+"/bin/sh" instead.
