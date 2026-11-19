# The count field — %c and field-width to set %n's value — case catalogue

%n writes 'bytes printed so far'. The %Nc specifier and field-width control that count: %999c prints 999 bytes, so %n writes 999.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | the write value is the byte count | count via width | %Nc |
| 2 | %999c before %n | count = 999 | the value |
| 3 | field-width %9999d | also counts | the value |

## Falsifier

Falsifier — the count can't reach the needed value in one call (a huge address byte): use %hhn byte-wise or a different write target.
