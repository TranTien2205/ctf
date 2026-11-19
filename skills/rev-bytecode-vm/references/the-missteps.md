# Missteps — the recurring wrong turns

- marshal.loads before checking the magic.
- Decompiling when dis would do.
- Reading the byte stream without the opcode table.
- Decoding byte-order not jump-order.
- Counting a flag-shaped constant as the answer.
- Hand-reading a 10k-instruction program — script the decode.
