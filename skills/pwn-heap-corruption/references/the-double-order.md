# A-B-A vs A-A — the ordering detail


fastbin top-check: top==victim is rejected — so A-A fails, A-B-A
passes: the ORDER of the two frees is the bypass.

## The subtlety

- free(A); free(A) → aborts (top==A).
- free(A); free(B); free(A) → passes (top==B on the third).

## Falsifier

No second chunk exists to interpose (one alloc only): the order trick
can't run — the key-clear route is needed instead.
