# Editor swap and temp files

Vim .swp, Emacs #file#, nano .save, Windows ~$: the editor's crash-recovery copy of a source file, served as text.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.index.php.swp or .file.swp 200 | vim swap | recover source via vim -r or strings |
| /file.save or file.bak | editor backup | read source |
| /~file or #file# | emacs/nano backup | read source |
| partial reads / range answers | server serves byte ranges | range-recover larger files |

## Steps

1. Probe .<file>.swp, <file>~, <file>.bak, <file>.old, <file>.save for each known filename.
2. swp files are vim binary — strings or vim -r recovers the edited text.
3. A .swp may be an OLDER version than the live file — diff against the served code.
4. Temp files for CONFIG files (.env.swp) are the highest-value targets.

## Falsifier

Falsifier — no swap/temp file for any known filename: no editor leftovers.

## Traps

- The swap file's name pattern is .<name>.swp in the same directory.
- Multiple .swo/.swn files exist for crashed multi-session edits.
- A stale .swp may hold a flag-bearing version since overwritten.

## Commands

```bash
for p in /.index.php.swp /index.php~ /index.php.bak /index.php.old; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`static-leftovers.md` · `source-disclosure.md`
