# The pointer array — the exploitation hub


Most heap services store object pointers in a .bss array — the hub
every technique passes through.

## Its roles

- The leak source: reading a slot's pointer is a heap disclosure.
- The UAF holder: an uncleared slot is the dangling reference.
- The write target: the array is .bss-fixed (non-PIE).
- The confusion surface: slot N's pointer written = retargeted ops.

## Falsifier

The pointers live elsewhere (list/tree on the heap): the table is
different — the techniques adapt to the real container.
