# When the read alone suffices — no write needed


Sometimes the flag sits in readable memory — a %s at the flag's address,
or a %p leak of a stack slot containing it — the read IS the exploit.

## Steps

1. If the flag is a string at a known/leaked address: plant the pointer,
   %s it.
2. If the flag's address is fixed (non-PIE .rodata), no leak needed.
3. Check strings/rodata for the flag first — cheapest win.

## Falsifier

The flag isn't at any readably-addressable location: the write is
required.
