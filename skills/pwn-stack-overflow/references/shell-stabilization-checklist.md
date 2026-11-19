# Shell stabilization — making the landed shell usable — checklist

Companion to `shell-stabilization.md`.

## Checklist

- [ ] A landed shell over a socket service is often a raw fd connection:
- [ ] commands go over stdin (the socket), output comes back. Stabilizing it
- [ ] is the difference between 'it worked' and 'I can use it'.
- [ ] rev64's reverse shell connects out — a listener on your side.
- [ ] cat64's flag-read writes to the socket — read the response.
- [ ] execve64's /bin/sh talks over the socket.
- [ ] A shell that opens but the flag-read path is wrong (/flag vs flag.txt vs
- [ ] ./flag) — find the real path first.
