# The checksum check — not a compare

Some VMs don't compare per-byte — they checksum the whole input and
compare the result. The flag isn't byte-recoverable from the
expected value alone.

## The recognizer

No per-byte cmp; a fold (sum/xor/crc) over the input then one final
cmp.

## The consequence

The flag can't be inverted from the checksum — but the check
CONFIRMS an input. If the checksum is weak (sum), many inputs pass
— construct any. If it's a digest, the flag is elsewhere or
brute-forceable if short.
