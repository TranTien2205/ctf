# Detection matrix — which channel is open — surface variants

One table: the probe, the positive answer, the file that owns it.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| /.git/HEAD = 'ref:' | git exposed | git-exposure |
| /.env* = KEY=VALUE | config leak | env-config-leaks |
| archive 200 + magic bytes | backup exposed | backup-archives |
| sourceMappingURL or .map | source maps | source-maps |

## Variant-specific traps

- Status is not the discriminator — content is.
- Each channel has its own falsifier; a closed channel doesn't close the class.

## Falsifier

Falsifier — the whole bounded list returns catch-all content: no channel is open.

## Cross-references

`bounded-sweep.md` · `catchall-falsifier.md`
