# The final checks — before firing the redirect


The last verification pass — every stage independently confirmed:

1. The offset N — verified against the marker THIS call site.
2. The planted pointer — %N$p prints it correctly.
3. The count arithmetic — the ledger adds up.
4. The target slot — the address valid, the firing condition real.
5. The write width — %hhn/%hn/%n matching the target.
6. The redirect's trigger — call/return/free will happen.

A failure at any check means that stage, not the whole exploit. Re-run
the failed stage only.
