# Reading past the varargs — raw stack scraping


Varargs beyond the declared count read RAW stack memory: saved registers,
return addresses, the canary — the deep leak that feeds ret-addr
knowledge.

## Steps

1. Keep raising N past the (nil) boundary — you're reading raw stack.
2. Return addresses appear as code pointers (0x40.../0x55...).
3. Saved rbp values appear as stack pointers (0x7ff...).
4. The canary appears at its frame position.

## Falsifier

A read hits an unmapped guard region and crashes before reaching the
useful depth. printf bounds-checks nothing — unmapped pages fault.
