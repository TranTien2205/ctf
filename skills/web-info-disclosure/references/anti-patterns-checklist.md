# Anti-patterns — disclosure edition — operational checklist

The moves that look productive and aren't.

## Checklist

- [ ] Running ffuf/gobuster wide on a shared host instead of the bounded list.
- [ ] Calling a catch-all 200 a 'find'.
- [ ] Probing invented paths with no evidence behind them.
- [ ] Downloading the archive without listing it first.
- [ ] Grep'ing the dump by opening it in an editor.
- [ ] Committing a found credential into the repo.
- [ ] Stopping at the artifact without chaining it to impact.
- [ ] Re-running the same sweep after a negative.

## Abort conditions

- --

## Falsifier

--

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
