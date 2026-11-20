# The traps

- Hard-coding a `__subclasses__` index from a different build.
- A word-blacklist escape against an AST check (or vice versa).
- Calling a returned value execution without observing the effect.
- Treating a sandbox below the interpreter as a name filter.

- A hard-coded subclass index.
- The wrong-layer escape.
- A returned value called execution.
