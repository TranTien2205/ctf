# Offset measurement — getting the exact byte count — checklist

The offset IS the bug's geometry: input_start → saved_return_address. Measure it empirically; never guess.

## Checklist

- [ ] python3 tools/pwn_cyclic.py 300 > pattern.txt — generate.
- [ ] Send the pattern; the process crashes at the pattern's offset-k bytes overwriting the saved RIP.
- [ ] Read RIP's 4 pattern bytes (r2 -d, core, or the service's dump).
- [ ] python3 tools/pwn_cyclic.py --find <bytes> — the offset.

## Abort conditions

- The pattern is de Bruijn — every 4-byte window is unique; --find needs the 4 bytes from RIP.
- Offset = bytes to saved RIP; padding = offset - (bytes that precede it including saved RBP).
- The crash message's fault address in dmesg/stderr may be the DATA not RIP — read the register.

## Falsifier

Falsifier — no input length produces a faulting RIP holding pattern bytes: the write doesn't reach saved state at this length; re-check the bound.
