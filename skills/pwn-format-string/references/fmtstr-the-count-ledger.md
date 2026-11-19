# The count ledger — tracking the byte count by hand


Building a multi-write payload by hand: keep a running ledger — the
count after each specifier, and what each %n writes.

## Example ledger — write 0x08049182 via 4 %hhn

| step | specifier | count | writes |
|---|---|---|---|
| 1 | %0x42c | 0x42 | |
| 2 | %7$hhn | 0x42 | 0x42 to byte0 |
| 3 | %0x41c | 0x83 | |
| 4 | %8$hhn | 0x83 | 0x83 to byte1 |
| 5 | %0xc0c | 0x143 | |
| 6 | %9$hhn | 0x143 | 0x43 to byte2 |
| 7 | %0xc1c | 0x204 | |
| 8 | %10$hhn | 0x204 | 0x04 to byte3 |

The bytes land little-endian per slot — plan which arg writes which
byte.
