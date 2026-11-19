# Remote fmtstr — protocol framing of specifiers — checklist

Companion to `remote-fmtstr-protocol.md`.

## Checklist

- [ ] 1. Send 'AAAA.%N$p\n' over the socket; read the reflected output.
- [ ] 2. Line-reads need the trailing newline.
- [ ] 3. Specifier bytes (% etc.) are printable — no transport filtering
- [ ] 4. Planted pointers need raw bytes — \x00 can't ride a line-read.
