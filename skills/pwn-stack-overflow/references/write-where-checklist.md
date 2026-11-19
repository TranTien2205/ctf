# Write-what-where — the primitive that builds everything — checklist

A controlled write to a controlled address is the universal exploit primitive: GOT entries, return addresses, hooks all become targets.

## Checklist

- [ ] Identify the write primitive: overflow? format-string %n? array-index write?
- [ ] Choose the target: a GOT slot, a return address, a hook, a vtable.
- [ ] Write the value; the next read/call to the target is controlled.
- [ ] Verify: the redirect happens on the next use.

## Abort conditions

- A stack smash writes CONTIGUOUS bytes — targets must be stack-reachable or need arb-write.
- GOT is the usual target under partial RELRO.
- A return address on the stack is always in reach of a stack smash.

## Falsifier

Falsifier — the write is constrained to a bounded region or the value isn't fully controlled: only within-range targets work.
