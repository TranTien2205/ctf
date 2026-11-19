# Multiple vulnerable functions — which one to hit — checklist

Companion to `multiple-vuln-funcs.md`.

## Checklist

- [ ] A binary can have several stack-corruption surfaces: the 'name' buffer,
- [ ] the 'comment' buffer, a recursive parser. Pick the one whose protections
- [ ] and bounds are friendliest.
- [ ] The function with no canary in its own frame.
- [ ] The read with the loosest byte filter.
- [ ] The buffer closest to saved state (smallest offset).
- [ ] The function reachable earliest in the protocol.
- [ ] Disassemble each candidate; the one with no %fs:0x28 load and the
- [ ] loosest read is the target.
