# The edit op — the corruption channel — checklist

Companion to `the-edit-op.md`.

## Checklist

- [ ] edit on a tcache chunk → set fd = (pos>>12)^target — the poison.
- [ ] edit on an unsorted chunk → corrupt its fd/bk — bin-link write.
- [ ] edit on a live object → normal data write.
