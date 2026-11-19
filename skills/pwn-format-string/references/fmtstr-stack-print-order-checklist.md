# The stack print order — what %p.%p.%p reveals — checklist

Companion to `fmtstr-stack-print-order.md`.

## Checklist

- [ ] %1$p .. %6$p: register args (rsi..r9-ish).
- [ ] %7$p onward: stack slots — the call's overflow area.
- [ ] Deeper: saved rbp, saved rip, caller locals, argv/env pointers.
- [ ] Somewhere: your input buffer's bytes (the marker).
- [ ] 0x55/0x56 prefix — binary/PIE pointer.
- [ ] 0x7f prefix — libc/mmap/stack.
- [ ] 0x7ff... — stack address.
- [ ] 0x41414141 — your marker.
