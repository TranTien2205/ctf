# Framework-specific debug surfaces — deep

Each framework ships a debug surface; each has its own paths, signals, and exploitation history. Match the framework from headers/errors to its checklist.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the framework's debug paths all 404 and error pages are generic production pages: debug surface off.

## Highest-cost traps

- Werkzeug PIN: the console page exists but needs the PIN from the traceback — read the traceback carefully.
- Django debug pages expose settings AND the SQL query — double disclosure.
- Ignition has a historical RCE (file_get_contents) — check the version if present.

## Commands

```bash
for p in /console /__debug__/ /_profiler /telescope /rails/info/routes; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`debug-endpoints.md` · `error-pages.md`
