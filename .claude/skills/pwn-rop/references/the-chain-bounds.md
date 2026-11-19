# Chain bounds — the length limit


The chain's length = the qwords it packs — bounded by the read's
limit:

    chain_bytes = (n_gadgets + n_args) * 8
    fits = offset + chain_bytes <= the read's limit

## The fixes when over

- Compress: fewer gadgets (the substitutes that do more).
- Stage: write the rest elsewhere, pivot.
- Shorten: a win function or one-gadget ending.
