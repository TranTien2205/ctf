# PIE — the code-pointer leak


pie: true: a code pointer must leak before ANY binary address is
usable — the leak's offset from the binary base is known.

## The order

    leak a code ptr → base = ptr - known_offset → every gadget
    derives.

## The sources

- A return address on the stack (read via fmtstr or a print).
- A saved code pointer in a readable structure.
- The binary's own output of an address.
