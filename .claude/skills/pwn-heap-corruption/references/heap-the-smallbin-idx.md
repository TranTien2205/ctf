# Smallbin index — the 62 classes


Small bins cover sizes below largebin's floor — 62 sorted doubly-linked
lists; index math differs from tcache's.

## The note

Smallbin insert/unlink has the fd<->bk consistency checks (2.30+) — the
strictest bin for link forgery.

## Falsifier

The forged links can't satisfy both directions: smallbin is closed.
