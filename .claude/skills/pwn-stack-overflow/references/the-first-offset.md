# The first offset — the one number that starts everything

The offset to saved RIP is the bug's single most important number: every
chain is `pad-to-offset + chain`. It is measured by `tools/pwn_cyclic.py`
once, then trusted for the whole run — ASLR changes addresses, never the
offset.

Measure it before any chain is designed; a guessed offset wastes the
whole attempt.
