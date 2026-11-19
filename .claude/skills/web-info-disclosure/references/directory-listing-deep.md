# Directory listing — autoindex and open dirs — deep

An enabled autoindex lists everything in a directory — backups, configs, uploads, test files — often the fastest way to find the artifact that matters.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — every directory path returns the catch-all or 403 with no index body: autoindex is off. Filenames would have to be guessed, which is out of scope unless hinted.

## Highest-cost traps

- A styled file manager is not autoindex — check for raw 'Index of' structure.
- Listing shows names only; you still need each file to read 200, not just exist.
- Symlinks in a listing can point outside webroot — an accidental file-read.

## Commands

```bash
for d in /uploads/ /files/ /backup/ /static/; do curl -s -o /tmp/r -w "$d %{http_code} %{size_download}\n" "$BASE$d"; done
```

## Cross-references

`backup-archives.md` · `exposed-artifacts.md`
