# Object-slot writes — vtables and handlers — checklist

Companion to `fmtstr-write-obj-targets.md`.

## Checklist

- [ ] 1. Find a vtable/handler pointer reachable by the write.
- [ ] 2. Write a fake-vtable address or a direct function.
- [ ] 3. The next virtual/indirect call redirects.
