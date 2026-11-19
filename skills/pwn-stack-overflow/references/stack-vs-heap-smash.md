# Stack smash vs heap metadata — the ownership boundary

Both are 'write past a buffer'; which class owns it depends on WHERE the corruption lands: stack frames belong here, heap chunk metadata belongs to pwn-heap-corruption.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the write reaches saved regs/RIP | stack corruption | this class |
| the write reaches chunk fd/bk/size | heap corruption | pwn-heap-corruption |
| the buffer is malloc'd | likely heap class | check where corruption lands |

## Steps

1. Identify the buffer's allocation: local array (stack) vs malloc (heap).
2. A stack-local buffer's overflow reaches the saved frame — this class.
3. A malloc'd buffer's overflow reaches the next chunk's metadata — heap class.
4. The cyclic/fault test works for both; the LANDING site names the class.

## Falsifier

Falsifier — the corruption demonstrably lands in heap metadata (a chunk header), not the stack frame: route to pwn-heap-corruption.

## Traps

- Same primitive, different target — the cyclic test doesn't distinguish; the fault does.
- A malloc'd buffer can still be adjacent to stack-relevant data only in exotic layouts.
- The owning class decides which skill's chains apply.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>   # is the buffer local or malloc'd?
```

## Cross-references

`class-boundary.md` · `unsorted-bin-fd.md`
