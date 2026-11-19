# Static leftovers — OS and editor artifacts — deep

.DS_Store, Thumbs.db, .swp files, node_modules paths, editor temp files: small artifacts that map the directory's real contents.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — no leftover artifacts serve: the channel is closed.

## Highest-cost traps

- .DS_Store is binary — needs a parser, not a text read.
- swp may hold a DIFFERENT version than the live file — note the discrepancy.

## Commands

```bash
for p in /.DS_Store /.index.php.swp /Thumbs.db; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`backup-archives.md` · `source-disclosure.md`
