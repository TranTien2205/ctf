# Reading the flag directly — the %s one-shot


If the flag string sits at a known or leaked address, %s reads it in one
shot — no write, no chain, the simplest possible win.

## Steps

1. strings -tx ./chal | grep flag → the flag's static address.
2. Plant it at a %N$s arg position; %s prints it.
3. Under PIE, leak the base first → flag_addr = base + offset.

## Falsifier

The flag isn't in memory as a readable string (it's behind exec or in a
file only readable post-exec): need the write.

## Commands

```bash
strings -tx ./chal | grep -iE 'flag|ctf'
```
