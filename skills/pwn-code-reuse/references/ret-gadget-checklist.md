# The bare ret — stack alignment — checklist

Companion to `ret-gadget.md`.

## Checklist

- [ ] system()/many libc calls require 16-byte rsp alignment at entry —
- [ ] Insert one `ret` before the call target — the crash becomes a clean
