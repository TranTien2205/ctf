# Is batching allowed? — probe first

Send two answers at once on round 1 — if the server accepts them,
pipeline; if it reads line-at-a-time and discards extras, batching
desyncs. Probe before building it.

## Probe

Two answers on round 1 — accepted means pipeline.
