# Mixed write widths — combining %hhn + %hn + %n


Different slots need different widths: GOT byte-wise %hhn, a 2-byte flag
via %hn, a full counter via %n — mix them in one call, each consuming
its position.

## Steps

1. Each %N$hhn/%hn/%n consumes its arg position and writes count&width.
2. Mix widths per target; order by the count each needs.
3. The count is shared — plan the cumulative sequence.

## Falsifier

The needed widths can't compose in one count sequence: split across
calls.
