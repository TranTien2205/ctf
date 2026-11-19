# Dynamic vs static — which decode applies

## Static wins when

- The dispatch table is fixed in the binary.
- The program array is a static buffer.
- The decode is deterministic from the bytes.

## Dynamic wins when

- The table/program is runtime-generated.
- Self-modifying code mutates the stream.
- The program is too long to hand-decode — trace it.

## The hybrid

Static-recover the table, trace the program — the table names the
ops, the trace shows the order.
