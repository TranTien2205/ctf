# Which frees you control — the surface


Enumerate the free paths: which slots, which objects, in what order —
the frees available bound the techniques.

## The map

- delete(i): frees slot i — ordering controllable if the menu allows.
- An internal free on error paths — frees you don't fully control.
- Implicit frees (realloc move, string replace).

## Falsifier

Exactly one free exists in the whole program: techniques needing
multiple frees are closed.
