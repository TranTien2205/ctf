# Directory listing — autoindex and open dirs

An enabled autoindex lists everything in a directory — backups, configs, uploads, test files — often the fastest way to find the artifact that matters.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /uploads/ or /files/ returns an index page | autoindex on | read every entry |
| 'Index of /' in the body | nginx/Apache autoindex | walk subdirs |
| Parent Directory link | traversable listing | walk up and sideways |
| A dir 403s on GET / but indexes on a subdir | partial exposure | probe siblings |

## Steps

1. Probe likely dirs: /uploads/ /files/ /backup/ /assets/ /static/ /tmp/ /old/.
2. Look for 'Index of', 'Parent Directory', or a structured file list.
3. Walk every listed entry — the flag file, a backup archive, a config are common.
4. Check sibling dirs the listing reveals — one open dir usually means several.

## Falsifier

Falsifier — every directory path returns the catch-all or 403 with no index body: autoindex is off. Filenames would have to be guessed, which is out of scope unless hinted.

## Traps

- A styled file manager is not autoindex — check for raw 'Index of' structure.
- Listing shows names only; you still need each file to read 200, not just exist.
- Symlinks in a listing can point outside webroot — an accidental file-read.

## Commands

```bash
for d in /uploads/ /files/ /backup/ /static/; do curl -s -o /tmp/r -w "$d %{http_code} %{size_download}\n" "$BASE$d"; done
```

## Cross-references

`backup-archives.md` · `exposed-artifacts.md`
