# Zeek: conn_state values

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Connection state letters: `SF` normal complete, `S0` attempt no reply, `REJ` rejected, `RSTR`/`RSTO`/`RSTOS0`/`RSTRH` reset variants, `S1`/`S2`/`S3` half-open/close oddities, `SH`/`SHR` SYN-only halves, `OTH` no SYN seen mid-stream, `OTH`. For exfil, `SF` with large `orig_bytes` is the clean case; `S0` floods are failed dials, not transfers.

## Evidence rule

Zeek rows are the quotable records — grep the exact line and pass it through
`post-probe --response` verbatim, `#fields` context included when the column
meaning matters.

## Pivot

conn.log answers volume/direction; protocol logs answer content; notices are
leads. A sensor with `missed_bytes` high -> host-side artifacts
(`art-srum-usage`, `art-sysmon-3`).
