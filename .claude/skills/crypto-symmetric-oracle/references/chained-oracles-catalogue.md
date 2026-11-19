# Chained oracles — combining two distinguishers — case catalogue

Sometimes neither oracle alone suffices: a verify oracle gives 1 bit but the decrypt endpoint gives length. Chain them — each oracle answers what the other can't.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Decrypt endpoint + verify endpoint | two oracles | compose them |
| 2 | Encrypt + error distinguishers | multi-channel | choose per stage |
| 3 | Padding oracle AND a timing channel | double oracle | use the cheaper one per step |

## Falsifier

Falsifier — neither oracle discriminates the needed bit: the attack requires a channel neither provides. Re-run detection for a missed one.

## Coverage notes

- The verify oracle's bit is the pad-oracle's bit under a different name — check they differ meaningfully.
- Rate limits differ per endpoint — budget per endpoint separately.

## Cross-references

`cbc-padding-oracle.md` · `verify-oracle.md`
