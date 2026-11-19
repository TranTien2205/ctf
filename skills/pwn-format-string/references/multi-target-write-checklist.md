# Multi-target write — several %n in one fmtstr — checklist

One fmtstr can carry several %N$n writes: overwrite a GOT entry AND a return address, or write several bytes of one address via %hhn at increasing offsets.

## Checklist

- [ ] Plan the writes: which addresses, which values.
- [ ] For byte-wise: %hhn writes count&0xff — set the count's low byte per write.
- [ ] Order the writes so the cumulative count produces the right low bytes.
- [ ] Each %N$n consumes an argument position — count them.

## Abort conditions

- The cumulative count is shared across all writes in one call.
- Order %hhn writes so increasing counts produce the right bytes.
- A one-shot service needs ALL writes in one call — plan the deltas.

## Falsifier

Falsifier — the argument positions or the count arithmetic can't produce all needed writes in one call: split across calls if re-triggerable.
