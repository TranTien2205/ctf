# Directory listing — autoindex and open dirs — operational checklist

An enabled autoindex lists everything in a directory — backups, configs, uploads, test files — often the fastest way to find the artifact that matters.

## Checklist

- [ ] Probe likely dirs: /uploads/ /files/ /backup/ /assets/ /static/ /tmp/ /old/.
- [ ] Look for 'Index of', 'Parent Directory', or a structured file list.
- [ ] Walk every listed entry — the flag file, a backup archive, a config are common.
- [ ] Check sibling dirs the listing reveals — one open dir usually means several.

## Abort conditions

- A styled file manager is not autoindex — check for raw 'Index of' structure.
- Listing shows names only; you still need each file to read 200, not just exist.
- Symlinks in a listing can point outside webroot — an accidental file-read.

## Falsifier

Falsifier — every directory path returns the catch-all or 403 with no index body: autoindex is off. Filenames would have to be guessed, which is out of scope unless hinted.

## Cross-references

`backup-archives.md` · `exposed-artifacts.md`
