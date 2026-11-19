# Planting the string — the /bin/sh write — checklist

Companion to `the-string-write.md`.

## Checklist

- [ ] 1. write gadget: mov [rdi], rsi — write "/bin/sh\x00" as a qword.
- [ ] 2. read into .bss: the string arrives via stdin.
- [ ] 3. Existing data: a "sh" substring in the binary (`strings -a`).
