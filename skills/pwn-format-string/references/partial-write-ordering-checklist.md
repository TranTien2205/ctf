# Partial-write ordering — which bytes first — checklist

Companion to `partial-write-ordering.md`.

## Checklist

- [ ] If the target's high bytes match the existing value: only overwrite
- [ ] If the whole address differs: %hhn at each byte offset.
- [ ] A 2-byte %hn redirect reaches the same 64KB region.
- [ ] 1. Compare the target to the existing value — which bytes differ?
- [ ] 2. Only overwrite the differing bytes.
- [ ] 3. Write them in an order that keeps the running count producing the
