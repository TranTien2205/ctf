# Endgame table — ending shapes by primitive — checklist

Companion to `the-endgame-table.md`.

## Checklist

- [ ] Primitive available | The ending
- [ ] arb write + hooks exist | hook = system/one-gadget
- [ ] arb write + no hooks | FSOP vtable / app fn ptr
- [ ] arb read only | flag-in-mem / environ→stack→ret read
- [ ] overlap + confusion | ptr forge → read or call
- [ ] value-limited write | counts[]/flag-word corruption
