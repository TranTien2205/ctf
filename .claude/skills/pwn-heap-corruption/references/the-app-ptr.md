# App-owned function pointers — the no-libc target


The program's own function pointers (callback fields, vtables, handler
tables) are call slots that need NO libc knowledge — often in .bss
(non-PIE: fixed address).

## Find them

- Source: struct fields called later.
- r2 -A: afl for indirect-call candidates; axt on function pointers.
- A "run/execute/print" menu op that dispatches through a field.

## The write

Aim the arbitrary write at the field; trigger the call — no libc leak
needed if the replacement is a win function in the binary (non-PIE)
or a leaked address.

## Falsifier

No indirect call reachable with a corruptible pointer: app-ptr routes
are absent — libc targets only.
