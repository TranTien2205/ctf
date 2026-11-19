# The arg-size edge — %ln vs %n on x32


On x86, %n writes 4 bytes; %ln also 4 bytes (long = 32-bit on i386). The
write width differs between ABIs.

| Specifier | x86 | x64 |
|---|---|---|
| %n | 4 bytes | 4 bytes (int) |
| %ln | 4 bytes | 8 bytes |
| %lln | 8 bytes | 8 bytes |

## Falsifier

The write width isn't what the target needs: pick the right width
specifier.
