# Directory listing — autoindex and open dirs — case catalogue

An enabled autoindex lists everything in a directory — backups, configs, uploads, test files — often the fastest way to find the artifact that matters.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /uploads/ or /files/ returns an index page | autoindex on | read every entry |
| 2 | 'Index of /' in the body | nginx/Apache autoindex | walk subdirs |
| 3 | Parent Directory link | traversable listing | walk up and sideways |
| 4 | A dir 403s on GET / but indexes on a subdir | partial exposure | probe siblings |

## Falsifier

Falsifier — every directory path returns the catch-all or 403 with no index body: autoindex is off. Filenames would have to be guessed, which is out of scope unless hinted.

## Coverage notes

- A styled file manager is not autoindex — check for raw 'Index of' structure.
- Listing shows names only; you still need each file to read 200, not just exist.
- Symlinks in a listing can point outside webroot — an accidental file-read.

## Cross-references

`backup-archives.md` · `exposed-artifacts.md`
