# Write-what-where — the primitive that builds everything

A controlled write to a controlled address is the universal exploit primitive: GOT entries, return addresses, hooks all become targets.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| arbitrary write exists | the master primitive | GOT/hook/ret targets |
| stack smash that reaches arbitrary stack slots | controlled writes | place them |

## Steps

1. Identify the write primitive: overflow? format-string %n? array-index write?
2. Choose the target: a GOT slot, a return address, a hook, a vtable.
3. Write the value; the next read/call to the target is controlled.
4. Verify: the redirect happens on the next use.

## Falsifier

Falsifier — the write is constrained to a bounded region or the value isn't fully controlled: only within-range targets work.

## Traps

- A stack smash writes CONTIGUOUS bytes — targets must be stack-reachable or need arb-write.
- GOT is the usual target under partial RELRO.
- A return address on the stack is always in reach of a stack smash.

## Cross-references

`fgot-overwrite.md` · `control-flow.md`
