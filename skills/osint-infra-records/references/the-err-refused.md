# Error — refused/timeout

A refused query or timeout — try a different resolver (`--server`
8.8.8.8 or the authoritative NS), a different type, or TCP; a
refusal isn't absence.

## The causes

- The resolver rate-limited you — retry against the authoritative.
- A filtered type (ANY) — query the specific type.
- UDP blocked — force TCP.
- A genuinely missing name — distinguish from a transport failure.

## NODATA vs failure

A refused/timeout is a transport problem; an empty answer (NODATA) is a real negative — the host exists, that type does not.
