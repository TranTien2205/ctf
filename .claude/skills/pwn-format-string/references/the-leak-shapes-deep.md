# The leak shapes — recognizing what's in the %p dump — deep

Companion to `the-leak-shapes.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
