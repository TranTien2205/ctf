# The format string as data — reading your own input


Your input buffer appears in the %p dump as its byte values — 'AAAA'
shows as 0x41414141 — the marker that locates your arg position.

## Steps

1. The dump shows your input's bytes — 'AAAA' = 0x41414141.
2. Find it to name the arg-offset N.
3. An 8-byte marker (AAAABBBB) rules out coincidence.

## Falsifier

The marker never appears: the input isn't a stack arg; re-check the call.
