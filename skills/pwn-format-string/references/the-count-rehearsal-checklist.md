# Rehearsing the count — dry-running the arithmetic — checklist

Companion to `the-count-rehearsal.md`.

## Checklist

- [ ] 1. List the target bytes low→high.
- [ ] 2. Assign a printed-count to each %hhn so count&0xff = the byte.
- [ ] 3. Order specifiers so the running count hits each needed low byte.
- [ ] 4. Between writes, pad with %c/%% to reach the next byte's count.
