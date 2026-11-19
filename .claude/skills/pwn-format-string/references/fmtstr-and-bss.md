# Writing into .bss/.data — the static targets


Global variables in .bss/.data have fixed addresses under non-PIE — a %n
write into them patches program state without needing a stack leak.

## Steps

1. Under non-PIE, .bss/.data addresses are compile-time fixed.
2. Global flags, string pointers, sizes — overwrite directly.
3. A global function pointer is a redirect target too.
4. Read the symbol table for globals: nm ./chal or r2's is.

## Falsifier

PIE on and no leak: .bss addresses are unknown until the base leaks.

## Commands

```bash
nm ./chal | grep -i ' [bdD] '
r2 -A ./chal && is
```
