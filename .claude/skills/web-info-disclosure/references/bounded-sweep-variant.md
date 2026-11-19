# The bounded sweep — scope discipline — surface variants

Info-disclosure sweeps are bounded by definition: a short list of well-known paths, not a scanner. The class lives inside the supplied surface.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| ~15-20 canonical paths | the sweep | run once, read carefully |
| a hinted path (comment, header, error) | targeted probe | add exactly that one |
| shared host | politeness bound | no brute-force |

## Variant-specific traps

- Directory brute-forcing (ffuf/gobuster wide) is not this class — it's a scope violation on shared infra.
- A path you invent has no evidence to stand on — don't probe it.
- The sweep is once per target; re-run only when new evidence names a path.

## Falsifier

Falsifier — canonical list all-negatives AND no evidence names a custom path: the disclosure surface is closed.

## Cross-references

`exposed-artifacts.md` · `catchall-falsifier.md`
