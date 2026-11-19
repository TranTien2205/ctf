# The double-write — pointer chains through two writes — checklist

Companion to `the-double-write.md`.

## Checklist

- [ ] 1. Write the pointer value into a writable slot (bss/stack var).
- [ ] 2. That slot is now an argument containing your pointer.
- [ ] 3. Second call: %N$s/%N$n at that slot's index → uses your pointer.
