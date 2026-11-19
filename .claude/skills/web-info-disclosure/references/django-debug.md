# Django DEBUG=True — the yellow page

Django's debug error page dumps settings values, the SQL query, request vars, and the full Python traceback — a multi-layer disclosure.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| yellow Django error page | DEBUG on | settings + query + traceback |
| settings SECRET_KEY visible | session signing key | forge sessions |
| SQL query in the error | query structure | hands to web-sqli |
| installed apps and paths | app map | route discovery |

## Steps

1. Trigger a 404 or a crash — DEBUG pages appear on both.
2. Read settings: SECRET_KEY, DATABASE_URL, INSTALLED_APPS.
3. The SQL query section shows the query that failed — sqli material.
4. SECRET_KEY → forge sessions (web-auth-session).

## Falsifier

Falsifier — generic 404/500 pages only: DEBUG is off.

## Traps

- DEBUG pages show settings VALUES — including keys Django would mask elsewhere.
- The local vars in each traceback frame carry more secrets than the settings block.
- A DEBUG=False app still leaks via custom error handlers.

## Commands

```bash
curl -s '$BASE/nonexistent-path' | grep -i django
```

## Cross-references

`framework-debug.md` · `error-pages.md`
