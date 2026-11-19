# State persistence — does the heap survive?


Does state persist across the exploit's ops? On a persistent service:
yes — the corruption accumulates. On a one-shot: the whole chain runs
in one alloc/free sequence.

## The two regimes

- Persistent: the multi-stage recipe applies.
- One-shot: leak and write in one run — the same ops, compressed.

## Falsifier

State resets between connections: every connection starts clean — the
exploit must be self-contained per connection.
