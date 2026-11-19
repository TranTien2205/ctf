# The route map — choosing by protections


| Protections | The route |
|---|---|
| NX only, non-PIE, dynamic | ret2plt → GOT leak → ret2libc |
| NX + PIE | leak a code ptr → same as above + base |
| NX + static | syscall gadgets — no libc needed |
| NX + full RELRO | PLT calls only — no GOT writes |
| NX + canary | leak the canary first |

The protections name the route before any gadget is chosen.
