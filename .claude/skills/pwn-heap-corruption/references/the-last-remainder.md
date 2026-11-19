# last_remainder — the cached split fragment


main_arena.last_remainder caches the last split fragment — the next
non-exact malloc can serve from it directly.

## Exploitation

- Corrupting last_remainder redirects the served chunk.
- The remainder's own fd/bk (unsorted-era) can leak/corrupt.

## Falsifier

The remainder is consumed before you can use it: the cached-fragment
path isn't available.
