# Backup and archive exposure — deep

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.

## Highest-cost traps

- A huge archive may be a zip bomb or decoy — list before extracting, extract to a bounded dir.
- SQL dumps can be GBs — grep, don't open.
- The archive may 403 while directory listing shows it — combine with directory-listing.

## Commands

```bash
for p in /backup.zip /app.zip /db.sql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `directory-listing.md` · `source-disclosure.md`
