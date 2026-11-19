# ret2csu — the universal gadget pair — case catalogue

__libc_csu_init carries two gadgets that set rdx, rsi, rdi, and call an arbitrary function — the fallback when the binary is sparse of clean pops.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | __libc_csu_init in symbols | universal gadgets exist | use the pair |
| 2 | no pop rdx gadget anywhere | csu supplies it | the pair |
| 3 | x64 dynamic binary | csu present | the pair |

## Falsifier

Falsifier — statically linked or stripped binary without __libc_csu_init: the universal pair doesn't exist.
