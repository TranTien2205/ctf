# Per-read bound — the effective length each call allows


Each read's EFFECTIVE bound decides whether the smash reaches saved
state: n from a length-field, n from an input, n hardcoded.

| Read source | Effective bound |
|---|---|
| `read(0,buf,N)` fixed N | N — is N > buffer size? |
| `read(0,buf,n)` n=input | attacker — set huge |
| `fgets(buf,N)` | N-1 chars |
| `scanf %s` | unbounded (no bound arg) |
| `gets` | unbounded |
| `memcpy(d,s,n)` | n — is n influenced? |

The bound vs the buffer-size gap is the overwrite distance.
