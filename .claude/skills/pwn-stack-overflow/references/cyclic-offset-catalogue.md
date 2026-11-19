# Offset measurement — the cyclic pattern — case catalogue

The first deliverable of every stack challenge: the exact byte offset from your input's start to the saved return address. tools/pwn_cyclic.py makes the De Bruijn pattern; a faulting register reads the offset back.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | crash with a controllable fault address | offset measurable | cyclic + fault read |
| 2 | RIP holds four pattern bytes | control proven | build the payload |
| 3 | pattern repeats but no crash at write boundary | length capped too short | not stack-smash — re-check the bound |

## Falsifier

Falsifier — the faulting register never holds pattern bytes at any length: no write reaches the saved return address. Re-check the read bound; it is probably capped below the saved-state distance.
