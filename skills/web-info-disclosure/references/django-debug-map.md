# Django DEBUG=True — the yellow page — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| yellow Django error page | DEBUG on | settings + query + traceback |
| settings SECRET_KEY visible | session signing key | forge sessions |
| SQL query in the error | query structure | hands to web-sqli |
| installed apps and paths | app map | route discovery |

## Falsifier

Falsifier — generic 404/500 pages only: DEBUG is off.
