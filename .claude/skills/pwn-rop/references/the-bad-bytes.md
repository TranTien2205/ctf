# Bad bytes — the transport's constraints


Bytes the channel mangles end the chain:

- 0x00: the gets-style terminator — an address's high bytes are zeros;
  the LAST address truncating the read is usually fine, a mid-chain
  zero truncates early.
- 0x0a/0x0d: the line-read terminator.
- Others the filter strips.

## The moves

- Pick gadget addresses without the bad bytes.
- Compute a bad-byte value via xor instead of a literal.
- Use a non-line-based channel if the protocol offers one.
