# TTL + resolver — record drift

Record answers change — note the TTL and which resolver answered;
a cached answer may differ from the authoritative one. Query the
authoritative NS directly when it matters.

## Why it matters

- A just-changed record's old answer may still be cached.
- The authoritative NS has the current truth — use `--server <ns>`.
- The TTL tells how long a cached answer could be stale.
- Quote the resolver + date with the answer for provenance.

## A changed answer

When two queries disagree, prefer the authoritative NS and note both + the time — the diff is the signal.
