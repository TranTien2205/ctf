# Same-page redirect — the 2-byte %hn trick


To redirect a call to a function in the SAME binary, often only the low
1-2 bytes differ: %hn writes 2 bytes — a partial overwrite reaching any
same-64KB target.

## Steps

1. Compare the target's address with the slot's current value.
2. Overwrite only the differing low bytes with %hn/%hhn.
3. No leak needed for same-binary redirects — the high bytes stay.

## Falsifier

The target's high bytes differ and can't be composed: full write needed.
