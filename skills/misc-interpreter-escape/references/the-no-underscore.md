# No underscores — build the dunder

`chr(95)+chr(95)` builds `__`; `getattr(x,chr(95)*2+'class'+chr(95)*2)`
reaches `__class__` with no literal underscore.

## chr(95)

chr(95)*2 builds __ — no literal underscore.
