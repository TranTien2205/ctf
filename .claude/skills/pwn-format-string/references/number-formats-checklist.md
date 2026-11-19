# Number formats — %d %u %o for read/count — checklist

Companion to `number-formats.md`.

## Checklist

- [ ] %d/%u/%o read args like %x but format differently — same leak.
- [ ] As count-pumps they're interchangeable with %c.
- [ ] If hex chars are filtered from output, %d still leaks as decimal.
