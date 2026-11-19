# The saved-return write — a complete recipe


Overwriting the saved return address redirects at function return —
needs a stack address leak and a planted pointer.

## Recipe

1. Leak a stack pointer (saved rbp / argv) — compute the saved-ret slot.
2. saved_ret = *saved_rbp + 8 typically (verify the frame layout).
3. Plant the saved-ret address at arg position N (input bytes or a
   first-write plant).
4. %Nc ... %N$hn writes the target's bytes over saved_ret.
5. Function returns — redirect fires.

## Multi-call variant

Call 1: leak the stack addr. Call 2: plant + write. Call 3+: trigger.

## Falsifier

The function doesn't return (exit/abort/longjmp): the write lands but
never fires — pick a slot that fires earlier.
