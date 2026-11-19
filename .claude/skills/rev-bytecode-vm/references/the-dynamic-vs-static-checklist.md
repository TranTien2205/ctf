# Dynamic vs static — which decode applies — checklist

Companion to `the-dynamic-vs-static.md`.

## Checklist

- [ ] The dispatch table is fixed in the binary.
- [ ] The program array is a static buffer.
- [ ] The decode is deterministic from the bytes.
- [ ] The table/program is runtime-generated.
- [ ] Self-modifying code mutates the stream.
- [ ] The program is too long to hand-decode — trace it.
