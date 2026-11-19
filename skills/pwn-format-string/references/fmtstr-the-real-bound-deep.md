# The real bound — what actually limits the fmtstr — deep

Companion to `fmtstr-the-real-bound.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
