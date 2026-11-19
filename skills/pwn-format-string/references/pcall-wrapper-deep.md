# pcall/xpcall wrappers — the protected call — deep

Companion to `pcall-wrapper.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
