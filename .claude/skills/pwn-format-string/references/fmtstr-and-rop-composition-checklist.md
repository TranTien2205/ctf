# Fmtstr + ROP — the write that feeds the chain — checklist

Companion to `fmtstr-and-rop-composition.md`.

## Checklist

- [ ] The write lands a gadget's address → the chain's start.
- [ ] The ret-addr or GOT points to the chain → the redirect.
- [ ] 1. Write the chain's first gadget address via %n.
- [ ] 2. The return/call redirects to it — the ROP chain runs.
- [ ] 3. Compose: leak (if needed) → %n write → chain executes.
