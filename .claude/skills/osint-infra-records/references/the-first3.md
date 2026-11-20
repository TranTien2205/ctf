# The first three queries — always

1. `--type TXT` — the flag's home.
2. `--type ANY` — the sweep.
3. `--crtsh` — the SAN siblings.
Those three cover most CTF infra-record answers before whois and
AXFR are even needed.

## Why this order

TXT carries a planted flag; ANY is a fast sweep; crt.sh names the
siblings — the three highest-signal queries up front. Everything
else (whois, AXFR, passive) deepens a lead those three opened.

## Why three

TXT (flag), ANY (sweep), crtsh (siblings) — the highest-signal coverage in three commands.
