# The timing angle — the oracle check


A byte-by-byte check that exits early leaks per-position correctness
— the timing/exit-pattern oracle brute-forces the input byte by byte
without replication.

## The shape

Feed a prefix; a longer-running or different response means the
prefix was right — the classic strcmp-timing attack's offline form.
