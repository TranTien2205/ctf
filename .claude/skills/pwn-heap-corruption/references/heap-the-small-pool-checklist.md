# Small allocation pools — the tiny services — checklist

Companion to `heap-the-small-pool.md`.

## Checklist

- [ ] No unsorted leak from small sizes — need a different libc source.
- [ ] The dup/poison paths dominate.
