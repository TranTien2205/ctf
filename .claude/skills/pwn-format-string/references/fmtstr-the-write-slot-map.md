# Choosing the slot — GOT vs ret vs hook decision — map

Companion to `fmtstr-the-write-slot.md`.

| Slot | Needs | Fires on |
|---|---|---|
| GOT[x] | partial RELRO + x called next + right arg | next call to x |
| saved ret | stack addr leak | function return |
| __free_hook | glibc <= 2.34 + a free | next free() |
| a stack function-ptr | stack addr leak | its call |
