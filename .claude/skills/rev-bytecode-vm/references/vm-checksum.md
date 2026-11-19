# The checksum check

A fold (sum/xor/crc) over input then one cmp — not byte-invertible; a weak checksum is constructible, a digest isn't.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
