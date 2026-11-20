# Query the authoritative NS directly

`dig @ns1.example.com name` or `--server` — bypasses the caching
resolver for the current answer; matters when records were just
changed.

## When to use it

- The answer differs across resolvers — ask the authoritative.
- A just-planted record — the cache hasn't caught up.
- The authoritative answer is the truth for the zone.
