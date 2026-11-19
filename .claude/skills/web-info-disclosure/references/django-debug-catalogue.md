# Django DEBUG=True — the yellow page — case catalogue

Django's debug error page dumps settings values, the SQL query, request vars, and the full Python traceback — a multi-layer disclosure.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | yellow Django error page | DEBUG on | settings + query + traceback |
| 2 | settings SECRET_KEY visible | session signing key | forge sessions |
| 3 | SQL query in the error | query structure | hands to web-sqli |
| 4 | installed apps and paths | app map | route discovery |

## Falsifier

Falsifier — generic 404/500 pages only: DEBUG is off.
