# The print-object op — blessed leaks — checklist

Companion to `the-object-print.md`.

## Checklist

- [ ] Does show() print any pointer-valued field? That's a free heap leak.
- [ ] Does it print raw memory or only safe fields?
