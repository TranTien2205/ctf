# Framework-specific debug surfaces — operational checklist

Each framework ships a debug surface; each has its own paths, signals, and exploitation history. Match the framework from headers/errors to its checklist.

## Checklist

- [ ] Fingerprint the framework (headers, error styling, default routes).
- [ ] Run the framework's debug-path probe list.
- [ ] Extract the env/config values the debug page shows.
- [ ] For consoles (Werkzeug, Ignition): check whether the console evaluates — PIN exploits are well-documented.

## Abort conditions

- Werkzeug PIN: the console page exists but needs the PIN from the traceback — read the traceback carefully.
- Django debug pages expose settings AND the SQL query — double disclosure.
- Ignition has a historical RCE (file_get_contents) — check the version if present.

## Falsifier

Falsifier — the framework's debug paths all 404 and error pages are generic production pages: debug surface off.

## Cross-references

`debug-endpoints.md` · `error-pages.md`
