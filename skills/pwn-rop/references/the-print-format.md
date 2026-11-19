# The print's format — how the leak arrives


- puts: raw bytes + newline — the leak is the line minus the newline.
- write: exactly n bytes — no terminator.
- printf("%p"): the hex text — parse, don't unpack.

## The parse

Match the printer's format when unpacking the leak.
