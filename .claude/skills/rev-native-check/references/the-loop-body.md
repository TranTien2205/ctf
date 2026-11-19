# The loop body — the iterated compare


The compare loop's body: load input[i], transform, load expected[i],
compare, jne-fail — the per-byte check; the expected array's address
is the extraction.
