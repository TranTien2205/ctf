# Worked example — the table check


1. input[i] indexes table[i] (a 256-byte permutation).
2. The compare: table[input[i]] == stored[i].
3. Invert: answer[i] = table_inverse[stored[i]] — the table dumped
   via pxq.
4. Verify.
