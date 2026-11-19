# Two-stage write — a write that enables a bigger write — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a bounded second input | first write extends it | the enabling write |
| a pointer written first | plants the arg for stage 2 | the setup |
| a bound/length field writable | enlarge the buffer for stage 2 | the write |

## Falsifier

Falsifier — nothing the first write could change makes the second input reach further: no composition.
