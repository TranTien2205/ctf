# Symlink & Hardlink Upload — the file that points elsewhere

## The archive-symlink shape — a zip/tar carrying a link entry

A zip entry flagged `LNK`/a tar `LNKTYPE`/`SYMTYPE` — extract creates a
symlink, not a regular file:

```
tar:
  symlinked.txt → /etc/passwd   (type SYMTYPE, linkname=/etc/passwd)
zip:
  entry with unix attrs 0o120000 (S_IFLNK) → extractor honors it
```

`archive_gen` builds the slip shapes; symlink entries are the deeper
variant — the extractor honors `linkname` over filename.

## What a symlink buys — three primitives

| Landing | Effect |
|---|---|
| into the webroot → `GET /link` | serves the TARGET file — file-read primitive (`/link`→`/etc/passwd`) |
| into an include path | `include('link')` reads the target — file-read → RCE |
| over an existing file's name | write to `link` writes to TARGET — arbitrary overwrite |

## The "follow_symlinks" config question — who honors it

- `tar -x`/`unzip` with `--no-overwrite-dir`/`-K` — different defaults
- python `tarfile.extract`/`zipfile` — `zipfile` doesn't extract symlinks
  by default (stores as data); `tarfile` honors them unless filtered
- nginx/apache `follow_symlinks`/`Options FollowSymLinks` — the SERVE side
  must follow the link for the file-read primitive
- `disable_symlinks`/`Options -FollowSymLinks` → 403 on the link — dead

## The `phar://` symlink path — php-specific

`phar://` meta-data/`link` entries — `phar-format-deep.md`. PHP's
`phar` stream wrapper follows links inside a phar — a symlinked file
inside a phar reaches the target.

## The "upload a file that's a symlink" without archive — raw filesystem

If the storage layer is NFS/FUSE/a local fs and the upload handler calls
`rename`/`link`/`symlink` on the file — the file may land as a link. Rare
in HTTP uploads (multipart doesn't carry link metadata) — the archive
route is the standard carrier.

## The "symlink an existing protected file into a writable dir" — the
overwrite-side use

`ln -s /app/config.php /uploads/x` → `x` is a link to `config.php`; any
write to `x` edits `config.php` — `file-overwrite.md`'s indirect write.

## Detection — does the extractor honor links?

- upload a tar/zip with a SYMTYPE entry → check if the extracted file is
  a link (`file`/`ls -la` on the landing dir — white-box)
- `GET /uploads/link` serves the target's content — file-read confirmed
- `stat`/`readlink` on the landed file — white-box check

## The `dereference` trap — `zipfile.extractall` flattening

python `zipfile` extracts entries as regular files — a "symlink" entry
inside a zip just becomes a file whose CONTENT is the link target string
— not a real link. The exploit needs an extractor that honors the flag —
`tarfile`/`unzip` do, `zipfile` doesn't.

## Falsifiers

- the extractor is `zipfile`-like (ignores link flag)
- `FollowSymLinks` off on the serve path AND no include-write path
- no extraction step exists

## Output to record

- the extractor's link handling + whether the served path follows links
