# The fd's shape — what a bin link looks like — checklist

Companion to `bin-fd-shape.md`.

## Checklist

- [ ] 0x55/0x56-shaped fd → tcache/fastbin (heap).
- [ ] 0x7f..-shaped fd → arena-resident (unsorted/small/large).
- [ ] mangled fd (2.32+) → weird values — de-mangle with pos>>12.
