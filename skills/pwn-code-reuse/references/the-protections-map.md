# The protections map — what each blocks


| Protection | Blocks | Route left |
|---|---|---|
| NX | shellcode | the chain itself |
| PIE | fixed addresses | leak a code ptr first |
| canary | naive overwrite | leak it |
| full RELRO | GOT writes | ret targets / hooks |
| partial RELRO | (nothing extra) | GOT writes ok |
| ASLR (system) | libc addrs | the leak |

Read the triage report — it names each protection and its evidence.
