# Multi-target write — several %n in one fmtstr

One fmtstr can carry several %N$n writes: overwrite a GOT entry AND a return address, or write several bytes of one address via %hhn at increasing offsets.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| several addresses need writing | multi-write | several %n |
| one address needs byte-wise writes | %hhn sequence | the bytes |
| a large value via byte writes | ordered %hhn | the count deltas |

## Steps

1. Plan the writes: which addresses, which values.
2. For byte-wise: %hhn writes count&0xff — set the count's low byte per write.
3. Order the writes so the cumulative count produces the right low bytes.
4. Each %N$n consumes an argument position — count them.

## Falsifier

Falsifier — the argument positions or the count arithmetic can't produce all needed writes in one call: split across calls if re-triggerable.

## Traps

- The cumulative count is shared across all writes in one call.
- Order %hhn writes so increasing counts produce the right bytes.
- A one-shot service needs ALL writes in one call — plan the deltas.

## Cross-references

`partial-write.md` · `arb-write-via-n.md`
