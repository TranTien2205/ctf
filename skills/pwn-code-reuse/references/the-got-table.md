# The GOT table — the resolved map


readelf -r lists GOT slots — each import's resolved pointer slot.

## The entries

- Symbol's GOT slot = where its resolved address lives.
- Reading it (post-resolution) = the libc leak.
- Writing it (partial RELRO) = the redirect.
