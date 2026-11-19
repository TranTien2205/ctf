# The count field — %c and field-width to set %n's value — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the write value is the byte count | count via width | %Nc |
| %999c before %n | count = 999 | the value |
| field-width %9999d | also counts | the value |

## Falsifier

Falsifier — the count can't reach the needed value in one call (a huge address byte): use %hhn byte-wise or a different write target.
