# The recv shape — reading the response — checklist

Companion to `the-recv-shape.md`.

## Checklist

- [ ] Fixed-size: recv(n) until n bytes.
- [ ] Delimited: until a marker (a newline, a prompt).
- [ ] Timed: until quiet — a heuristic, not a guarantee.
