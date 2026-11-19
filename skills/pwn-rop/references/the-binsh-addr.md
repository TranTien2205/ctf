# The /bin/sh address — the arg's value


The pointer's value: the string's home —

- rodata: `strings -t x` offset (non-PIE absolute).
- .bss: where you planted it.
- libc: base + str offset.

## The pass

pop rdi ; THE ADDRESS — not the string itself.
