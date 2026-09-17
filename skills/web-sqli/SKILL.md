---
name: web-sqli
description: >
  SQL and NoSQL injection: detection, DBMS fingerprint, extraction. Use when a
  request value reaches a datastore query — an SQL error, a login anomaly, a
  boolean or timing delta, a UNION opportunity, or an object-shaped filter
  accepted from a JSON body. Routes to references/ per DBMS and technique.
tags: [web, sqli, nosqli, injection, database, auth-bypass]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same injection point: 3 payloads, no new signal"
    - "WAF block confirmed after 2 bypass attempts"
---

# SQL / NoSQL Injection — Depth Skill

## Confirm the primitive before extracting anything

Take a baseline, then compare: `id=1`, `id=1'`, `id=1 AND 1=1`, `id=1 AND 1=2`.

| Observation | Channel |
|---|---|
| A database error appears | error-based |
| True and false responses differ | boolean-blind |
| Response time varies with the payload | time-blind |
| A column is reflected into the page | UNION |

First probes:

```text
error    1'
boolean  ' AND 1=1-- -    vs    ' AND 1=2-- -
time     MySQL ' AND SLEEP(5)-- -  |  PostgreSQL ' AND pg_sleep(5)-- -
         MSSQL '; WAITFOR DELAY '0:0:5'-- -
union    ' ORDER BY N-- -  raising N until it errors, then ' UNION SELECT NULL,...-- -
```

Login bypass is worth trying first when the sink is an authentication query:
`' OR '1'='1'-- -`, `admin'-- -`, `admin'#`, `') OR ('1'='1`.

## NoSQL

When the body is JSON and the query takes an object, the injection is a shape,
not a string. Confirm with a **read-safe** probe: send the filter pinned to an
object you created, with every write field omitted, and read what comes back.
Only then test comparison or update operators. A broad filter combined with write
fields rewrites the whole collection — see `references/nosql.md`.

## Route to depth

| Observation | File |
|---|---|
| A database error is shown | `references/error-based.md` plus the DBMS file |
| True and false responses differ | `references/boolean-blind.md` |
| Only timing answers | `references/time-blind.md` |
| Files must be read or written | `references/file-operations.md` |
| A filter blocks the payload | `references/waf-evasion.md` |
| Object-shaped filter, comparison operators | `references/nosql.md` |
| DBMS identified | `references/mysql.md`, `postgresql.md`, `mssql.md`, `oracle.md` |
| Still unsure | `references/detection.md` |

Fingerprint once: MySQL `@@version`, PostgreSQL `version()`, MSSQL `@@version`,
Oracle `v$version`. Then read only that DBMS file.

## Extraction order

Database names, then tables from the information schema, then columns, then the
target rows, then any file or out-of-band channel.

Blind extraction: binary-search the character code, roughly seven probes per
character. A linear scan over the charset is an order of magnitude slower and
will time out. Order any grouped output explicitly, or rows arrive differently
between queries and corrupt the result. Verify the final value with a hex
comparison against the row, as string to string.

## Variants and bypasses

When this file lacks the specific bypass, open one named file:
`../ctf-web/sql-injection.md`.

## Discipline

- Confirm the primitive before exfiltrating. One injection point, cheapest probe
  first.
- Three payloads at one point with no change in signal means a filter or the
  wrong point. Change layer rather than adding payloads. See
  `../LOOP_DISCIPLINE.md`.
- Timing oracles: measure the baseline first, keep probes sequential, and
  remember a conditional sleep costs one sleep per matching row.
