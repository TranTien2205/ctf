# The pointer array — the exploitation hub — checklist

Companion to `heap-the-ptr-array.md`.

## Checklist

- [ ] The leak source: reading a slot's pointer is a heap disclosure.
- [ ] The UAF holder: an uncleared slot is the dangling reference.
- [ ] The write target: the array is .bss-fixed (non-PIE).
- [ ] The confusion surface: slot N's pointer written = retargeted ops.
