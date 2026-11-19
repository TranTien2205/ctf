# The bounded sweep — scope discipline — case catalogue

Info-disclosure sweeps are bounded by definition: a short list of well-known paths, not a scanner. The class lives inside the supplied surface.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | ~15-20 canonical paths | the sweep | run once, read carefully |
| 2 | a hinted path (comment, header, error) | targeted probe | add exactly that one |
| 3 | shared host | politeness bound | no brute-force |

## Falsifier

Falsifier — canonical list all-negatives AND no evidence names a custom path: the disclosure surface is closed.

## Coverage notes

- Directory brute-forcing (ffuf/gobuster wide) is not this class — it's a scope violation on shared infra.
- A path you invent has no evidence to stand on — don't probe it.
- The sweep is once per target; re-run only when new evidence names a path.

## Cross-references

`exposed-artifacts.md` · `catchall-falsifier.md`
