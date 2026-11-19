# ret2csu — the universal gadget pair — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| __libc_csu_init in symbols | universal gadgets exist | use the pair |
| no pop rdx gadget anywhere | csu supplies it | the pair |
| x64 dynamic binary | csu present | the pair |

## Falsifier

Falsifier — statically linked or stripped binary without __libc_csu_init: the universal pair doesn't exist.
