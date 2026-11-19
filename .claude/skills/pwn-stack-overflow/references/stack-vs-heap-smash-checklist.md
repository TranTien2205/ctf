# Stack smash vs heap metadata — the ownership boundary — checklist

Both are 'write past a buffer'; which class owns it depends on WHERE the corruption lands: stack frames belong here, heap chunk metadata belongs to pwn-heap-corruption.

## Checklist

- [ ] Identify the buffer's allocation: local array (stack) vs malloc (heap).
- [ ] A stack-local buffer's overflow reaches the saved frame — this class.
- [ ] A malloc'd buffer's overflow reaches the next chunk's metadata — heap class.
- [ ] The cyclic/fault test works for both; the LANDING site names the class.

## Abort conditions

- Same primitive, different target — the cyclic test doesn't distinguish; the fault does.
- A malloc'd buffer can still be adjacent to stack-relevant data only in exotic layouts.
- The owning class decides which skill's chains apply.

## Falsifier

Falsifier — the corruption demonstrably lands in heap metadata (a chunk header), not the stack frame: route to pwn-heap-corruption.
