# Backup/Restore Upload — the "import config" primitive

## The shape — upload a backup, the app restores it

Endpoints like `restore`, `import config`, `upload backup`, `restore
database`, `import project` — the file isn't served, it's read and
applied. Two bug classes inside:

1. the archive extracts with traversal → write anywhere
2. the "config" format itself carries exec directives

## `.tar`/`.zip` config bundles — traversal in the restore path

A "backup" is often a zip/tar of config files — restore extracts it:

- traversal entries land outside the restore dir — `archive-attacks.md`
- the extractor may use the entry name verbatim — `zip-format-deep.md`
- a `.gitignore`d/`.env` overwrite — credentials overwrite

## `.sql`/`mysqldump` restore — SQLi via file import

An `.sql` file gets fed to `mysql`/`psql` — any SQL in it executes:

- `INSERT INTO users VALUES (...)` — data injection
- `SELECT ... INTO OUTFILE` — file write
- `CREATE TRIGGER` — exec via trigger
- `LOAD DATA INFILE` — file read
- `xp_cmdshell` in T-SQL — direct exec on MSSQL

The "import backup" is a stored SQLi — every statement runs.

## `.conf`/`.ini`/`yaml`/`env` restore — the config-as-code shapes

- `.env` → credentials/flag paths overridden
- `config.php`/`settings.py` → code exec if the config is `eval`'d
- `nginx.conf`/`httpd.conf` → `Include`/`SetHandler` → exec
- `crontab` restore → scheduled exec
- `supervisord`/`systemd` config → exec as whatever the daemon runs as

## `.sqlite`/`.db` import — database file restore

A sqlite/db file replaces or merges into the app DB — path traversal into
the DB location, or the file's contents become queryable data —
`file-overwrite.md` for the write side.

## The "the restore happens as root/admin" privilege gap

Restore/import typically runs as the app's service account — a malicious
backup gets applied with those privileges — the "restore" is a
priv-esc-by-design.

## Detection — which restore endpoints exist

- `/admin/backup`, `/import`, `/restore`, `/upload-backup`
- the exported file's format tells you what the importer expects — grab
  the real backup first, modify, re-upload
- filename `*.bak`/`.sql`/`.dump`/`.tar.gz` accepted = restore shape

## The chain — export→modify→import

1. export the real backup (`export`/`download backup`)
2. modify inside — traversal paths, exec payloads, config edits
3. re-upload through `import`/`restore`
4. the app applies it

`python3 tools/web/archive_gen.py zipslip --out x.zip --name 'x' --content 'MARKER' --depth 8`
builds the traversal form for step 2.

## Falsifiers

- no restore/import endpoint exists
- restore validates structure strictly (rejects non-whitelist entries,
  normalizes all paths, rejects traversal)

## Output to record

- the import format + what it does with path/content fields + its
  execution context
