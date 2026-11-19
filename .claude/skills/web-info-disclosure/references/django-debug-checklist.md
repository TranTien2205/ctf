# Django DEBUG=True — the yellow page — checklist

Django's debug error page dumps settings values, the SQL query, request vars, and the full Python traceback — a multi-layer disclosure.

## Checklist

- [ ] Trigger a 404 or a crash — DEBUG pages appear on both.
- [ ] Read settings: SECRET_KEY, DATABASE_URL, INSTALLED_APPS.
- [ ] The SQL query section shows the query that failed — sqli material.
- [ ] SECRET_KEY → forge sessions (web-auth-session).

## Abort conditions

- DEBUG pages show settings VALUES — including keys Django would mask elsewhere.
- The local vars in each traceback frame carry more secrets than the settings block.
- A DEBUG=False app still leaks via custom error handlers.

## Falsifier

Falsifier — generic 404/500 pages only: DEBUG is off.
