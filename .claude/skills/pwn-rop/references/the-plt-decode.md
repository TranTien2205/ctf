# Decoding the PLT — the stub walk


The PLT's stubs:

    plt[0]:  push [got+8]; jmp [got+16]   # the resolver
    plt[x]:  jmp [got[x]]; push idx; jmp plt[0]

Each function's stub is `jmp [got_slot]` — ret2plt decodes the `ff 25`
stub to find which GOT slot it references.

## The find

    r2 -A ./chal ; pdf @ sym.imp.puts
    readelf -r ./chal | grep puts    # the GOT slot
