# Worked example — the xor transform


1. The compare loop xors input[i] with a key byte, compares to a
   stored byte.
2. The key stream: a fixed byte, or key[i] = table[i] — dump the
   source.
3. answer[i] = stored[i] ^ key[i] — the Python inversion.
4. Verify.
