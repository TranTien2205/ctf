# The consolidation window — the timing


Consolidation happens at specific ops — the window between corruption
and consolidation is where the forged state must be perfect.

## The rule

Forge everything BEFORE the trigger runs — a partial forge consumed by
an early consolidate aborts.

## Falsifier

The trigger runs before you finish the forge (an internal malloc you
didn't expect): reorder the ops.
