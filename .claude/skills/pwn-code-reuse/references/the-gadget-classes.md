# The gadget classes — a field guide


- pop — the register setters (the commonest).
- mov-store / mov-load — memory ops.
- xor — zeroing.
- call/jmp — transfers.
- leave/xchg/add — pivots.
- syscall/int — kernel entries.
- ret — alignment.

The chain composes these; the audit reads each's full tail.
