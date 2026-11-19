# A-B-A vs A-A — the ordering detail — checklist

Companion to `the-double-order.md`.

## Checklist

- [ ] free(A); free(A) → aborts (top==A).
- [ ] free(A); free(B); free(A) → passes (top==B on the third).
