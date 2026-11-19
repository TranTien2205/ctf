# Partial overwrite — low-byte control without a full leak — checklist

Can't leak a full pointer? Overwrite only the low 1-2 bytes of a saved return or GOT entry — redirect to a nearby target in the same page.

## Checklist

- [ ] If the write reaches the return address but not enough for a full pointer: overwrite only the low bytes.
- [ ] The high bytes keep their original value — the redirect lands in the same 4KB/64KB region.
- [ ] Useful when ASLR makes the high bytes unknown but a nearby gadget/function shares them.
- [ ] A 1-byte overwrite reaches within 256 bytes; 2-byte within 64KB.

## Abort conditions

- The low bytes are the least ASLR'd — a 12-bit-page is deterministic.
- Same-page redirect: useful for reaching a gadget one page over.
- Works on saved return addresses and GOT entries alike.

## Falsifier

Falsifier — the low-byte-controlled target doesn't include any useful gadget/function: no partial redirect is possible.
