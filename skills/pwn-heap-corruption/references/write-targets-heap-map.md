# Heap write targets — where the aim lands — map

Companion to `write-targets-heap.md`.

| Target | Needs | Fires on |
|---|---|---|
| __free_hook | glibc <= 2.34 + libc leak + write | next free() |
| __malloc_hook | <= 2.34 + write | next malloc() |
| FILE vtable/entry | 2.24+ aware; vtable in __libc_IO_vtables | stdio call/exit |
| app function ptr | a live call site | its invocation |
| tcache_perthread_struct | heap addr + write | next tcache op |
| saved env/argv region | stack addr | later reads |
| .bss pointer array | fixed addr (non-PIE) | the next deref |
