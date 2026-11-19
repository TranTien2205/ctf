# The protections map — what each blocks — map

Companion to `the-protections-map.md`.

| Protection | Blocks | Route left |
|---|---|---|
| NX | shellcode | the chain itself |
| PIE | fixed addresses | leak a code ptr first |
| canary | naive overwrite | leak it |
| full RELRO | GOT writes | ret targets / hooks |
| partial RELRO | (nothing extra) | GOT writes ok |
| ASLR (system) | libc addrs | the leak |
