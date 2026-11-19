# The newline — the other terminator


A 0x0a in a payload byte ends line-based reads — an address or
argument containing 0x0a truncates the chain.

## The workaround

Pick different gadgets (addresses without 0x0a), or compute the
argument rather than pass it literal, or use a non-line-based input
channel.
