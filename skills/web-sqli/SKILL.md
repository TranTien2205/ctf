---
name: web-sqli
description: >
  SQL injection depth skill: detection, DBMS fingerprint, extraction. Use when a
  request value reaches a datastore query — an SQL error, a login anomaly, a
  boolean or timing delta, or a UNION opportunity. NoSQL/operator injection has
  its own class and skill: use web-nosqli when the value remains an object.
tags: [web, sqli, injection, database, auth-bypass]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same injection point: 3 payloads, no new signal"
    - "WAF block confirmed after 2 bypass attempts"
evidence_level: verified
---

# SQL Injection — Canonical Depth Skill

**Verified here.** Chains that prove this class: `htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli`, `htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli`.


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

For blind SQLi, do not hand-infer a bit from a remembered payload. Establish a
baseline, run a matched true/false pair (or a measured timing oracle), and
preserve the actual responses. A scanner such as `sqlmap` is an optional
authorized-target adapter; its summary is not evidence unless the underlying
request/response or extracted value is recorded. For second-order SQLi, trigger
the deferred consumer and inspect its output before applying the falsifier.

## Do not confuse SQLi with NoSQLi

When the body is JSON and the query takes an object, the injection is a shape,
not a string. Route to `../web-nosqli/SKILL.md` rather than forcing SQL syntax.
That skill contains the read-safe probe and the write blast-radius warning.

**Falsifier for immediate sinks:** the matched true and false forms produce the
same validated result. For stored/deferred sinks, this is not a falsifier until
the consuming job, page, report, or worker has run and its output has been read.

## Route to depth

If the needed reference is not obvious, open `references/README.md` and choose
one named file. Do not load the entire directory.

| Observation | File |
|---|---|
| A database error is shown | `references/error-based.md` plus the DBMS file |
| True and false responses differ | `references/boolean-blind.md` |
| Only timing answers | `references/time-blind.md` |
| Files must be read or written | `references/file-operations.md` |
| A filter blocks the payload | `references/waf-evasion.md` |
| The value is stored, then consumed by a later job/page | `references/extended-corpus.md` — Second-Order SQL Injection |
| A client-controlled sort/key expression reaches `ORDER BY` | `references/extended-corpus.md` — ExpressionEngine ORDER BY SQLi |
| Object-shaped filter, comparison operators | `../web-nosqli/SKILL.md` and its references |
| DBMS identified | `references/mysql.md`, `references/postgresql.md`, `references/mssql.md`, `references/oracle.md` |
| Still unsure | `references/detection.md` |

For an immediate sort/column signal, use `references/detection.md` for the
bounded `ORDER BY N` column-count probe before trying UNION. Do not use response
size alone to search for sort keys: compare ordering or a query-derived marker.

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

When the local references below lack the specific bypass, open one named file
from the extended corpus:
`references/extended-corpus.md`.

The extended corpus is supplementary knowledge, not a second routing skill. Do
not open the whole `skills/ctf-web/` directory. Start with the local reference
matching the observed channel, then open the extended SQLi file only for a
named variant or challenge pattern it explicitly covers.

## Discipline

- Confirm the primitive before exfiltrating. One injection point, cheapest probe
  first.
- Three payloads at one point with no change in signal means a filter or the
  wrong point. Change layer rather than adding payloads. See
  `../LOOP_DISCIPLINE.md`.
- Timing oracles: measure the baseline first, keep probes sequential, and
  remember a conditional sleep costs one sleep per matching row.

## Operational probe

One syntax marker, then a matched true/false pair against the *same* input. A
single error page is surface evidence and cannot confirm the class:

```bash
for v in "1' AND '1'='1" "1' AND '1'='2"; do
  python3 tools/web/http_probe.py --challenge "$C" --class web-sqli \
    --url "$BASE/item?id=$(printf %s "$v" | jq -sRr @uri)" \
    --evidence-regex 'syntax error|unterminated|SQLSTATE' \
    --evidence-kind class --on-match confirms --on-miss inconclusive
done
```

The signal is a *difference* between the two, not the presence of an error.

**Falsifier:** an immediate sink returns the identical validated response for both
forms; a stored or deferred sink shows the same output on the later read.

Pipe the result straight into the write gate: `http_probe.py` already emits the
shape `tools/hooks.py post-probe` wants, so the excerpt is verbatim and a
transport failure is recorded as `transport`, which can never confirm.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
