# The overflow's size class — which chunk — checklist

Companion to `heap-the-overflow-size.md`.

## Checklist

- [ ] Overflow into a same-size neighbor: its size + first data bytes.
- [ ] Into a bigger neighbor: same, but the corruption has more runway.
- [ ] Into a bin-linked chunk: its fd/bk are in reach.
