# Anti-patterns — disclosure edition

The moves that look productive and aren't.

## Steps

1. Running ffuf/gobuster wide on a shared host instead of the bounded list.
2. Calling a catch-all 200 a 'find'.
3. Probing invented paths with no evidence behind them.
4. Downloading the archive without listing it first.
5. Grep'ing the dump by opening it in an editor.
6. Committing a found credential into the repo.
7. Stopping at the artifact without chaining it to impact.
8. Re-running the same sweep after a negative.

## Falsifier

--

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
