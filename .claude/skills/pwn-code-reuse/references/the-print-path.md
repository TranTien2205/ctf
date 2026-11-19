# The print path — getting bytes out


A leak must reach the output: call puts/printf/write on the address —
the value prints.

## The recipe

    pop rdi ; got_entry
    puts@plt

The GOT contents print as raw bytes — unpack them.

## The alternatives

- write(1, addr, 8) — raw 8 bytes.
- printf with a %p format — formatted.
