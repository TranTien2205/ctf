# Partial overwrite — low-byte control without a full leak

Can't leak a full pointer? Overwrite only the low 1-2 bytes of a saved return or GOT entry — redirect to a nearby target in the same page.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| only a few bytes controllable past the bound | low-byte redirect | partial write |
| the target shares the high bytes | same page | low bytes only |
| a 2-byte overwrite reaches a nearby function | same-page redirect | the trick |

## Steps

1. If the write reaches the return address but not enough for a full pointer: overwrite only the low bytes.
2. The high bytes keep their original value — the redirect lands in the same 4KB/64KB region.
3. Useful when ASLR makes the high bytes unknown but a nearby gadget/function shares them.
4. A 1-byte overwrite reaches within 256 bytes; 2-byte within 64KB.

## Falsifier

Falsifier — the low-byte-controlled target doesn't include any useful gadget/function: no partial redirect is possible.

## Traps

- The low bytes are the least ASLR'd — a 12-bit-page is deterministic.
- Same-page redirect: useful for reaching a gadget one page over.
- Works on saved return addresses and GOT entries alike.

## Cross-references

`pie-leak.md` · `fgot-overwrite.md`
