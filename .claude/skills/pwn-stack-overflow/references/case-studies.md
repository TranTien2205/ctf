# Case studies — the canonical shapes

Not solved-here claims — the standard shapes the class was built against.

## 1. The gets() challenge

`gets(buf)` into a stack buffer, NX off, no canary, no PIE: the shortest
chain — shellcode on the stack, ret to it.

## 2. The read() with a length you control

`read(0, buf, *(int*)&size)` where `size` is read from input — set it huge,
the overflow is full.

## 3. The PIE + canary + format-string

A printf(input) exists too: leak canary + PIE base via %p, then ret2libc.
Two stages, the format-string is the leak not the exploit.

## 4. The ret2win drop-in

`void win() { system("cat flag"); }` exists — pad + p64(win). Done.

## 5. The one-shot remote

nc service, single input, NX on, libc-linked: compose leak+smash in one
input — a format read inside the smash, or a no-leak chain.

## 6. The fork-server canary

Per-connection fork reuses the canary: byte-by-byte brute across ~2048
connections, then the smash.

## 7. Where nothing worked

Full RELRO + canary + PIE + no leak primitive: stack route closed —
recorded as negative; the bug was real but unreachable with the primitives
present.
