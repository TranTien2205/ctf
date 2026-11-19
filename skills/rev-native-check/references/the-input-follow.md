# Following the input — forward from the read


The complementary route: find the input read (read/fgets/scanf/gets),
follow the buffer to the compare.

## The trace

- afl + the imports list the read function.
- Its destination buffer is a stack/global slot.
- The compare reads that slot — the deciding check.
