# Chained oracles — combining two distinguishers — operational checklist

Sometimes neither oracle alone suffices: a verify oracle gives 1 bit but the decrypt endpoint gives length. Chain them — each oracle answers what the other can't.

## Checklist

- [ ] Enumerate all endpoints and what each returns.
- [ ] Match each stage of the attack to the oracle that gives the needed bit.
- [ ] Use the cheapest distinguisher for the bulk work (status over timing).
- [ ] Use the richer oracle only where the cheaper one can't discriminate.

## Abort conditions

- The verify oracle's bit is the pad-oracle's bit under a different name — check they differ meaningfully.
- Rate limits differ per endpoint — budget per endpoint separately.

## Falsifier

Falsifier — neither oracle discriminates the needed bit: the attack requires a channel neither provides. Re-run detection for a missed one.

## Cross-references

`cbc-padding-oracle.md` · `verify-oracle.md`
