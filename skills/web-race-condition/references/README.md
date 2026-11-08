# Race condition reference map

This is the canonical reference entry for `web-race-condition`. Open it after
the first interleaving probe, then choose one named file. Do not use
deserialization material as the race-condition depth reference.

| Signal or task | Next material |
|---|---|
| Read/write gap and two requests can overlap | `interleaved-writes.md` |
| Token/limit/redeem window | `interleaved-writes.md` — the check-then-act alphabet |
| No attributable before/after state change | stop and record inconclusive; do not flood |

`interleaved-writes.md` was distilled from the confirmed field notes in
`../field-notes.md`.
