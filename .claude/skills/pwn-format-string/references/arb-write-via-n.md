# Arbitrary write via %n — the count write

%n writes 'the number of bytes printed so far' to a pointer argument. Control the count with %c/field-width and you write an arbitrary value to an arbitrary address — the write primitive.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a pointer you control lands as a %N$n arg | the write target | arbitrary write |
| a target address to overwrite | plant it | %n writes there |
| the count via %c/width | the value written | controlled |

## Steps

1. Plant the target address as a %N$n argument.
2. Send %Nc.%N$n — the %Nc prints N bytes (setting the count), then %n writes that count to *ptr.
3. The value written is the cumulative byte count — build it with %c and field width.
4. For a large value use %hn/%hhn to write partial bytes at controlled offsets.

## Falsifier

Falsifier — you can't plant a pointer at a %N$n position, or the write count can't reach the needed value: no controlled write.

## Traps

- %n writes the CUMULATIVE count — all printed bytes before it count.
- %hhn writes 1 byte, %hn 2, %n 8 — choose by the target's width.
- The count must be a small positive number — use %hhn for byte-wise.

## Cross-references

`got-overwrite-fmt.md` · `multi-target-write.md`
