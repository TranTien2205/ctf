# Evidence discipline for oracle challenges — checklist

The oracle is a claim about a response channel. Evidence = the two responses
that differ, quoted verbatim.

## Checklist

- [ ] A plausible-looking error — must differ from the OTHER corruption's error.
- [ ] A timing guess — must survive 50+ samples on both sides.
- [ ] A flag-shaped string typed into the request — only a response carries it.
- [ ] "The ciphertext looks random" — no oracle signal either way.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
