# Stack vs heap fmt buffer — where the input sits — deep

Companion to `fmtstr-stack-vs-heap.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed.
