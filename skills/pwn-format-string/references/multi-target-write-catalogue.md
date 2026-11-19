# Multi-target write — several %n in one fmtstr — case catalogue

One fmtstr can carry several %N$n writes: overwrite a GOT entry AND a return address, or write several bytes of one address via %hhn at increasing offsets.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | several addresses need writing | multi-write | several %n |
| 2 | one address needs byte-wise writes | %hhn sequence | the bytes |
| 3 | a large value via byte writes | ordered %hhn | the count deltas |

## Falsifier

Falsifier — the argument positions or the count arithmetic can't produce all needed writes in one call: split across calls if re-triggerable.
