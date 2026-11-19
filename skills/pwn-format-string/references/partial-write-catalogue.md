# Partial write — %hn / %hhn for byte-level control — case catalogue

A full %n writes a qword; %hn writes 2 bytes; %hhn writes 1. Byte-wise writes let you set a large value (like an address) without printing billions of bytes for the count.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the value is large (an address) | byte-wise write | %hhn |
| 2 | only low bytes need changing | partial overwrite | %hn/%hhn |
| 3 | a 2-byte redirect | %hn | low bytes |

## Falsifier

Falsifier — the byte-precision write can't compose the needed value at the reachable positions: the write is incomplete.
