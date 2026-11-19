# The count field — %c and field-width to set %n's value

%n writes 'bytes printed so far'. The %Nc specifier and field-width control that count: %999c prints 999 bytes, so %n writes 999.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the write value is the byte count | count via width | %Nc |
| %999c before %n | count = 999 | the value |
| field-width %9999d | also counts | the value |

## Steps

1. %Nc prints N chars (one char of arg, padded) — sets the count to N.
2. %Nd with a width of N prints N chars — same effect.
3. After %Nc, the count is ~N → %n writes N.
4. For byte-wise writes, the count's LOW byte is what %hhn writes.

## Falsifier

Falsifier — the count can't reach the needed value in one call (a huge address byte): use %hhn byte-wise or a different write target.

## Traps

- %Nc counts as N printed bytes even though only 1 arg char is shown.
- The count is cumulative across all printed output in the call.
- %hhn writes count&0xff — the low byte is what matters.

## Cross-references

`arb-write-via-n.md` · `partial-write.md`
