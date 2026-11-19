# PIE leak — getting the code base under ASLR — checklist

PIE randomizes the binary's base: every function/gadget/data address is base+offset. A leak of ANY code/data pointer gives the base.

## Checklist

- [ ] Confirm PIE via readelf -h (Type: DYN) or pwn_triage.
- [ ] Find a leak: format-string %p, an uninitialized read, a puts of a pointer.
- [ ] base = leaked_addr - known_offset (the offset from source or symbols).
- [ ] Now every static address = base + offset.

## Abort conditions

- A partial overwrite of the low 2 bytes can redirect to a nearby function without a full leak.
- Fork servers re-leak per connection if the base is re-randomized — re-leak each time.
- The leaked offset is symbol-specific — get it from the binary's symbols.

## Falsifier

Falsifier — PIE on and no leak primitive exists: addresses can't be resolved; need a brute-force or a partial-overwrite trick.
