# The add op — allocation as a tool


add(size, data) is the alloc primitive — its size granularity and count
limit shape every technique.

## Check

- Allowed sizes: fixed set? arbitrary? min/max?
- Slot limit: the global array's cap bounds the spray.
- Does it read data into the object (controllable bytes) or just
  allocate?
- Reuse of slots: does add find a free slot or append?

## Falsifier

The size/count caps can't express the needed bin sequence: the
technique family shrinks to what the ops allow.
