# Two-stage write — a write that enables a bigger write — case catalogue

A first %n can write a pointer or a bound that makes a SECOND input's write/overflow reach further — the write that enables the next primitive.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a bounded second input | first write extends it | the enabling write |
| 2 | a pointer written first | plants the arg for stage 2 | the setup |
| 3 | a bound/length field writable | enlarge the buffer for stage 2 | the write |

## Falsifier

Falsifier — nothing the first write could change makes the second input reach further: no composition.
