# Framework-specific debug surfaces — case catalogue

Each framework ships a debug surface; each has its own paths, signals, and exploitation history. Match the framework from headers/errors to its checklist.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Werkzeug 'DEBUG MODE' banner | Flask debug console | /console PIN exploit |
| 2 | Django yellow error page | DEBUG=True | settings values, SQL in trace |
| 3 | Laravel Ignition/Whoops | debug on | env vars in error page |
| 4 | Rails /rails/info/routes or console | dev endpoints | route map |
| 5 | Next.js /_next/data or dev errors | dev overlay | route data |
| 6 | Spring Whitelabel error page | Spring stack | actuator family |

## Falsifier

Falsifier — the framework's debug paths all 404 and error pages are generic production pages: debug surface off.

## Coverage notes

- Werkzeug PIN: the console page exists but needs the PIN from the traceback — read the traceback carefully.
- Django debug pages expose settings AND the SQL query — double disclosure.
- Ignition has a historical RCE (file_get_contents) — check the version if present.

## Cross-references

`debug-endpoints.md` · `error-pages.md`
