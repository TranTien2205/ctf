# What value the techniques write — checklist

Companion to `the-write-value.md`.

## Checklist

- [ ] Technique | The written value
- [ ] unsorted-bin attack | a main_arena address (fixed, libc)
- [ ] largebin bk_nextsize | a heap chunk address
- [ ] tcache poison | your chosen pointer (post-leak)
- [ ] house-of-force | the top — then arbitrary via alloc
- [ ] overlap → ptr forge | your controlled bytes
- [ ] FSOP vtable | a vtable-region address
