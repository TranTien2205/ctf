# Remote vs local — the socket format string — checklist

Companion to `remote-vs-local.md`.

## Checklist

- [ ] Line reads need the trailing newline.
- [ ] A length-prefixed protocol caps the fmtstr.
- [ ] A blind service gives no reflected output — write blind or find a
- [ ] nc/python-socket, not pwntools.
