# Env-free input — fmtstr through argv/env/file — deep

Companion to `env-free-input.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative byte-count. Every specifier is index-addressed — locate N, steer the count, choose the target.
