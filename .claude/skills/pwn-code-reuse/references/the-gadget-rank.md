# Ranking gadgets — the cleanest first


Among several addresses for the same tail: prefer —

1. No side effects (just the pop + ret).
2. A clean address (no bad bytes).
3. A short encoding (for size-constrained inputs).

The audit of each candidate picks the best.
