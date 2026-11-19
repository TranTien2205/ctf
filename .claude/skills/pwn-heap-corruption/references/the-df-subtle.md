# The subtle double-free — via different paths


A chunk freed through two different names/paths: free(ptr) then
free(alias) where alias names the same chunk — the program doesn't
see the duplicate.

## Sources

- Two slot indexes pointing at the same chunk (index confusion).
- A path alias — obj->buf vs obj itself.
- A stale pointer re-freed after re-alloc.

## Falsifier

Every alias tracked: no path frees the same chunk twice.
