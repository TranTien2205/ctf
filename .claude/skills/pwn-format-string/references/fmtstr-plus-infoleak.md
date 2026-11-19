# Fmtstr + separate info-leak — two primitives, one chain


A binary can have a format-string write AND a separate info-leak (uninit
read, a dump, a different printf): the info-leak feeds the fmtstr's
targets.

## Steps

1. Use whatever leak exists — it doesn't have to be the fmtstr itself.
2. An uninit stack read, a debug dump, an error message — all are leaks.
3. Feed the values into the %n write's target/value.

## Falsifier

No leak of any kind exists: addresses are unknowable → only
deterministic targets.
