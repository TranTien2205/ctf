# PIE leak — getting the code base under ASLR

PIE randomizes the binary's base: every function/gadget/data address is base+offset. A leak of ANY code/data pointer gives the base.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| PIE enabled | all addresses relative | leak a pointer |
| a read shows a code/data address | base recoverable | subtract the offset |
| a format-string or info-leak | leak primitive | use it |

## Steps

1. Confirm PIE via readelf -h (Type: DYN) or pwn_triage.
2. Find a leak: format-string %p, an uninitialized read, a puts of a pointer.
3. base = leaked_addr - known_offset (the offset from source or symbols).
4. Now every static address = base + offset.

## Falsifier

Falsifier — PIE on and no leak primitive exists: addresses can't be resolved; need a brute-force or a partial-overwrite trick.

## Traps

- A partial overwrite of the low 2 bytes can redirect to a nearby function without a full leak.
- Fork servers re-leak per connection if the base is re-randomized — re-leak each time.
- The leaked offset is symbol-specific — get it from the binary's symbols.

## Commands

```bash
readelf -h ./chal | grep Type
r2 -A ./chal && afl
```

## Cross-references

`protection-modes.md` · `canary-bypass.md`
