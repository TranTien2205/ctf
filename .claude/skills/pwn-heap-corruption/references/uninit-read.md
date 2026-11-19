# Uninitialized chunk read — stale data leaks


A newly-allocated chunk returned without zeroing carries the previous
user's bytes — reading it leaks whatever was there.

## Steps

1. Free an object that held secrets (or bin pointers — a freed chunk's
   fd/bk sit in its user area).
2. Alloc same size → the chunk returns with stale bytes.
3. Read the "new" object's fields → the stale data leaks.

## Sources of stale data

- A freed chunk's fd/bk (bin links) — heap/arena pointers.
- A previously freed object's fields — app data, keys, flags.
- tc->key fields.

## Falsifier

The program calloc's (zeroing) or memsets on alloc: the stale read is
clean — no leak.
