# Remote vs local — the socket format string

A remote fmtstr is a socket conversation: send the specifier run, read
the reflected output (or not — blind). The payload must survive the
transport's framing.

- Line reads need the trailing newline.
- A length-prefixed protocol caps the fmtstr.
- A blind service gives no reflected output — write blind or find a
  second channel.
- nc/python-socket, not pwntools.
