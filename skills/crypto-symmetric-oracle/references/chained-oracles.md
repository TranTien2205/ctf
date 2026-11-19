# Chained oracles — combining two distinguishers

Sometimes neither oracle alone suffices: a verify oracle gives 1 bit but the decrypt endpoint gives length. Chain them — each oracle answers what the other can't.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Decrypt endpoint + verify endpoint | two oracles | compose them |
| Encrypt + error distinguishers | multi-channel | choose per stage |
| Padding oracle AND a timing channel | double oracle | use the cheaper one per step |

## Steps

1. Enumerate all endpoints and what each returns.
2. Match each stage of the attack to the oracle that gives the needed bit.
3. Use the cheapest distinguisher for the bulk work (status over timing).
4. Use the richer oracle only where the cheaper one can't discriminate.

## Falsifier

Falsifier — neither oracle discriminates the needed bit: the attack requires a channel neither provides. Re-run detection for a missed one.

## Traps

- The verify oracle's bit is the pad-oracle's bit under a different name — check they differ meaningfully.
- Rate limits differ per endpoint — budget per endpoint separately.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`cbc-padding-oracle.md` · `verify-oracle.md`
