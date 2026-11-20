# The filter layers — four shapes

- string blacklist on names -> getattr/chr-joins
- blocked brackets/quotes -> f-strings, format, dunders
- AST node rejection -> the grammar the checker forgot
- shell keyword block -> $IFS, globs, ${var:offset:1}
- sandbox below the interpreter -> a different class

## The shape table

One escape shape per layer — the map chooses it.
