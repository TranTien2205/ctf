# red-island-2 (WAF SQLi) — SOLVED (no writeup: source-on-homepage only)

- Platform: HTB-style web, blackbox with source shown on `/`
- Date: 2026-09-07
- Flag: `HTB{REDACTED}` (HEX-verified against DB row)
- Artifacts: `~/ctf/challenges/red-island-2/{source.php, blindi.py, flag.txt}`
- Solved WITHOUT writeup — the first full no-writeup solve in this toolkit.
  Writeup search was attempted ("Red Island" noise only) and contributed nothing.

## Chain

1. Source on homepage: POST body -> `waf()` -> `json_decode()` -> vsprintf into
   `SELECT note FROM notes WHERE assignee = '%s'`.
2. WAF (on RAW body): chars `*(<=>|'&-@` + words `select,and,or,if,by,from,
   where,as,is,in,not,having` (case-insensitive substring).
3. **Core trick**: WAF scans BEFORE `json_decode` -> every blocked char/word
   passes as `\uXXXX` (`\u0027`=`'`, `\u0073elect`=`select`). Escape EVERY char
   of the payload (alnum too) — words hide inside letters ("database" contains
   "as", "substring" contains "in").
4. No echo channel (200 empty always) -> time-based oracle:
   `' OR IF((cond),SLEEP(n),0) #`. Confirmed: SLEEP(3) -> 3.77s vs 0.73s baseline.
5. Blind extraction (ASCII binary search, ~7 probes/char):
   tables -> `definitely_not_a_flag,notes`; columns -> `flag`; flag value.

## Oracle-reliability traps (each cost a corrupted run)

- **GROUP_CONCAT needs ORDER BY** — row order is nondeterministic across queries;
  unordered extraction mixed two table names into garbage.
- **Parallel SLEEP probes corrupt the oracle** (FPM contention/queuing) —
  extract SEQUENTIALLY; parallelism only across positions with stable server.
- Note rowcount: `IF(...,SLEEP..)` in WHERE sleeps **per matching row** —
  probe cost = sleep × rowcount (here 1 row).
- Baseline jitter (0.73–1.06s) vs SLEEP(1.5): threshold 1.25 too close -> raised
  to SLEEP=1.2/THRESHOLD=1.5 after measuring; always measure baseline first.
- End-of-string reads as space (binary search floors at 32): verify with
  `ORD(SUBSTRING(q,pos,1)) > 0` before appending space / stopping.
- HEX verify: compare string-vs-string `HEX(x) = '<hex>'`, NOT `= 0x<hex>`
  (type mismatch silently returns false).

## Reusable

- JSON `\uXXXX` WAF bypass applies to ANY filter that scans raw body before
  decode (PHP json_decode, JS JSON.parse flows).
- blindi.py is now a generic time-based blind-SQLi extractor
  (oracle/bs_num/extract) reusable on any injectable point + timing oracle.
