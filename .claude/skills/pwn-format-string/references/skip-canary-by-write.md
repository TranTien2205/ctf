# Writing around the canary via %n


A fmtstr write doesn't have to cross the canary: %n addresses ONE pointer
— overwrite the return address directly, or a GOT slot, leaving the
canary untouched.

## Key difference vs smash

A stack smash must write through the canary's position to reach the saved
return. A %n write jumps straight to the target — the canary never gets
corrupted.

## Shapes

- %n → GOT slot: fires on the next call of that import.
- %n → saved return address: fires at function return; needs the stack
  address leaked first.
- %n → __free_hook: fires on next free (glibc ≤2.34).

## Steps

1. Leak what you need (canary-free targets preferred).
2. Plant the target's address at a %N$n position.
3. Write the redirect value with the right count.

## Falsifier

The only redirectable slots are unreachable by %N$n positions, or their
values can't be composed by the count.
