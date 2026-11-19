# Leaking the binary base — the PIE de-randomization


Under PIE the binary's addresses are base+offset — one leaked code
pointer recovers the base.

## Steps

1. Scan the %p dump for a 0x55..(x86-64 PIE) or module-range pointer.
2. Subtract its known offset (the symbol it points at — usually a return
   addr into a known function, or a GOT/PLT entry).
3. base = leaked - offset. All binary addresses now computable.

## Identifying which pointer

- A saved return address points into the calling function — known
  offset from disassembly.
- A GOT slot pointer = base + got_offset — from readelf -r.
- A string pointer into .rodata = base + rodata_offset.

## Verify

    r2 -A ./chal ; pdf @ main    # find the ret-addr offset
    readelf -r ./chal            # GOT offsets

## Falsifier

No module-range pointer leaks: base unknowable — only absolute (non-PIE)
targets reachable.
