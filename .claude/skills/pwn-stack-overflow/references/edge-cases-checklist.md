# Edge cases — the odd shapes — checklist

Companion to `edge-cases.md`.

## Checklist

- [ ] Shape
- [ ] buffer at frame edge (adjacent to canary)
- [ ] a struct field, not a bare buffer
- [ ] recursion into the vulnerable func
- [ ] the input is parsed before the copy
- [ ] two reads into adjacent buffers
- [ ] a signed char index
- [ ] vfork/clone shares the stack
- [ ] signal-handler frame on the stack
