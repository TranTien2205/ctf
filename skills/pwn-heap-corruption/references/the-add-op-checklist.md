# The add op — allocation as a tool — checklist

Companion to `the-add-op.md`.

## Checklist

- [ ] Allowed sizes: fixed set? arbitrary? min/max?
- [ ] Slot limit: the global array's cap bounds the spray.
- [ ] Does it read data into the object (controllable bytes) or just
- [ ] Reuse of slots: does add find a free slot or append?
