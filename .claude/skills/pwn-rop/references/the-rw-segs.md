# The RW segments — the writable map


    readelf -l ./chal | grep RW

The writable segments: .data+.bss (and GOT if partial RELRO) — the
plant/write surface.
