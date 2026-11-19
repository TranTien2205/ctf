# Spray-then-aim — the imprecise fallback


When the write can't aim precisely, fill the region with the payload so
any landing hits it: spray a data pattern across many chunks.

## Steps

1. Allocate N objects all carrying your payload pattern.
2. Free/arrange so the target region is dense with them.
3. A partially-aimed write/read lands on sprayed content.

## Limits

- Probability, not certainty — use only when no precise route exists.
- Bounded by memory caps.

## Falsifier

Precision is available — prefer it always; spray is the fallback of
last resort.
