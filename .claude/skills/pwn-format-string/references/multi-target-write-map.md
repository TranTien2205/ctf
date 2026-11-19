# Multi-target write — several %n in one fmtstr — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| several addresses need writing | multi-write | several %n |
| one address needs byte-wise writes | %hhn sequence | the bytes |
| a large value via byte writes | ordered %hhn | the count deltas |

## Falsifier

Falsifier — the argument positions or the count arithmetic can't produce all needed writes in one call: split across calls if re-triggerable.
