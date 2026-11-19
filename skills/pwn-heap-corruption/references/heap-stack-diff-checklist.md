# Heap vs stack corruption — why the recipes differ — checklist

Companion to `heap-stack-diff.md`.

## Checklist

- [ ] No single "return address" target — the targets are bin pointers,
- [ ] The write often happens on a LATER alloc/free — not on the corrupting
- [ ] Order matters more than bytes: the alloc/free sequence IS the
- [ ] Detection is indirect: crashes on malloc/free, wrong-size returns,
