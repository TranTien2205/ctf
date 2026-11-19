# Symmetric-oracle workflow — the ordered path — checklist

The class is defined by one question: which oracle do you hold? Everything
else is mechanical once that is named.

## Checklist

- [ ] Determinism: submit identical input twice. Same output → ECB or fixed-IV.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
