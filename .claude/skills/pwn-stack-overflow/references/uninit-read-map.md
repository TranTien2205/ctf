# Uninitialized read as a leak primitive — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| read returns more than was written | stale bytes leak | a pointer/canary |
| a struct with padding returned raw | padding bytes leak | a pointer |
| a partially-filled buffer dumped | the tail holds stale data | the leak |

## Falsifier

Falsifier — the buffer is fully written before being read: no stale bytes; no leak.
