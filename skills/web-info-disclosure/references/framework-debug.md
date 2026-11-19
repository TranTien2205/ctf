# Framework-specific debug surfaces

Each framework ships a debug surface; each has its own paths, signals, and exploitation history. Match the framework from headers/errors to its checklist.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Werkzeug 'DEBUG MODE' banner | Flask debug console | /console PIN exploit |
| Django yellow error page | DEBUG=True | settings values, SQL in trace |
| Laravel Ignition/Whoops | debug on | env vars in error page |
| Rails /rails/info/routes or console | dev endpoints | route map |
| Next.js /_next/data or dev errors | dev overlay | route data |
| Spring Whitelabel error page | Spring stack | actuator family |

## Steps

1. Fingerprint the framework (headers, error styling, default routes).
2. Run the framework's debug-path probe list.
3. Extract the env/config values the debug page shows.
4. For consoles (Werkzeug, Ignition): check whether the console evaluates — PIN exploits are well-documented.

## Falsifier

Falsifier — the framework's debug paths all 404 and error pages are generic production pages: debug surface off.

## Traps

- Werkzeug PIN: the console page exists but needs the PIN from the traceback — read the traceback carefully.
- Django debug pages expose settings AND the SQL query — double disclosure.
- Ignition has a historical RCE (file_get_contents) — check the version if present.

## Commands

```bash
for p in /console /__debug__/ /_profiler /telescope /rails/info/routes; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`debug-endpoints.md` · `error-pages.md`
